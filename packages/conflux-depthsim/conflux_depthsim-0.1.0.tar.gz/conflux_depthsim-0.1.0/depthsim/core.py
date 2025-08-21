"""
DepthSim Core Engine

This module contains the main DepthSimulator class that orchestrates
order book depth simulation by consuming market data and generating
realistic bid-ask spreads, order book snapshots, and trade prints.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Callable, Tuple
import numpy as np
import pandas as pd

from .models import OrderBook, OrderBookLevel, Quote, Trade, TradeType, SpreadModel
from .spread_models import (
    BaseSpreadModel, 
    ConstantSpreadModel, 
    VolatilityLinkedSpreadModel,
    VolumeLinkedSpreadModel,
    VolatilityVolumeSpreadModel,
    TimeOfDaySpreadModel,
    CustomSpreadModel,
    get_spread_model
)


class DepthSimulator:
    """
    Main order book depth simulation engine.
    
    Consumes market data (OHLCV) and generates realistic bid-ask spreads,
    order book depth, and trade prints based on configurable models.
    """
    
    def __init__(
        self,
        spread_model: Union[str, BaseSpreadModel] = "volatility",
        base_spread_bps: float = 5.0,
        volatility_window: int = 20,
        depth_levels: int = 10,
        seed: Optional[int] = None,
        **model_kwargs
    ):
        """
        Initialize DepthSimulator.
        
        Args:
            spread_model: Spread model name or instance 
            base_spread_bps: Base spread for models that use it
            volatility_window: Rolling window for volatility calculation
            depth_levels: Default number of order book levels
            seed: Random seed for reproducible results
            **model_kwargs: Additional parameters for spread models
        """
        if seed is not None:
            np.random.seed(seed)
        
        self.volatility_window = volatility_window
        self.depth_levels = depth_levels
        self.seed = seed
        
        # Initialize spread model
        if isinstance(spread_model, str):
            # Handle parameter mapping for different models
            if spread_model == 'constant':
                # ConstantSpreadModel uses 'spread_bps', not 'base_spread_bps'
                if 'spread_bps' not in model_kwargs:
                    model_kwargs['spread_bps'] = base_spread_bps
            else:
                # Most other models use 'base_spread_bps'
                if 'base_spread_bps' not in model_kwargs:
                    model_kwargs['base_spread_bps'] = base_spread_bps
            self.spread_model = get_spread_model(spread_model, **model_kwargs)
        elif isinstance(spread_model, BaseSpreadModel):
            self.spread_model = spread_model
        else:
            raise ValueError("spread_model must be string name or BaseSpreadModel instance")
    
    def calculate_volatility(self, prices: pd.Series) -> pd.Series:
        """
        Calculate rolling volatility from price series.
        
        Args:
            prices: Price series (typically close prices)
            
        Returns:
            Rolling volatility series
        """
        returns = prices.pct_change()
        volatility = returns.rolling(window=self.volatility_window).std()
        
        # Fill initial NaN values with first valid volatility
        first_valid = volatility.first_valid_index()
        if first_valid is not None:
            volatility.iloc[:volatility.index.get_loc(first_valid)] = volatility.iloc[volatility.index.get_loc(first_valid)]
        
        return volatility.fillna(0.02)  # Default 2% if all NaN
    
    def generate_quotes(
        self, 
        market_data: pd.DataFrame,
        price_column: str = 'close',
        volume_column: str = 'volume'
    ) -> pd.DataFrame:
        """
        Generate L1 quotes (bid/ask) from market data.
        
        Args:
            market_data: DataFrame with market data (must have timestamp index)
            price_column: Column name for prices (default 'close')
            volume_column: Column name for volume (default 'volume')
            
        Returns:
            DataFrame with bid, ask, mid, spread_bps, spread_pct columns
        """
        if price_column not in market_data.columns:
            raise ValueError(f"Price column '{price_column}' not found in market data")
        if volume_column not in market_data.columns:
            raise ValueError(f"Volume column '{volume_column}' not found in market data")
        
        prices = market_data[price_column]
        volumes = market_data[volume_column]
        
        # Calculate volatility
        volatility = self.calculate_volatility(prices)
        
        # Generate spreads for each timestamp
        quotes_data = []
        
        for idx, (timestamp, price) in enumerate(prices.items()):
            vol = volatility.iloc[idx]
            volume = volumes.iloc[idx]
            
            # Calculate spread using the model
            kwargs = {'timestamp': timestamp} if hasattr(timestamp, 'hour') else {}
            spread_bps = self.spread_model.calculate_spread(price, vol, volume, **kwargs)
            
            # Convert spread to price units
            spread_price = price * (spread_bps / 10000.0)
            half_spread = spread_price / 2.0
            
            # Calculate bid and ask
            bid = price - half_spread
            ask = price + half_spread
            
            quotes_data.append({
                'timestamp': timestamp,
                'bid': bid,
                'ask': ask,
                'mid': price,
                'spread_bps': spread_bps,
                'spread_pct': spread_bps / 100.0
            })
        
        quotes_df = pd.DataFrame(quotes_data)
        quotes_df.set_index('timestamp', inplace=True)
        
        return quotes_df
    
    def generate_order_book_depth(
        self,
        mid_price: float,
        spread_price: float,
        volume: float,
        levels: Optional[int] = None,
        base_size_ratio: float = 0.1,
        decay_factor: float = 0.75,
        size_randomness: float = 0.3
    ) -> tuple[List[OrderBookLevel], List[OrderBookLevel]]:
        """
        Generate realistic order book depth with power law distribution.
        
        Args:
            mid_price: Mid price for the order book
            spread_price: Full spread in price units
            volume: Current volume for sizing
            levels: Number of levels per side (uses default if None)
            base_size_ratio: Base size as ratio of volume
            decay_factor: Size decay rate (0.5-0.9)
            size_randomness: Random variation in sizes
            
        Returns:
            Tuple of (bids, asks) with OrderBookLevel lists
        """
        levels = levels or self.depth_levels
        half_spread = spread_price / 2.0
        base_size = volume * base_size_ratio
        
        best_bid = mid_price - half_spread
        best_ask = mid_price + half_spread
        
        bids = []
        asks = []
        
        # Generate bid levels (descending price)
        bid_prices = []
        for i in range(levels):
            # Price gets worse (lower) as we go deeper
            price_offset = i * half_spread * (0.3 + np.random.random() * 0.7)
            price = best_bid - price_offset
            bid_prices.append(price)
            
        # Sort bid prices in descending order to ensure proper ordering
        bid_prices.sort(reverse=True)
        
        for i, price in enumerate(bid_prices):
            # Size follows power law decay with randomness
            size_multiplier = (decay_factor ** i) * (1 + np.random.normal(0, size_randomness))
            size = max(base_size * size_multiplier, 1000)
            
            # Number of orders decreases with size but has randomness
            orders = max(int(size / 75000) + np.random.poisson(2), 1)
            
            bids.append(OrderBookLevel(
                price=round(price, 2),
                size=round(size, 0),
                orders=orders
            ))
        
        # Generate ask levels (ascending price)
        ask_prices = []
        for i in range(levels):
            # Price gets worse (higher) as we go deeper
            price_offset = i * half_spread * (0.3 + np.random.random() * 0.7)
            price = best_ask + price_offset
            ask_prices.append(price)
            
        # Sort ask prices in ascending order to ensure proper ordering
        ask_prices.sort()
        
        for i, price in enumerate(ask_prices):
            # Size follows power law decay with randomness  
            size_multiplier = (decay_factor ** i) * (1 + np.random.normal(0, size_randomness))
            size = max(base_size * size_multiplier, 1000)
            
            # Number of orders
            orders = max(int(size / 75000) + np.random.poisson(2), 1)
            
            asks.append(OrderBookLevel(
                price=round(price, 2),
                size=round(size, 0),
                orders=orders
            ))
        
        return bids, asks
    
    def generate_depth_ladder(
        self,
        market_data: pd.DataFrame,
        levels: Optional[int] = None,
        price_column: str = 'close',
        volume_column: str = 'volume'
    ) -> Dict[datetime, OrderBook]:
        """
        Generate order book depth ladder for each timestamp.
        
        Args:
            market_data: DataFrame with market data
            levels: Number of levels per side
            price_column: Price column name
            volume_column: Volume column name
            
        Returns:
            Dictionary mapping timestamps to OrderBook instances
        """
        # First generate quotes to get spread information
        quotes = self.generate_quotes(market_data, price_column, volume_column)
        
        depth_ladder = {}
        
        for timestamp, quote_row in quotes.iterrows():
            volume = market_data.loc[timestamp, volume_column]
            spread_price = quote_row['ask'] - quote_row['bid']
            
            # Generate depth for this timestamp
            bids, asks = self.generate_order_book_depth(
                mid_price=quote_row['mid'],
                spread_price=spread_price,
                volume=volume,
                levels=levels
            )
            
            # Create OrderBook instance
            order_book = OrderBook(
                bids=bids,
                asks=asks,
                mid_price=quote_row['mid'],
                spread=spread_price,
                spread_bps=quote_row['spread_bps'],
                timestamp=timestamp
            )
            
            depth_ladder[timestamp] = order_book
        
        return depth_ladder
    
    def generate_trade_prints(
        self,
        market_data: pd.DataFrame,
        trade_frequency: float = 0.5,
        size_distribution: str = 'pareto',
        price_column: str = 'close',
        volume_column: str = 'volume'
    ) -> List[Trade]:
        """
        Generate realistic trade prints using Poisson arrivals.
        
        Args:
            market_data: Market data DataFrame
            trade_frequency: Average trades per minute
            size_distribution: Size distribution model ('pareto', 'lognormal', 'uniform')
            price_column: Price column name
            volume_column: Volume column name
            
        Returns:
            List of Trade objects
        """
        quotes = self.generate_quotes(market_data, price_column, volume_column)
        trades = []
        
        for timestamp, quote_row in quotes.iterrows():
            volume = market_data.loc[timestamp, volume_column]
            
            # Determine number of trades for this period (Poisson arrivals)
            # Assume periods are 1 minute for now (could be parameterized)
            expected_trades = trade_frequency
            num_trades = np.random.poisson(expected_trades)
            
            for i in range(num_trades):
                # Random time within the period
                trade_time = timestamp  # Simplified - could add sub-minute randomness
                
                # Determine trade side (buy hits ask, sell hits bid)
                is_buy = np.random.random() > 0.5
                trade_price = quote_row['ask'] if is_buy else quote_row['bid']
                
                # Generate trade size based on distribution
                if size_distribution == 'pareto':
                    # Pareto distribution - many small trades, few large ones
                    size = np.random.pareto(1.5) * 1000 + 100
                elif size_distribution == 'lognormal':
                    # Log-normal distribution
                    size = np.random.lognormal(6, 1)  # Mean around 400
                else:  # uniform
                    size = np.random.uniform(100, 10000)
                
                # Cap size at reasonable level
                size = min(size, volume * 0.1)  # Max 10% of period volume
                
                trades.append(Trade(
                    timestamp=trade_time,
                    price=trade_price,
                    size=round(size, 0),
                    side=TradeType.BUY if is_buy else TradeType.SELL,
                    trade_id=f"{timestamp.isoformat()}_{i}"
                ))
        
        return sorted(trades, key=lambda t: t.timestamp)
    
    def apply_latency_effects(
        self,
        quotes: pd.DataFrame,
        latency_ms: Union[float, tuple] = (1.0, 3.0)
    ) -> pd.DataFrame:
        """
        Apply latency effects to quotes (delays, jitter).
        
        Args:
            quotes: Quote DataFrame
            latency_ms: Latency in milliseconds (float or (min, max) tuple)
            
        Returns:
            Quote DataFrame with latency effects applied
        """
        # This is a simplified latency model
        # In reality, latency affects both data arrival and order placement
        
        if isinstance(latency_ms, tuple):
            min_latency, max_latency = latency_ms
        else:
            min_latency = max_latency = latency_ms
        
        # Add random latency to each quote
        quotes_with_latency = quotes.copy()
        
        for i in range(len(quotes_with_latency)):
            # Random latency for this quote
            delay_ms = np.random.uniform(min_latency, max_latency)
            
            # Apply some price staleness (simplified model)
            staleness_factor = delay_ms / 1000.0  # Convert to seconds
            price_impact = np.random.normal(0, staleness_factor * 0.001)  # Small random impact
            
            quotes_with_latency.iloc[i, quotes.columns.get_loc('bid')] *= (1 + price_impact)
            quotes_with_latency.iloc[i, quotes.columns.get_loc('ask')] *= (1 + price_impact)
            quotes_with_latency.iloc[i, quotes.columns.get_loc('mid')] *= (1 + price_impact)
        
        return quotes_with_latency
    
    def generate_l2_depth_snapshots(
        self,
        market_data: pd.DataFrame,
        levels: int = 20,
        asymmetry_factor: float = 0.1,
        size_clustering: bool = True,
        price_improvement: bool = True,
        price_column: str = 'close',
        volume_column: str = 'volume'
    ) -> Dict[pd.Timestamp, 'OrderBook']:
        """
        Generate advanced L2 depth snapshots with realistic market microstructure.
        
        Args:
            market_data: Market data DataFrame
            levels: Number of price levels per side
            asymmetry_factor: How asymmetric bid/ask sides can be (0-1)
            size_clustering: Whether to cluster size at certain price levels
            price_improvement: Whether to simulate sub-penny pricing
            price_column: Column name for price data
            volume_column: Column name for volume data
            
        Returns:
            Dictionary mapping timestamps to OrderBook objects
        """
        quotes = self.generate_quotes(market_data, price_column, volume_column)
        depth_snapshots = {}
        
        for timestamp, quote_row in quotes.iterrows():
            volume = market_data.loc[timestamp, volume_column]
            
            # Generate asymmetric sides
            bid_levels = max(int(levels * (1 - asymmetry_factor * np.random.random())), levels // 2)
            ask_levels = max(int(levels * (1 - asymmetry_factor * np.random.random())), levels // 2)
            
            bids, asks = self._generate_order_book_levels(
                quote_row['mid'], 
                quote_row['spread_bps'] / 10000 * quote_row['mid'],
                volume,
                bid_levels,
                ask_levels,
                size_clustering=size_clustering,
                price_improvement=price_improvement
            )
            
            # Calculate order book metrics
            total_bid_size = sum(level.size for level in bids)
            total_ask_size = sum(level.size for level in asks)
            imbalance = (total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)
            
            order_book = OrderBook(
                bids=bids,
                asks=asks,
                mid_price=quote_row['mid'],
                spread=quote_row['ask'] - quote_row['bid'],
                spread_bps=quote_row['spread_bps'],
                timestamp=timestamp,
                _total_bid_size=total_bid_size,
                _total_ask_size=total_ask_size,
                _imbalance=imbalance
            )
            
            depth_snapshots[timestamp] = order_book
            
        return depth_snapshots
    
    def _generate_order_book_levels(
        self,
        mid_price: float,
        spread_price: float,
        volume: float,
        bid_levels: int,
        ask_levels: int,
        size_clustering: bool = True,
        price_improvement: bool = True,
        decay_factor: float = 0.85,
        base_size_ratio: float = 0.08,
        size_randomness: float = 0.4
    ) -> Tuple[List['OrderBookLevel'], List['OrderBookLevel']]:
        """
        Generate order book levels with advanced microstructure features.
        
        Args:
            mid_price: Current mid price
            spread_price: Current spread in price units
            volume: Current volume for sizing
            bid_levels: Number of bid levels
            ask_levels: Number of ask levels
            size_clustering: Enable size clustering at key levels
            price_improvement: Enable sub-penny price improvement
            decay_factor: Size decay factor by level
            base_size_ratio: Base size as ratio of volume
            size_randomness: Random variation in sizes
            
        Returns:
            Tuple of (bid_levels, ask_levels)
        """
        half_spread = spread_price / 2.0
        base_size = volume * base_size_ratio
        
        best_bid = mid_price - half_spread
        best_ask = mid_price + half_spread
        
        # Generate bid levels with clustering and price improvement
        bid_prices = []
        for i in range(bid_levels):
            if i == 0:
                price = best_bid
            else:
                # Base price decrement
                base_decrement = i * half_spread * (0.2 + np.random.random() * 0.6)
                price = best_bid - base_decrement
                
                # Price improvement (sub-penny pricing)
                if price_improvement and np.random.random() < 0.3:
                    price += np.random.uniform(0.001, 0.009)
            
            bid_prices.append(price)
        
        # Sort and generate bid order book levels
        bid_prices.sort(reverse=True)
        bids = []
        
        for i, price in enumerate(bid_prices):
            # Size calculation with clustering
            size_multiplier = (decay_factor ** i) * (1 + np.random.normal(0, size_randomness))
            
            # Size clustering at key psychological levels
            if size_clustering and (price % 10 < 0.5 or price % 5 < 0.5):
                size_multiplier *= 1.3  # 30% more size at key levels
            
            size = max(base_size * size_multiplier, 500)
            
            # Number of orders (more orders at better prices)
            orders = max(int(size / (50000 + i * 10000)) + np.random.poisson(1), 1)
            
            bids.append(OrderBookLevel(
                price=round(price, 3),  # Allow sub-penny precision
                size=round(size, 0),
                orders=orders
            ))
        
        # Generate ask levels (similar logic)
        ask_prices = []
        for i in range(ask_levels):
            if i == 0:
                price = best_ask
            else:
                base_increment = i * half_spread * (0.2 + np.random.random() * 0.6)
                price = best_ask + base_increment
                
                # Price improvement
                if price_improvement and np.random.random() < 0.3:
                    price -= np.random.uniform(0.001, 0.009)
            
            ask_prices.append(price)
        
        # Sort and generate ask order book levels
        ask_prices.sort()
        asks = []
        
        for i, price in enumerate(ask_prices):
            size_multiplier = (decay_factor ** i) * (1 + np.random.normal(0, size_randomness))
            
            # Size clustering
            if size_clustering and (price % 10 < 0.5 or price % 5 < 0.5):
                size_multiplier *= 1.3
            
            size = max(base_size * size_multiplier, 500)
            orders = max(int(size / (50000 + i * 10000)) + np.random.poisson(1), 1)
            
            asks.append(OrderBookLevel(
                price=round(price, 3),
                size=round(size, 0),
                orders=orders
            ))
        
        return bids, asks
    
    def simulate_market_impact(
        self,
        order_size: float,
        order_side: str,
        order_book: 'OrderBook',
        impact_model: str = 'linear'
    ) -> Dict[str, float]:
        """
        Simulate market impact of a large order on the order book.
        
        Args:
            order_size: Size of the order
            order_side: 'buy' or 'sell'
            order_book: Current order book state
            impact_model: Impact model ('linear', 'square_root', 'power_law')
            
        Returns:
            Dictionary with impact metrics
        """
        if order_side.lower() == 'buy':
            levels = order_book.asks
            reference_price = order_book.best_ask
        else:
            levels = order_book.bids
            reference_price = order_book.best_bid
            
        if not levels or reference_price is None:
            return {'average_price': 0.0, 'impact_bps': 0.0, 'levels_consumed': 0}
        
        remaining_size = order_size
        total_cost = 0.0
        levels_consumed = 0
        
        # Walk through order book levels
        for level in levels:
            if remaining_size <= 0:
                break
                
            consumed_size = min(remaining_size, level.size)
            total_cost += consumed_size * level.price
            remaining_size -= consumed_size
            levels_consumed += 1
            
            if consumed_size == level.size:
                # Fully consumed this level
                continue
            else:
                # Partially consumed
                break
        
        if total_cost == 0:
            return {'average_price': reference_price, 'impact_bps': 0.0, 'levels_consumed': 0}
            
        executed_size = order_size - remaining_size
        average_price = total_cost / executed_size if executed_size > 0 else reference_price
        
        # Calculate impact in basis points
        if order_side.lower() == 'buy':
            impact_bps = (average_price - reference_price) / reference_price * 10000
        else:
            impact_bps = (reference_price - average_price) / reference_price * 10000
            
        return {
            'average_price': average_price,
            'impact_bps': impact_bps,
            'levels_consumed': levels_consumed,
            'executed_size': executed_size,
            'remaining_size': remaining_size
        }
    
    def generate_realistic_trade_sequence(
        self,
        market_data: pd.DataFrame,
        trade_intensity: float = 1.0,
        institutional_ratio: float = 0.15,
        price_column: str = 'close',
        volume_column: str = 'volume'
    ) -> List[Trade]:
        """
        Generate realistic sequence of trades with institutional and retail patterns.
        
        Args:
            market_data: Market data DataFrame
            trade_intensity: Overall trade frequency multiplier
            institutional_ratio: Fraction of trades that are institutional
            price_column: Column name for price data
            volume_column: Column name for volume data
            
        Returns:
            List of Trade objects with realistic patterns
        """
        quotes = self.generate_quotes(market_data, price_column, volume_column)
        trades = []
        
        for timestamp, quote_row in quotes.iterrows():
            volume = market_data.loc[timestamp, volume_column]
            
            # Base trade frequency depends on volume
            base_frequency = max(0.5, min(10.0, np.log(volume / 100000) * trade_intensity))
            actual_trades = np.random.poisson(base_frequency)
            
            for i in range(actual_trades):
                # Determine if this is an institutional trade
                is_institutional = np.random.random() < institutional_ratio
                
                # Trade side probability (slightly favor buying in bull markets)
                price_momentum = (quote_row['mid'] / market_data[price_column].iloc[0] - 1) * 100
                buy_probability = 0.5 + np.tanh(price_momentum / 10) * 0.1
                is_buy = np.random.random() < buy_probability
                
                # Trade price (with some price improvement for institutional)
                if is_buy:
                    base_price = quote_row['ask']
                    if is_institutional and np.random.random() < 0.3:
                        # Institutional trades sometimes get price improvement
                        price_improvement = np.random.uniform(0.0001, 0.001) * base_price
                        trade_price = base_price - price_improvement
                    else:
                        trade_price = base_price
                else:
                    base_price = quote_row['bid']
                    if is_institutional and np.random.random() < 0.3:
                        # Price improvement for sells
                        price_improvement = np.random.uniform(0.0001, 0.001) * base_price
                        trade_price = base_price + price_improvement
                    else:
                        trade_price = base_price
                
                # Trade size distribution
                if is_institutional:
                    # Institutional: larger sizes, log-normal distribution
                    mean_size = volume * 0.05  # 5% of hourly volume
                    size_log_mean = np.log(mean_size) - 0.5
                    trade_size = np.random.lognormal(size_log_mean, 1.2)
                    trade_size = min(trade_size, volume * 0.3)  # Cap at 30% of volume
                else:
                    # Retail: smaller sizes, exponential distribution  
                    mean_retail_size = volume * 0.001  # 0.1% of volume
                    trade_size = np.random.exponential(mean_retail_size)
                    trade_size = min(trade_size, volume * 0.05)  # Cap at 5%
                
                trade_size = max(trade_size, 100)  # Minimum trade size
                
                # Add some time jitter within the period
                trade_timestamp = timestamp + pd.Timedelta(
                    minutes=np.random.uniform(0, 60)  # Assume 1H periods
                )
                
                trade = Trade(
                    timestamp=trade_timestamp,
                    price=round(trade_price, 2),
                    size=round(trade_size, 0),
                    side=TradeType.BUY if is_buy else TradeType.SELL,
                    trade_id=f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{i:03d}"
                )
                
                trades.append(trade)
        
        # Sort trades by timestamp
        trades.sort(key=lambda x: x.timestamp)
        return trades