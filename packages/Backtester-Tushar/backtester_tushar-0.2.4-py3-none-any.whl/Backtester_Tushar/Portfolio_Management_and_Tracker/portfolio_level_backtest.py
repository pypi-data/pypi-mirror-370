import pandas as pd
import numpy as np
from numba import njit, prange
from scipy import stats, optimize, linalg
from scipy.stats import norm
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
import warnings
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import logging

warnings.filterwarnings('ignore')


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    max_position_size: float = 0.05  # 5% max per position
    max_sector_exposure: float = 0.20  # 20% max per sector
    max_beta_exposure: float = 0.15  # Net beta limit
    max_daily_var: float = 0.02  # 2% daily VaR
    max_drawdown: float = 0.10  # 10% max drawdown
    max_leverage: float = 1.0  # Net leverage limit


@njit
def fast_softmax(x):
    """Numerically stable softmax with numba acceleration"""
    x_shifted = x - np.max(x)
    exp_x = np.exp(x_shifted)
    return exp_x / np.sum(exp_x)


@njit
def fast_sharpe_ratio(returns, risk_free_rate=0.0):
    """Fast Sharpe ratio calculation"""
    excess_returns = returns - risk_free_rate
    if np.std(excess_returns) == 0:
        return 0.0
    return np.mean(excess_returns) / np.std(excess_returns)


@njit
def exponential_decay(values, half_life):
    """Apply exponential decay to signal values"""
    decay_factor = np.log(0.5) / half_life
    n = len(values)
    weights = np.exp(decay_factor * np.arange(n - 1, -1, -1))
    return values * weights


class SignalProcessor:
    """Advanced signal processing with decay, orthogonalization, and quality metrics"""

    def __init__(self, half_life_days=5, min_ic_threshold=0.02):
        self.half_life_days = half_life_days
        self.min_ic_threshold = min_ic_threshold
        self.signal_history = defaultdict(deque)
        self.ic_history = defaultdict(deque)

    def decay_signals(self, signals_df):
        """Apply exponential decay to signals based on age"""
        decayed_signals = signals_df.copy()

        for ticker in signals_df['ticker'].unique():
            ticker_data = signals_df[signals_df['ticker'] == ticker].sort_values('date')
            if len(ticker_data) > 1:
                signal_values = ticker_data['signal_descriptor'].values
                decayed_values = exponential_decay(signal_values, self.half_life_days)
                decayed_signals.loc[decayed_signals['ticker'] == ticker, 'signal_descriptor'] = decayed_values

        return decayed_signals

    def calculate_information_coefficient(self, signals, forward_returns, periods=20):
        """Calculate rolling information coefficient"""
        if len(signals) != len(forward_returns) or len(signals) < periods:
            return 0.0

        ic_values = []
        for i in range(periods, len(signals)):
            window_signals = signals[i - periods:i]
            window_returns = forward_returns[i - periods:i]

            if len(window_signals) > 5:  # Minimum sample size
                ic, _ = stats.spearmanr(window_signals, window_returns)
                if not np.isnan(ic):
                    ic_values.append(ic)

        return np.mean(ic_values) if ic_values else 0.0

    def orthogonalize_signals(self, signal_matrix):
        """Orthogonalize signals using Gram-Schmidt process"""
        if signal_matrix.shape[1] < 2:
            return signal_matrix

        # Handle NaN values
        signal_matrix = np.nan_to_num(signal_matrix, nan=0.0)

        # Apply Gram-Schmidt orthogonalization
        orthogonal_signals = np.zeros_like(signal_matrix)

        for i in range(signal_matrix.shape[1]):
            vector = signal_matrix[:, i].copy()

            for j in range(i):
                projection = np.dot(vector, orthogonal_signals[:, j]) / np.dot(orthogonal_signals[:, j],
                                                                               orthogonal_signals[:, j])
                if not np.isnan(projection):
                    vector -= projection * orthogonal_signals[:, j]

            norm = np.linalg.norm(vector)
            orthogonal_signals[:, i] = vector / norm if norm > 1e-10 else vector

        return orthogonal_signals


class MarketImpactModel:
    """Almgren-Chriss execution model with market impact"""

    def __init__(self, permanent_impact=0.1, temporary_impact=0.01, volatility_adjustment=True):
        self.permanent_impact = permanent_impact
        self.temporary_impact = temporary_impact
        self.volatility_adjustment = volatility_adjustment

    def calculate_market_impact(self, shares, avg_volume, volatility, participation_rate=0.1):
        """Calculate market impact cost using Almgren-Chriss model"""
        if avg_volume <= 0 or shares == 0:
            return 0.0

        # Market impact parameters
        volume_ratio = abs(shares) / avg_volume

        # Permanent impact (linear in volume)
        permanent_cost = self.permanent_impact * volume_ratio

        # Temporary impact (square-root law)
        temporary_cost = self.temporary_impact * np.sqrt(volume_ratio)

        # Volatility adjustment
        if self.volatility_adjustment and volatility > 0:
            vol_multiplier = volatility / 0.02  # Normalize to 2% daily vol
            permanent_cost *= vol_multiplier
            temporary_cost *= vol_multiplier

        total_impact = permanent_cost + temporary_cost
        return min(total_impact, 0.05)  # Cap at 5%

    def optimal_execution_schedule(self, total_shares, time_horizon_days, risk_aversion=1e-6):
        """Calculate optimal execution schedule"""
        if time_horizon_days <= 0:
            return [total_shares]

        # Simple arithmetic schedule for now (can be enhanced with more complex optimization)
        shares_per_period = total_shares / time_horizon_days
        return [shares_per_period] * int(time_horizon_days)


class RiskManager:
    """Comprehensive risk management with VaR, factor exposure, and compliance"""

    def __init__(self, risk_limits: RiskLimits, lookback_days=252):
        self.risk_limits = risk_limits
        self.lookback_days = lookback_days
        self.factor_loadings = {}
        self.correlation_matrix = None
        self.var_models = {}

    def calculate_portfolio_var(self, positions, returns_covariance, confidence=0.05):
        """Calculate portfolio Value at Risk using parametric method"""
        if not positions or returns_covariance is None:
            return 0.0

        # Convert positions to numpy array
        tickers = list(positions.keys())
        position_values = np.array([positions[ticker]['market_value'] for ticker in tickers])

        if len(position_values) == 0:
            return 0.0

        # Ensure covariance matrix matches positions
        if returns_covariance.shape[0] != len(position_values):
            return 0.0

        # Portfolio variance
        portfolio_variance = np.dot(position_values.T, np.dot(returns_covariance, position_values))
        portfolio_std = np.sqrt(portfolio_variance)

        # VaR calculation
        z_score = norm.ppf(confidence)
        var = -z_score * portfolio_std

        return var

    def calculate_marginal_var(self, ticker, positions, returns_covariance, confidence=0.05):
        """Calculate marginal VaR contribution of a position"""
        if ticker not in positions or returns_covariance is None:
            return 0.0

        # Calculate VaR with and without the position
        full_var = self.calculate_portfolio_var(positions, returns_covariance, confidence)

        # Remove position and recalculate
        positions_without = {k: v for k, v in positions.items() if k != ticker}
        var_without = self.calculate_portfolio_var(positions_without, returns_covariance, confidence)

        return full_var - var_without

    def check_risk_limits(self, positions, portfolio_value, beta_exposure=0.0):
        """Check all risk limits and return violations"""
        violations = []

        if not positions:
            return violations

        # Position size limits
        for ticker, pos in positions.items():
            position_pct = abs(pos['market_value']) / portfolio_value
            if position_pct > self.risk_limits.max_position_size:
                violations.append(f"Position size limit violated for {ticker}: {position_pct:.2%}")

        # Beta exposure limit
        if abs(beta_exposure) > self.risk_limits.max_beta_exposure:
            violations.append(f"Beta exposure limit violated: {beta_exposure:.3f}")

        # Leverage limit
        gross_exposure = sum(abs(pos['market_value']) for pos in positions.values())
        leverage = gross_exposure / portfolio_value
        if leverage > self.risk_limits.max_leverage:
            violations.append(f"Leverage limit violated: {leverage:.2f}")

        return violations

    def calculate_risk_adjusted_weights(self, expected_returns, covariance_matrix, risk_aversion=1.0):
        """Calculate optimal portfolio weights using mean-variance optimization"""
        if len(expected_returns) == 0 or covariance_matrix is None:
            return {}

        try:
            # Regularize covariance matrix
            regularization = 1e-8 * np.eye(covariance_matrix.shape[0])
            reg_cov_matrix = covariance_matrix + regularization

            # Solve for optimal weights: w = (1/lambda) * inv(Sigma) * mu
            inv_cov = linalg.inv(reg_cov_matrix)
            optimal_weights = np.dot(inv_cov, expected_returns) / risk_aversion

            # Normalize weights
            total_weight = np.sum(np.abs(optimal_weights))
            if total_weight > 0:
                optimal_weights = optimal_weights / total_weight

            return optimal_weights

        except (linalg.LinAlgError, np.linalg.LinAlgError):
            # Fall back to equal weights if optimization fails
            n_assets = len(expected_returns)
            return np.ones(n_assets) / n_assets


class PerformanceAnalyzer:
    """Advanced performance analytics with attribution and benchmarking"""

    def __init__(self, benchmark_returns=None):
        self.benchmark_returns = benchmark_returns
        self.performance_history = []
        self.attribution_history = []

    def calculate_performance_metrics(self, returns, benchmark_returns=None):
        """Calculate comprehensive performance metrics"""
        if len(returns) == 0:
            return {}

        returns_array = np.array(returns)
        returns_array = returns_array[~np.isnan(returns_array)]

        if len(returns_array) == 0:
            return {}

        # Basic metrics
        total_return = np.prod(1 + returns_array) - 1
        annualized_return = (1 + np.mean(returns_array)) ** 252 - 1
        annualized_vol = np.std(returns_array) * np.sqrt(252)
        sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0

        # Risk metrics
        downside_returns = returns_array[returns_array < 0]
        downside_vol = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = annualized_return / downside_vol if downside_vol > 0 else 0

        # Drawdown metrics
        cumulative_returns = np.cumprod(1 + returns_array)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        # Skewness and Kurtosis
        skewness = stats.skew(returns_array)
        kurtosis = stats.kurtosis(returns_array)

        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'var_95': np.percentile(returns_array, 5),
            'cvar_95': np.mean(returns_array[returns_array <= np.percentile(returns_array, 5)])
        }

        # Benchmark-relative metrics
        if benchmark_returns is not None and len(benchmark_returns) == len(returns_array):
            excess_returns = returns_array - np.array(benchmark_returns)
            tracking_error = np.std(excess_returns) * np.sqrt(252)
            information_ratio = np.mean(excess_returns) * 252 / tracking_error if tracking_error > 0 else 0

            # Beta calculation
            covariance = np.cov(returns_array, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0

            # Alpha calculation
            risk_free_rate = 0.02 / 252  # Assume 2% annual risk-free rate
            alpha = (annualized_return - risk_free_rate) - beta * (np.mean(benchmark_returns) * 252 - risk_free_rate)

            metrics.update({
                'tracking_error': tracking_error,
                'information_ratio': information_ratio,
                'beta': beta,
                'alpha': alpha
            })

        return metrics


class InstitutionalPortfolio:
    """Institutional-grade portfolio management system"""

    def __init__(self,
                 initial_capital=10000000,
                 n_long_positions=20,
                 k_short_positions=20,
                 long_capital_pct=0.6,
                 short_capital_pct=0.4,
                 rebalance_frequency=1,
                 risk_limits=None,
                 transaction_cost_bps=5.0):

        # Core parameters
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.n_long_positions = n_long_positions
        self.k_short_positions = k_short_positions
        self.long_capital_pct = long_capital_pct
        self.short_capital_pct = short_capital_pct
        self.rebalance_frequency = rebalance_frequency

        # Risk management
        self.risk_limits = risk_limits or RiskLimits()
        self.risk_manager = RiskManager(self.risk_limits)

        # Advanced components
        self.signal_processor = SignalProcessor()
        self.market_impact_model = MarketImpactModel()
        self.performance_analyzer = PerformanceAnalyzer()

        # Position and trade tracking
        self.positions = {}
        self.trade_log = []
        self.performance_log = []
        self.risk_log = []

        # Market data and models
        self.returns_covariance = None
        self.factor_loadings = {}
        self.correlation_matrix = None

        # Performance tracking
        self.portfolio_values = []
        self.returns = []
        self.peak_value = initial_capital
        self.current_drawdown = 0.0

        # Trading infrastructure
        self.transaction_cost_bps = transaction_cost_bps / 10000
        self.trade_id = 1
        self.last_rebalance_date = None

        # Compliance and logging
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('portfolio_management.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PortfolioManager')

    def estimate_covariance_matrix(self, returns_data, method='ledoit_wolf'):
        """Estimate returns covariance matrix using advanced methods"""
        if returns_data is None or len(returns_data) < 20:
            return None

        returns_matrix = returns_data.values if hasattr(returns_data, 'values') else returns_data

        # Remove any rows/columns with all NaN values
        valid_data = returns_matrix[~np.isnan(returns_matrix).all(axis=1)]
        if len(valid_data) < 10:
            return None

        try:
            if method == 'ledoit_wolf':
                lw = LedoitWolf()
                cov_matrix, _ = lw.fit(valid_data).covariance_, lw.shrinkage_
            elif method == 'sample':
                cov_matrix = np.cov(valid_data.T)
            else:
                # Exponentially weighted covariance
                weights = np.exp(-0.01 * np.arange(len(valid_data))[::-1])
                weights = weights / np.sum(weights)
                weighted_data = valid_data * weights[:, np.newaxis]
                cov_matrix = np.cov(weighted_data.T)

            return cov_matrix

        except Exception as e:
            self.logger.warning(f"Covariance estimation failed: {e}")
            return None

    def select_optimal_portfolio(self, signals_df, returns_data=None):
        """Select optimal portfolio using advanced signal processing and optimization"""
        if len(signals_df) == 0:
            return {}, {}

        # Apply signal decay
        decayed_signals = self.signal_processor.decay_signals(signals_df)

        # Separate long and short signals
        long_signals = decayed_signals[decayed_signals['signal'] == 1].copy()
        short_signals = decayed_signals[decayed_signals['signal'] == -1].copy()

        # Apply advanced selection logic
        long_portfolio = self._select_long_portfolio(long_signals, returns_data)
        short_portfolio = self._select_short_portfolio(short_signals, returns_data)

        return long_portfolio, short_portfolio

    def _select_long_portfolio(self, long_signals, returns_data):
        """Select optimal long portfolio using risk-adjusted optimization"""
        if len(long_signals) == 0:
            return {}

        # Sort by signal strength and select top candidates
        long_signals_sorted = long_signals.nlargest(min(self.n_long_positions * 2, len(long_signals)),
                                                    'signal_descriptor')

        if len(long_signals_sorted) == 0:
            return {}

        # Calculate risk-adjusted scores
        scores = []
        tickers = []

        for _, row in long_signals_sorted.iterrows():
            # Base score: signal strength adjusted for volatility
            base_score = row['signal_descriptor'] / max(row['ATR'], 0.001)

            # Apply market impact adjustment
            market_impact = self.market_impact_model.calculate_market_impact(
                1000,  # Standardized share count
                row.get('Volume', 1000000),
                row['ATR']
            )

            # Risk-adjusted score
            adjusted_score = base_score * (1 - market_impact)
            scores.append(adjusted_score)
            tickers.append(row['ticker'])

        # Use mean-variance optimization if we have returns data
        if returns_data is not None and len(scores) > 1:
            try:
                # Estimate expected returns from signal scores
                expected_returns = np.array(scores)
                expected_returns = expected_returns / np.sum(np.abs(expected_returns))

                # Get covariance matrix subset
                ticker_indices = [i for i, ticker in enumerate(tickers)]
                if self.returns_covariance is not None and len(ticker_indices) <= self.returns_covariance.shape[0]:
                    subset_cov = self.returns_covariance[np.ix_(ticker_indices, ticker_indices)]
                    optimal_weights = self.risk_manager.calculate_risk_adjusted_weights(expected_returns, subset_cov)

                    # Convert to portfolio dictionary
                    portfolio = {}
                    for i, ticker in enumerate(tickers[:len(optimal_weights)]):
                        if abs(optimal_weights[i]) > 0.01:  # Minimum weight threshold
                            portfolio[ticker] = optimal_weights[i]

                    return portfolio
            except Exception as e:
                self.logger.warning(f"Optimization failed, falling back to softmax: {e}")

        # Fallback to softmax allocation
        if len(scores) > 0:
            weights = fast_softmax(np.array(scores))
            return dict(zip(tickers[:self.n_long_positions], weights[:self.n_long_positions]))

        return {}

    def _select_short_portfolio(self, short_signals, returns_data):
        """Select optimal short portfolio using risk-adjusted optimization"""
        if len(short_signals) == 0:
            return {}

        # Sort by signal strength (most negative) and select bottom candidates
        short_signals_sorted = short_signals.nsmallest(min(self.k_short_positions * 2, len(short_signals)),
                                                       'signal_descriptor')

        if len(short_signals_sorted) == 0:
            return {}

        # Calculate risk-adjusted scores (use absolute values for shorts)
        scores = []
        tickers = []

        for _, row in short_signals_sorted.iterrows():
            base_score = abs(row['signal_descriptor']) / max(row['ATR'], 0.001)

            # Apply market impact and borrowing cost adjustments for shorts
            market_impact = self.market_impact_model.calculate_market_impact(
                1000,
                row.get('Volume', 1000000),
                row['ATR']
            )

            # Additional borrowing cost for shorts
            borrowing_cost = 0.02 / 252  # 2% annual borrowing cost
            adjusted_score = base_score * (1 - market_impact - borrowing_cost)

            scores.append(adjusted_score)
            tickers.append(row['ticker'])

        # Apply similar optimization logic as longs
        if returns_data is not None and len(scores) > 1:
            try:
                expected_returns = np.array(scores)
                expected_returns = expected_returns / np.sum(np.abs(expected_returns))

                ticker_indices = [i for i, ticker in enumerate(tickers)]
                if self.returns_covariance is not None and len(ticker_indices) <= self.returns_covariance.shape[0]:
                    subset_cov = self.returns_covariance[np.ix_(ticker_indices, ticker_indices)]
                    optimal_weights = self.risk_manager.calculate_risk_adjusted_weights(expected_returns, subset_cov)

                    portfolio = {}
                    for i, ticker in enumerate(tickers[:len(optimal_weights)]):
                        if abs(optimal_weights[i]) > 0.01:
                            portfolio[ticker] = optimal_weights[i]

                    return portfolio
            except Exception as e:
                self.logger.warning(f"Short optimization failed, falling back to softmax: {e}")

        # Fallback to softmax allocation
        if len(scores) > 0:
            weights = fast_softmax(np.array(scores))
            return dict(zip(tickers[:self.k_short_positions], weights[:self.k_short_positions]))

        return {}

    def execute_smart_rebalancing(self, target_long_portfolio, target_short_portfolio, current_date, market_data,
                                  next_day_data=None):
        """Execute sophisticated rebalancing with transaction cost optimization"""

        # If no next day data provided, use current day close as fallback (less realistic)
        execution_data = next_day_data if next_day_data is not None else market_data

        # Calculate target positions in shares using next day's open prices
        target_positions = {}

        # Long positions
        long_capital = self.current_capital * self.long_capital_pct
        for ticker, weight in target_long_portfolio.items():
            ticker_data = execution_data[execution_data['ticker'] == ticker]
            if len(ticker_data) > 0:
                # Use next day's open price for execution
                execution_price = ticker_data.iloc[0]['Open'] if 'Open' in ticker_data.columns else ticker_data.iloc[0][
                    'Close']
                target_capital = long_capital * weight
                target_shares = target_capital / execution_price
                target_positions[ticker] = {
                    'shares': target_shares,
                    'direction': 1,
                    'price': execution_price,
                    'market_value': target_shares * execution_price
                }

        # Short positions
        short_capital = self.current_capital * self.short_capital_pct
        for ticker, weight in target_short_portfolio.items():
            ticker_data = execution_data[execution_data['ticker'] == ticker]
            if len(ticker_data) > 0:
                # Use next day's open price for execution
                execution_price = ticker_data.iloc[0]['Open'] if 'Open' in ticker_data.columns else ticker_data.iloc[0][
                    'Close']
                target_capital = short_capital * weight
                target_shares = target_capital / execution_price
                target_positions[ticker] = {
                    'shares': target_shares,
                    'direction': -1,
                    'price': execution_price,
                    'market_value': target_shares * execution_price
                }

        # Execute trades with advanced logic
        trades_executed = []
        total_transaction_costs = 0.0

        # Risk check before trading
        risk_violations = self.risk_manager.check_risk_limits(target_positions, self.current_capital)
        if risk_violations:
            self.logger.warning(f"Risk violations detected: {risk_violations}")
            # Scale down positions if needed
            scale_factor = 0.8  # Conservative scaling
            for ticker in target_positions:
                target_positions[ticker]['shares'] *= scale_factor
                target_positions[ticker]['market_value'] *= scale_factor

        # Execute position changes
        current_tickers = set(self.positions.keys())
        target_tickers = set(target_positions.keys())

        # Close positions no longer in target
        for ticker in current_tickers - target_tickers:
            pos = self.positions[ticker]
            shares_to_trade = -pos['shares']

            # Calculate advanced transaction costs
            volume = market_data[market_data['ticker'] == ticker]['Volume'].iloc[0] if len(
                market_data[market_data['ticker'] == ticker]) > 0 else 1000000
            market_impact = self.market_impact_model.calculate_market_impact(
                shares_to_trade, volume, pos.get('volatility', 0.02)
            )

            transaction_cost = abs(shares_to_trade * pos['avg_price']) * (self.transaction_cost_bps + market_impact)
            total_transaction_costs += transaction_cost

            # Log trade
            trade = {
                'trade_id': self.trade_id,
                'date': current_date,
                'ticker': ticker,
                'action': 'CLOSE',
                'shares': shares_to_trade,
                'price': pos['avg_price'],
                'direction': pos['direction'],
                'transaction_cost': transaction_cost,
                'market_impact': market_impact,
                'position_type': 'FULL_CLOSE'
            }
            trades_executed.append(trade)
            self.trade_id += 1

            # Remove position
            del self.positions[ticker]

        # Open or adjust positions
        for ticker, target in target_positions.items():
            current_shares = self.positions.get(ticker, {}).get('shares', 0.0)
            shares_delta = target['shares'] - current_shares

            if abs(shares_delta) > 1:  # Minimum trade threshold
                # Calculate transaction costs
                volume = market_data[market_data['ticker'] == ticker]['Volume'].iloc[0] if len(
                    market_data[market_data['ticker'] == ticker]) > 0 else 1000000
                volatility = market_data[market_data['ticker'] == ticker]['ATR'].iloc[0] if len(
                    market_data[market_data['ticker'] == ticker]) > 0 else 0.02

                market_impact = self.market_impact_model.calculate_market_impact(shares_delta, volume, volatility)
                transaction_cost = abs(shares_delta * target['price']) * (self.transaction_cost_bps + market_impact)
                total_transaction_costs += transaction_cost

                # Determine action
                action = 'OPEN' if ticker not in current_tickers else 'ADJUST'
                position_type = 'NEW_POSITION' if ticker not in current_tickers else 'INCREMENTAL'

                # Log trade with execution details
                trade = {
                    'trade_id': self.trade_id,
                    'signal_date': current_date,  # Date when signal was generated
                    'execution_date': pd.to_datetime(current_date) + pd.Timedelta(
                        days=1) if next_day_data is not None else current_date,  # Actual execution date
                    'ticker': ticker,
                    'action': action,
                    'shares': shares_delta,
                    'execution_price': target['price'],  # Next day's open price
                    'signal_price': market_data[market_data['ticker'] == ticker].iloc[0]['Close'] if len(
                        market_data[market_data['ticker'] == ticker]) > 0 else target['price'],  # Previous day's close
                    'direction': target['direction'],
                    'transaction_cost': transaction_cost,
                    'market_impact': market_impact,
                    'position_type': position_type,
                    'slippage': target['price'] - (market_data[market_data['ticker'] == ticker].iloc[0]['Close'] if len(
                        market_data[market_data['ticker'] == ticker]) > 0 else target['price'])
                    # Gap between signal and execution
                }
                trades_executed.append(trade)
                self.trade_id += 1

                # Update position
                if ticker in self.positions:
                    # Weighted average cost
                    old_pos = self.positions[ticker]
                    old_value = old_pos['shares'] * old_pos['avg_price']
                    new_value = shares_delta * target['price']
                    total_value = old_value + new_value
                    new_total_shares = old_pos['shares'] + shares_delta

                    if abs(new_total_shares) > 1e-6:
                        new_avg_price = total_value / new_total_shares
                        self.positions[ticker] = {
                            'shares': new_total_shares,
                            'avg_price': new_avg_price,
                            'direction': target['direction'],
                            'entry_date': old_pos['entry_date'],
                            'market_value': new_total_shares * target['price'],
                            'volatility': volatility
                        }
                else:
                    # New position
                    self.positions[ticker] = {
                        'shares': target['shares'],
                        'avg_price': target['price'],
                        'direction': target['direction'],
                        'entry_date': current_date,
                        'market_value': target['shares'] * target['price'],
                        'volatility': volatility
                    }

        # Update capital
        self.current_capital -= total_transaction_costs

        # Add trades to log
        self.trade_log.extend(trades_executed)

        return total_transaction_costs, len(trades_executed)

    def calculate_comprehensive_portfolio_metrics(self, market_data, current_date):
        """Calculate advanced portfolio metrics including risk attribution"""

        # Basic portfolio value calculation
        cash = self.current_capital
        total_market_value = 0.0
        total_unrealized_pnl = 0.0
        position_details = {}

        # Calculate individual position metrics
        for ticker, pos in self.positions.items():
            ticker_data = market_data[market_data['ticker'] == ticker]
            if len(ticker_data) > 0:
                current_price = ticker_data.iloc[0]['Close']
                market_value = pos['shares'] * current_price
                cost_basis = pos['shares'] * pos['avg_price']

                if pos['direction'] == 1:  # Long position
                    unrealized_pnl = market_value - cost_basis
                else:  # Short position
                    unrealized_pnl = cost_basis - market_value

                total_market_value += market_value
                total_unrealized_pnl += unrealized_pnl

                # Position-level metrics
                position_details[ticker] = {
                    'shares': pos['shares'],
                    'avg_price': pos['avg_price'],
                    'current_price': current_price,
                    'market_value': market_value,
                    'cost_basis': cost_basis,
                    'unrealized_pnl': unrealized_pnl,
                    'weight': market_value / (cash + total_market_value) if (cash + total_market_value) > 0 else 0,
                    'direction': pos['direction'],
                    'days_held': (pd.to_datetime(current_date) - pd.to_datetime(pos['entry_date'])).days
                }

        portfolio_value = cash + total_market_value

        # Calculate returns
        if len(self.portfolio_values) > 0:
            daily_return = (portfolio_value - self.portfolio_values[-1]) / self.portfolio_values[-1]
        else:
            daily_return = 0.0

        self.returns.append(daily_return)

        # Update drawdown tracking
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value

        current_drawdown = (self.peak_value - portfolio_value) / self.peak_value
        self.current_drawdown = current_drawdown

        # Calculate portfolio-level risk metrics
        portfolio_beta = self._calculate_portfolio_beta(position_details, market_data)
        portfolio_var = self.risk_manager.calculate_portfolio_var(
            {ticker: {'market_value': pos['market_value']} for ticker, pos in position_details.items()},
            self.returns_covariance
        )

        # Sector/factor exposures (simplified)
        sector_exposures = self._calculate_sector_exposures(position_details, market_data)

        # Performance metrics
        if len(self.returns) > 20:
            performance_metrics = self.performance_analyzer.calculate_performance_metrics(self.returns[-252:])
        else:
            performance_metrics = {}

        # Compile comprehensive metrics
        comprehensive_metrics = {
            'date': current_date,
            'portfolio_value': portfolio_value,
            'cash': cash,
            'total_market_value': total_market_value,
            'total_unrealized_pnl': total_unrealized_pnl,
            'daily_return': daily_return,
            'current_drawdown': current_drawdown,
            'max_drawdown': max(getattr(self, 'max_drawdown_experienced', 0), current_drawdown),
            'num_positions': len(self.positions),
            'gross_exposure': sum(abs(pos['market_value']) for pos in position_details.values()),
            'net_exposure': sum(pos['market_value'] * pos['direction'] for pos in position_details.values()),
            'leverage': sum(abs(pos['market_value']) for pos in
                            position_details.values()) / portfolio_value if portfolio_value > 0 else 0,
            'portfolio_beta': portfolio_beta,
            'portfolio_var_95': portfolio_var,
            'sector_exposures': sector_exposures,
            'position_details': position_details
        }

        # Add performance metrics
        comprehensive_metrics.update(performance_metrics)

        # Store for history
        self.portfolio_values.append(portfolio_value)
        self.performance_log.append(comprehensive_metrics)

        return comprehensive_metrics

    def _calculate_portfolio_beta(self, position_details, market_data):
        """Calculate portfolio beta relative to market"""
        total_beta_exposure = 0.0
        total_weight = 0.0

        for ticker, pos in position_details.items():
            # Simplified beta calculation - in practice, use regression against market index
            ticker_data = market_data[market_data['ticker'] == ticker]
            if len(ticker_data) > 0:
                # Proxy beta using ATR relative to average ATR (simplified)
                ticker_atr = ticker_data.iloc[0].get('ATR', 0.02)
                avg_atr = market_data['ATR'].mean() if 'ATR' in market_data.columns else 0.02
                estimated_beta = ticker_atr / avg_atr if avg_atr > 0 else 1.0

                weight = abs(pos['weight'])
                total_beta_exposure += estimated_beta * weight * pos['direction']
                total_weight += weight

        return total_beta_exposure / total_weight if total_weight > 0 else 0.0

    def _calculate_sector_exposures(self, position_details, market_data):
        """Calculate sector exposures (simplified implementation)"""
        # In practice, this would use external sector classification data
        sector_exposures = defaultdict(float)

        for ticker, pos in position_details.items():
            # Simplified sector classification based on ticker patterns
            if ticker.startswith(('AAPL', 'MSFT', 'GOOGL', 'META')):
                sector = 'Technology'
            elif ticker.startswith(('JPM', 'BAC', 'WFC', 'GS')):
                sector = 'Financials'
            elif ticker.startswith(('XOM', 'CVX', 'COP')):
                sector = 'Energy'
            else:
                sector = 'Other'

            sector_exposures[sector] += pos['weight']

        return dict(sector_exposures)

    def run_institutional_backtest(self, master_df):
        """Run comprehensive institutional-grade backtest with next-day execution"""

        self.logger.info("Starting Institutional Portfolio Backtest with Next-Day Execution...")

        # Data preprocessing and validation
        master_df = self._preprocess_data(master_df)

        # Estimate covariance matrix from historical data
        self._initialize_risk_models(master_df)

        unique_dates = sorted(master_df['date'].unique())
        results = []

        for i, current_date in enumerate(unique_dates):
            try:
                # Get current day data for signal generation
                df_day = master_df[master_df['date'] == current_date].copy()

                # Get next day data for trade execution (if available)
                next_day_data = None
                if i < len(unique_dates) - 1:
                    next_date = unique_dates[i + 1]
                    next_day_data = master_df[master_df['date'] == next_date].copy()

                # Detect conflicts
                df_day = self._detect_and_handle_conflicts(df_day)

                # Check rebalancing conditions
                should_rebalance = self._should_rebalance(current_date)

                transaction_costs = 0.0
                trades_count = 0

                if should_rebalance and len(df_day) > 0 and next_day_data is not None:
                    # Get historical returns for covariance estimation
                    returns_window = self._get_returns_window(master_df, current_date, lookback=60)

                    # Select optimal portfolios based on current day signals
                    long_portfolio, short_portfolio = self.select_optimal_portfolio(df_day, returns_window)

                    # Execute rebalancing using next day's open prices
                    if len(long_portfolio) > 0 or len(short_portfolio) > 0:
                        transaction_costs, trades_count = self.execute_smart_rebalancing(
                            long_portfolio, short_portfolio, current_date, df_day, next_day_data
                        )

                        self.last_rebalance_date = current_date
                        self.logger.info(
                            f"Rebalanced on {current_date}: {len(long_portfolio)} longs, {len(short_portfolio)} shorts, {trades_count} trades")

                # Calculate comprehensive metrics using current day's data for portfolio valuation
                # Note: This creates a slight timing mismatch but is necessary for daily tracking
                daily_metrics = self.calculate_comprehensive_portfolio_metrics(df_day, current_date)

                # Add trading metrics
                daily_metrics.update({
                    'rebalanced': should_rebalance,
                    'transaction_costs': transaction_costs,
                    'trades_executed': trades_count,
                    'next_day_execution': next_day_data is not None
                })

                results.append(daily_metrics)

                # Risk monitoring and alerts
                self._monitor_risk_limits(daily_metrics)

                # Progress reporting
                if i % 50 == 0 or i == len(unique_dates) - 1:
                    progress = (i + 1) / len(unique_dates) * 100
                    self.logger.info(
                        f"Progress: {progress:.1f}% - Date: {current_date} - Portfolio Value: ${daily_metrics['portfolio_value']:,.2f}")

            except Exception as e:
                self.logger.error(f"Error processing date {current_date}: {str(e)}")
                continue

        self.logger.info("Backtest Complete!")

        # Generate comprehensive results
        results_df = pd.DataFrame(results)
        final_analytics = self._generate_final_analytics(results_df)
        risk_report = self._generate_risk_report(results_df)

        return {
            'daily_results': results_df,
            'final_analytics': final_analytics,
            'risk_report': risk_report,
            'trade_log': pd.DataFrame(self.trade_log),
            'position_history': self._generate_position_history()
        }

    def _preprocess_data(self, master_df):
        """Advanced data preprocessing with validation"""

        # Data quality checks
        required_columns = ['date', 'ticker', 'signal', 'signal_descriptor', 'Close', 'ATR', 'Volume']
        missing_columns = [col for col in required_columns if col not in master_df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Remove rows with critical missing data
        master_df = master_df.dropna(subset=['Close', 'ATR', 'signal_descriptor'])

        # Handle outliers in ATR (cap at 99th percentile)
        atr_99th = master_df['ATR'].quantile(0.99)
        master_df['ATR'] = master_df['ATR'].clip(upper=atr_99th)

        # Ensure proper data types
        master_df['date'] = pd.to_datetime(master_df['date'])
        master_df = master_df.sort_values(['date', 'ticker']).reset_index(drop=True)

        # Add derived fields
        master_df['returns'] = master_df.groupby('ticker')['Close'].pct_change()

        self.logger.info(f"Data preprocessing complete. {len(master_df)} records processed.")

        return master_df

    def _initialize_risk_models(self, master_df):
        """Initialize risk models and covariance matrices"""

        # Create returns matrix for covariance estimation
        returns_pivot = master_df.pivot_table(
            index='date',
            columns='ticker',
            values='returns',
            fill_value=0
        )

        if len(returns_pivot) > 60:  # Need sufficient history
            self.returns_covariance = self.estimate_covariance_matrix(returns_pivot.values[-252:])  # Use last year
            self.logger.info("Risk models initialized successfully")
        else:
            self.logger.warning("Insufficient data for risk model initialization")

    def _detect_and_handle_conflicts(self, df_day):
        """Enhanced conflict detection with resolution strategies"""

        # Group by ticker and detect conflicts
        ticker_groups = df_day.groupby('ticker')

        df_day['direction_flag'] = 0

        for ticker, group in ticker_groups:
            signals = group['signal'].dropna()
            if len(signals.unique()) > 1 and 0 not in signals.unique():
                # Mark conflicting entries
                df_day.loc[df_day['ticker'] == ticker, 'direction_flag'] = 42

                # Resolution strategy: keep strongest signal
                strongest_signal_idx = group['signal_descriptor'].abs().idxmax()
                df_day.loc[(df_day['ticker'] == ticker) & (df_day.index != strongest_signal_idx), 'signal'] = 0

        return df_day

    def _should_rebalance(self, current_date):
        """Enhanced rebalancing logic with market conditions"""

        if self.last_rebalance_date is None:
            return True

        days_since_rebalance = (pd.to_datetime(current_date) - pd.to_datetime(self.last_rebalance_date)).days

        # Standard frequency-based rebalancing
        if days_since_rebalance >= self.rebalance_frequency:
            return True

        # Emergency rebalancing conditions
        if self.current_drawdown > self.risk_limits.max_drawdown * 0.8:
            self.logger.warning("Emergency rebalancing triggered due to high drawdown")
            return True

        return False

    def _get_returns_window(self, master_df, current_date, lookback=60):
        """Get historical returns window for analysis"""

        current_date_dt = pd.to_datetime(current_date)
        start_date = current_date_dt - pd.Timedelta(days=lookback)

        window_data = master_df[
            (master_df['date'] >= start_date) &
            (master_df['date'] < current_date)
            ]

        return window_data

    def _monitor_risk_limits(self, daily_metrics):
        """Real-time risk monitoring with alerts"""

        # Check critical risk limits
        alerts = []

        if daily_metrics['current_drawdown'] > self.risk_limits.max_drawdown:
            alerts.append(f"CRITICAL: Drawdown limit breached - {daily_metrics['current_drawdown']:.2%}")

        if daily_metrics.get('leverage', 0) > self.risk_limits.max_leverage:
            alerts.append(f"WARNING: Leverage limit exceeded - {daily_metrics['leverage']:.2f}")

        if daily_metrics.get('portfolio_var_95', 0) > self.risk_limits.max_daily_var:
            alerts.append(f"WARNING: VaR limit exceeded - {daily_metrics['portfolio_var_95']:.2%}")

        # Log alerts
        for alert in alerts:
            self.logger.warning(alert)

        # Store risk metrics
        self.risk_log.append({
            'date': daily_metrics['date'],
            'alerts': alerts,
            'risk_metrics': {
                'drawdown': daily_metrics['current_drawdown'],
                'leverage': daily_metrics.get('leverage', 0),
                'var_95': daily_metrics.get('portfolio_var_95', 0),
                'beta': daily_metrics.get('portfolio_beta', 0)
            }
        })

    def _generate_final_analytics(self, results_df):
        """Generate comprehensive final analytics"""

        if len(results_df) == 0:
            return {}

        # Basic performance metrics
        initial_value = self.initial_capital
        final_value = results_df['portfolio_value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value

        # Risk-adjusted metrics
        returns = results_df['daily_return'].dropna()
        if len(returns) > 0:
            performance_metrics = self.performance_analyzer.calculate_performance_metrics(returns.values)
        else:
            performance_metrics = {}

        # Enhanced trading statistics with slippage analysis
        total_trades = len(self.trade_log)
        total_transaction_costs = sum(trade['transaction_cost'] for trade in self.trade_log)

        # Calculate slippage statistics (difference between signal price and execution price)
        slippage_data = [trade.get('slippage', 0) for trade in self.trade_log if 'slippage' in trade]
        avg_slippage = np.mean(slippage_data) if slippage_data else 0
        slippage_cost = sum(abs(trade.get('slippage', 0)) * abs(trade.get('shares', 0))
                            for trade in self.trade_log if 'slippage' in trade)

        avg_holding_period = np.mean([
            trade.get('days_held', 0) for trade in self.trade_log
            if trade.get('action') == 'CLOSE'
        ]) if self.trade_log else 0

        # Risk statistics
        max_leverage = results_df['leverage'].max() if 'leverage' in results_df.columns else 0
        avg_num_positions = results_df['num_positions'].mean()

        final_analytics = {
            'performance': {
                'initial_capital': initial_value,
                'final_value': final_value,
                'total_return': total_return,
                **performance_metrics
            },
            'risk': {
                'max_drawdown': results_df['current_drawdown'].max(),
                'max_leverage': max_leverage,
                'avg_positions': avg_num_positions,
                'var_breaches': len([r for r in self.risk_log if r['alerts']])
            },
            'trading': {
                'total_trades': total_trades,
                'total_transaction_costs': total_transaction_costs,
                'avg_holding_period': avg_holding_period,
                'turnover_rate': total_transaction_costs / initial_value,
                'avg_slippage': avg_slippage,
                'total_slippage_cost': slippage_cost,
                'next_day_execution_rate': len(
                    [t for t in self.trade_log if t.get('execution_date') != t.get('signal_date')]) / max(total_trades,
                                                                                                          1)
            }
        }

        return final_analytics

    def _generate_risk_report(self, results_df):
        """Generate detailed risk analysis report"""

        risk_report = {
            'drawdown_analysis': self._analyze_drawdowns(results_df),
            'var_analysis': self._analyze_var_performance(results_df),
            'concentration_analysis': self._analyze_concentration_risk(results_df),
            'factor_exposures': self._analyze_factor_exposures(results_df)
        }

        return risk_report

    def _analyze_drawdowns(self, results_df):
        """Analyze drawdown characteristics"""

        if 'current_drawdown' not in results_df.columns:
            return {}

        drawdowns = results_df['current_drawdown'].values

        # Find drawdown periods
        drawdown_periods = []
        in_drawdown = False
        start_idx = 0

        for i, dd in enumerate(drawdowns):
            if dd > 0.01 and not in_drawdown:  # Start of drawdown
                in_drawdown = True
                start_idx = i
            elif dd < 0.005 and in_drawdown:  # End of drawdown
                in_drawdown = False
                drawdown_periods.append({
                    'start': results_df.iloc[start_idx]['date'],
                    'end': results_df.iloc[i]['date'],
                    'duration': i - start_idx,
                    'max_drawdown': drawdowns[start_idx:i + 1].max()
                })

        return {
            'max_drawdown': drawdowns.max(),
            'avg_drawdown': drawdowns.mean(),
            'drawdown_periods': len(drawdown_periods),
            'longest_drawdown': max([dd['duration'] for dd in drawdown_periods]) if drawdown_periods else 0,
            'recovery_times': [dd['duration'] for dd in drawdown_periods]
        }

    def _analyze_var_performance(self, results_df):
        """Analyze VaR model performance"""

        if 'portfolio_var_95' not in results_df.columns or 'daily_return' not in results_df.columns:
            return {}

        var_predictions = results_df['portfolio_var_95'].values
        actual_returns = results_df['daily_return'].values

        # VaR exceptions (where actual loss exceeded VaR prediction)
        exceptions = actual_returns < -var_predictions
        exception_rate = np.mean(exceptions)

        return {
            'var_exceptions': np.sum(exceptions),
            'exception_rate': exception_rate,
            'expected_exception_rate': 0.05,
            'var_accuracy': abs(exception_rate - 0.05) < 0.02  # Within reasonable bounds
        }

    def _analyze_concentration_risk(self, results_df):
        """Analyze portfolio concentration risk"""

        concentration_metrics = []

        for _, row in results_df.iterrows():
            position_details = row.get('position_details', {})
            if position_details:
                weights = [abs(pos['weight']) for pos in position_details.values()]
                if weights:
                    # Herfindahl index
                    hhi = sum(w ** 2 for w in weights)
                    max_weight = max(weights)
                    concentration_metrics.append({
                        'date': row['date'],
                        'hhi': hhi,
                        'max_weight': max_weight,
                        'num_positions': len(weights)
                    })

        if not concentration_metrics:
            return {}

        concentration_df = pd.DataFrame(concentration_metrics)

        return {
            'avg_hhi': concentration_df['hhi'].mean(),
            'max_single_position': concentration_df['max_weight'].max(),
            'avg_num_positions': concentration_df['num_positions'].mean()
        }

    def _analyze_factor_exposures(self, results_df):
        """Analyze factor exposures over time"""

        sector_exposures_over_time = []

        for _, row in results_df.iterrows():
            sector_exposures = row.get('sector_exposures', {})
            if sector_exposures:
                sector_exposures_over_time.append({
                    'date': row['date'],
                    **sector_exposures
                })

        if not sector_exposures_over_time:
            return {}

        exposures_df = pd.DataFrame(sector_exposures_over_time)

        # Calculate average and maximum exposures by sector
        factor_analysis = {}
        for col in exposures_df.columns:
            if col != 'date':
                factor_analysis[col] = {
                    'avg_exposure': exposures_df[col].mean(),
                    'max_exposure': exposures_df[col].max(),
                    'volatility': exposures_df[col].std()
                }

        return factor_analysis

    def _generate_position_history(self):
        """Generate detailed position history for analysis"""

        position_history = {
            'current_positions': self.positions,
            'trade_summary': {
                'total_trades': len(self.trade_log),
                'profitable_trades': len([t for t in self.trade_log if t.get('pnl', 0) > 0]),
                'avg_trade_size': np.mean(
                    [abs(t['shares'] * t['price']) for t in self.trade_log]) if self.trade_log else 0
            }
        }

        return position_history