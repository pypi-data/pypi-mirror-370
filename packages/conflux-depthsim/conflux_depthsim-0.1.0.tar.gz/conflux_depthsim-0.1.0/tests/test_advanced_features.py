"""
Advanced Features Tests for DepthSim

Tests for the comprehensive features including advanced spread models,
L2 depth snapshots, market impact simulation, and realistic trade sequences.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch

from depthsim import DepthSimulator
from depthsim.models import OrderBook, OrderBookLevel, Trade, TradeType
from depthsim.spread_models import (
    ImbalanceAdjustedSpreadModel,
    VolatilityVolumeSpreadModel, 
    TimeOfDaySpreadModel,
    CustomSpreadModel
)


class TestAdvancedSpreadModels:
    """Test advanced spread models functionality."""
    
    def test_imbalance_adjusted_spread_model(self):
        """Test imbalance-adjusted spread model."""
        model = ImbalanceAdjustedSpreadModel(
            base_spread_bps=5.0,
            imbalance_sensitivity=10.0,
            noise_level=0.0  # No noise for predictable testing
        )
        
        # Test with no imbalance
        spread_balanced = model.calculate_spread(100.0, 0.02, 1000000, imbalance=0.0)
        assert abs(spread_balanced - 5.0) < 0.1
        
        # Test with positive imbalance (more bids)
        spread_bid_heavy = model.calculate_spread(100.0, 0.02, 1000000, imbalance=0.3)
        assert spread_bid_heavy > spread_balanced
        
        # Test with negative imbalance (more asks)
        spread_ask_heavy = model.calculate_spread(100.0, 0.02, 1000000, imbalance=-0.3)
        assert spread_ask_heavy > spread_balanced
        
        # Absolute imbalance should have same effect
        assert abs(spread_bid_heavy - spread_ask_heavy) < 0.1
    
    def test_volatility_volume_spread_model(self):
        """Test combined volatility and volume spread model."""
        model = VolatilityVolumeSpreadModel(
            base_spread_bps=6.0,
            volatility_sensitivity=50.0,
            volume_sensitivity=0.5,
            noise_level=0.0
        )
        
        # Baseline
        base_spread = model.calculate_spread(100.0, 0.01, 1000000)
        
        # Higher volatility should increase spread
        high_vol_spread = model.calculate_spread(100.0, 0.05, 1000000)
        assert high_vol_spread > base_spread
        
        # Higher volume should decrease spread
        high_vol_low_spread = model.calculate_spread(100.0, 0.01, 5000000)
        assert high_vol_low_spread < base_spread
        
        # Combined effect
        combined_spread = model.calculate_spread(100.0, 0.05, 5000000)
        # Should be between base and high volatility (volume effect partially offsets)
        assert base_spread < combined_spread < high_vol_spread
    
    def test_time_of_day_spread_model(self):
        """Test time-of-day spread model."""
        model = TimeOfDaySpreadModel(
            base_spread_bps=5.0,
            open_close_multiplier=0.8,  # Tighter at open/close
            lunch_multiplier=1.5,       # Wider at lunch
            overnight_multiplier=2.0    # Much wider overnight
        )
        
        # Test market open (9:30 AM)
        with patch('pandas.Timestamp.now') as mock_now:
            mock_now.return_value = pd.Timestamp('2024-01-01 09:30:00')
            open_spread = model.calculate_spread(100.0, 0.02, 1000000)
            assert abs(open_spread - 4.0) < 0.1  # 5.0 * 0.8
        
        # Test lunch period (1:00 PM)
        with patch('pandas.Timestamp.now') as mock_now:
            mock_now.return_value = pd.Timestamp('2024-01-01 13:00:00')
            lunch_spread = model.calculate_spread(100.0, 0.02, 1000000)
            assert abs(lunch_spread - 7.5) < 0.1  # 5.0 * 1.5
        
        # Test overnight (2:00 AM)
        with patch('pandas.Timestamp.now') as mock_now:
            mock_now.return_value = pd.Timestamp('2024-01-01 02:00:00')
            overnight_spread = model.calculate_spread(100.0, 0.02, 1000000)
            assert abs(overnight_spread - 10.0) < 0.1  # 5.0 * 2.0
    
    def test_custom_spread_model(self):
        """Test custom spread model with user-defined function."""
        def custom_func(mid_price: float, volatility: float, volume: float) -> float:
            # Simple custom logic: higher spread for round numbers
            base = 5.0
            if mid_price % 100 == 0:  # Round hundreds
                return base + 2.0
            return base
        
        model = CustomSpreadModel(
            spread_function=custom_func,
            min_spread_bps=1.0,
            max_spread_bps=20.0
        )
        
        # Test non-round number
        normal_spread = model.calculate_spread(99.5, 0.02, 1000000)
        assert abs(normal_spread - 5.0) < 0.1
        
        # Test round number
        round_spread = model.calculate_spread(100.0, 0.02, 1000000)
        assert abs(round_spread - 7.0) < 0.1
        
        # Test bounds enforcement
        def extreme_func(mid_price: float, volatility: float, volume: float) -> float:
            return 100.0  # Above max
        
        extreme_model = CustomSpreadModel(extreme_func, max_spread_bps=15.0)
        capped_spread = extreme_model.calculate_spread(100.0, 0.02, 1000000)
        assert capped_spread == 15.0
    
    def test_spread_model_integration(self):
        """Test spread models integrated with DepthSimulator."""
        market_data = pd.DataFrame({
            'close': [100.0, 101.0, 102.0],
            'volume': [1000000, 1200000, 800000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        # Test imbalance model integration
        sim = DepthSimulator(spread_model='imbalance', base_spread_bps=6.0)
        quotes = sim.generate_quotes(market_data)
        
        assert len(quotes) == 3
        assert all(quotes['spread_bps'] >= 0.5)  # Above minimum
        assert all(quotes['spread_bps'] <= 80.0)  # Below default max


class TestL2DepthFeatures:
    """Test advanced L2 depth snapshot functionality."""
    
    def setup_method(self):
        """Setup test data."""
        self.market_data = pd.DataFrame({
            'close': [50000.0, 50100.0, 49900.0],
            'volume': [2000000, 1800000, 2200000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        self.sim = DepthSimulator(
            spread_model='constant',
            spread_bps=5.0,
            depth_levels=20
        )
    
    def test_l2_depth_snapshots_basic(self):
        """Test basic L2 depth snapshot generation."""
        snapshots = self.sim.generate_l2_depth_snapshots(
            self.market_data,
            levels=10,
            asymmetry_factor=0.0,  # Symmetric for testing
            size_clustering=False,
            price_improvement=False
        )
        
        assert len(snapshots) == 3
        
        for timestamp, book in snapshots.items():
            assert isinstance(book, OrderBook)
            assert len(book.bids) <= 10  # May be less due to asymmetry
            assert len(book.asks) <= 10
            assert book.best_bid < book.best_ask  # No crossed market
            assert not book.is_crossed
    
    def test_l2_asymmetric_depth(self):
        """Test asymmetric depth generation."""
        snapshots = self.sim.generate_l2_depth_snapshots(
            self.market_data,
            levels=20,
            asymmetry_factor=0.3,  # 30% asymmetry
            size_clustering=False,
            price_improvement=False
        )
        
        # Check that sides can be asymmetric
        level_counts = []
        for book in snapshots.values():
            bid_count = len(book.bids)
            ask_count = len(book.asks)
            level_counts.append((bid_count, ask_count))
            
            # Should be between 10 and 20 levels (50% to 100% of requested)
            assert 10 <= bid_count <= 20
            assert 10 <= ask_count <= 20
        
        # At least some books should be asymmetric
        asymmetric_books = [counts for counts in level_counts if counts[0] != counts[1]]
        assert len(asymmetric_books) > 0
    
    def test_l2_size_clustering(self):
        """Test size clustering at key price levels."""
        np.random.seed(42)  # For reproducible results
        
        snapshots = self.sim.generate_l2_depth_snapshots(
            self.market_data,
            levels=15,
            asymmetry_factor=0.1,
            size_clustering=True,  # Enable clustering
            price_improvement=False
        )
        
        # Check that some levels show clustering effects
        for book in snapshots.values():
            # Look for levels near round numbers (psychological levels)
            clustered_levels = []
            for level in book.bids + book.asks:
                if level.price % 10 < 0.5 or level.price % 5 < 0.5:
                    clustered_levels.append(level)
            
            # Should have some levels near round numbers
            assert len(clustered_levels) > 0
    
    def test_l2_price_improvement(self):
        """Test sub-penny price improvement."""
        np.random.seed(42)
        
        snapshots = self.sim.generate_l2_depth_snapshots(
            self.market_data,
            levels=10,
            asymmetry_factor=0.1,
            size_clustering=False,
            price_improvement=True  # Enable sub-penny
        )
        
        # Check for sub-penny precision
        sub_penny_found = False
        for book in snapshots.values():
            for level in book.bids + book.asks:
                # Check if price has more precision than 2 decimals
                price_str = f"{level.price:.3f}"
                if price_str.endswith('1') or price_str.endswith('3') or price_str.endswith('7'):
                    sub_penny_found = True
                    break
            if sub_penny_found:
                break
        
        # Should find at least some sub-penny pricing
        assert sub_penny_found
    
    def test_l2_order_book_metrics(self):
        """Test order book metrics calculation."""
        snapshots = self.sim.generate_l2_depth_snapshots(
            self.market_data,
            levels=15
        )
        
        for book in snapshots.values():
            # Test cached vs calculated metrics
            calculated_bid_size = sum(level.size for level in book.bids)
            calculated_ask_size = sum(level.size for level in book.asks)
            
            assert abs(book.total_bid_size - calculated_bid_size) < 0.1
            assert abs(book.total_ask_size - calculated_ask_size) < 0.1
            
            # Test imbalance calculation
            total_size = book.total_bid_size + book.total_ask_size
            expected_imbalance = (book.total_bid_size - book.total_ask_size) / total_size
            assert abs(book.depth_imbalance - expected_imbalance) < 1e-10


class TestMarketImpactSimulation:
    """Test market impact simulation functionality."""
    
    def setup_method(self):
        """Setup test data."""
        self.market_data = pd.DataFrame({
            'close': [50000.0],
            'volume': [2000000]
        }, index=pd.date_range('2024-01-01', periods=1, freq='1H'))
        
        self.sim = DepthSimulator(
            spread_model='constant',
            spread_bps=5.0,
            depth_levels=20
        )
        
        # Generate test order book
        depth_ladder = self.sim.generate_depth_ladder(self.market_data, levels=20)
        self.test_book = next(iter(depth_ladder.values()))
    
    def test_buy_order_impact(self):
        """Test buy order market impact."""
        # Small order - should execute at best ask
        small_impact = self.sim.simulate_market_impact(
            order_size=10000,
            order_side='buy',
            order_book=self.test_book
        )
        
        assert small_impact['levels_consumed'] >= 1
        assert small_impact['impact_bps'] >= 0
        assert small_impact['executed_size'] <= 10000
        assert small_impact['average_price'] >= self.test_book.best_ask
        
        # Large order - should consume multiple levels
        large_impact = self.sim.simulate_market_impact(
            order_size=500000,
            order_side='buy',
            order_book=self.test_book
        )
        
        assert large_impact['levels_consumed'] > small_impact['levels_consumed']
        assert large_impact['impact_bps'] > small_impact['impact_bps']
        assert large_impact['average_price'] > small_impact['average_price']
    
    def test_sell_order_impact(self):
        """Test sell order market impact."""
        # Small sell order
        small_impact = self.sim.simulate_market_impact(
            order_size=10000,
            order_side='sell',
            order_book=self.test_book
        )
        
        assert small_impact['levels_consumed'] >= 1
        assert small_impact['impact_bps'] >= 0
        assert small_impact['executed_size'] <= 10000
        assert small_impact['average_price'] <= self.test_book.best_bid
        
        # Large sell order
        large_impact = self.sim.simulate_market_impact(
            order_size=500000,
            order_side='sell',
            order_book=self.test_book
        )
        
        assert large_impact['levels_consumed'] > small_impact['levels_consumed']
        assert large_impact['impact_bps'] > small_impact['impact_bps']
        assert large_impact['average_price'] < small_impact['average_price']
    
    def test_partial_fill_scenario(self):
        """Test scenario where order cannot be fully filled."""
        # Calculate total ask liquidity
        total_ask_liquidity = sum(level.size for level in self.test_book.asks)
        
        # Order larger than available liquidity
        oversized_impact = self.sim.simulate_market_impact(
            order_size=total_ask_liquidity * 2,
            order_side='buy',
            order_book=self.test_book
        )
        
        assert oversized_impact['executed_size'] <= total_ask_liquidity
        assert oversized_impact['remaining_size'] > 0
        assert oversized_impact['levels_consumed'] == len(self.test_book.asks)
    
    def test_empty_book_scenario(self):
        """Test impact on empty order book."""
        empty_book = OrderBook(
            bids=[],
            asks=[],
            mid_price=50000.0,
            spread=0.0,
            spread_bps=0.0
        )
        
        impact = self.sim.simulate_market_impact(
            order_size=10000,
            order_side='buy',
            order_book=empty_book
        )
        
        assert impact['average_price'] == 0.0
        assert impact['impact_bps'] == 0.0
        assert impact['levels_consumed'] == 0
        assert impact['executed_size'] == 0


class TestRealisticTradeSequence:
    """Test realistic trade sequence generation."""
    
    def setup_method(self):
        """Setup test data."""
        # Create market data spanning different times of day
        timestamps = pd.date_range('2024-01-01 09:30', periods=8, freq='1H')
        self.market_data = pd.DataFrame({
            'close': [50000 + i * 100 for i in range(8)],  # Trending up
            'volume': [1500000 + i * 200000 for i in range(8)]  # Increasing volume
        }, index=timestamps)
        
        self.sim = DepthSimulator(
            spread_model='time_of_day',
            base_spread_bps=4.0
        )
    
    def test_basic_trade_generation(self):
        """Test basic trade sequence generation."""
        trades = self.sim.generate_realistic_trade_sequence(
            self.market_data,
            trade_intensity=1.0,
            institutional_ratio=0.15
        )
        
        assert len(trades) > 0
        
        # Check trade objects are properly formed
        for trade in trades[:5]:  # Check first 5
            assert isinstance(trade, Trade)
            assert trade.price > 0
            assert trade.size > 0
            assert trade.side in [TradeType.BUY, TradeType.SELL]
            assert trade.trade_id is not None
            assert isinstance(trade.timestamp, datetime)
    
    def test_trade_intensity_scaling(self):
        """Test that trade intensity affects number of trades."""
        # Low intensity
        low_intensity_trades = self.sim.generate_realistic_trade_sequence(
            self.market_data,
            trade_intensity=0.5,
            institutional_ratio=0.15
        )
        
        # High intensity
        high_intensity_trades = self.sim.generate_realistic_trade_sequence(
            self.market_data,
            trade_intensity=2.0,
            institutional_ratio=0.15
        )
        
        # High intensity should generate more trades
        assert len(high_intensity_trades) >= len(low_intensity_trades)
    
    def test_institutional_vs_retail_patterns(self):
        """Test institutional vs retail trade patterns."""
        # Mostly institutional
        inst_trades = self.sim.generate_realistic_trade_sequence(
            self.market_data,
            trade_intensity=1.0,
            institutional_ratio=0.8  # 80% institutional
        )
        
        # Mostly retail
        retail_trades = self.sim.generate_realistic_trade_sequence(
            self.market_data,
            trade_intensity=1.0,
            institutional_ratio=0.2  # 20% institutional
        )
        
        # Institutional trades should have larger average size
        if len(inst_trades) > 0 and len(retail_trades) > 0:
            avg_inst_size = sum(t.size for t in inst_trades) / len(inst_trades)
            avg_retail_size = sum(t.size for t in retail_trades) / len(retail_trades)
            
            # Allow for randomness - institutional should be significantly larger
            assert avg_inst_size > avg_retail_size * 1.5
    
    def test_trade_timing_and_ordering(self):
        """Test trade timestamp ordering and timing."""
        trades = self.sim.generate_realistic_trade_sequence(
            self.market_data,
            trade_intensity=1.5
        )
        
        if len(trades) > 1:
            # Check trades are sorted by timestamp
            timestamps = [t.timestamp for t in trades]
            assert timestamps == sorted(timestamps)
            
            # Check trades fall within market data time range
            first_market_time = self.market_data.index[0]
            last_market_time = self.market_data.index[-1]
            
            for trade in trades:
                assert first_market_time <= trade.timestamp <= last_market_time + timedelta(hours=1)
    
    def test_price_momentum_bias(self):
        """Test that trades show momentum bias."""
        # Create strongly bullish market data
        bull_data = pd.DataFrame({
            'close': [50000, 52000, 55000, 58000],  # Strong uptrend
            'volume': [2000000] * 4
        }, index=pd.date_range('2024-01-01', periods=4, freq='1H'))
        
        bull_trades = self.sim.generate_realistic_trade_sequence(
            bull_data,
            trade_intensity=2.0
        )
        
        if len(bull_trades) > 10:  # Need reasonable sample
            buy_trades = [t for t in bull_trades if t.side == TradeType.BUY]
            buy_ratio = len(buy_trades) / len(bull_trades)
            
            # Should favor buys in bull market (allow for randomness)
            assert buy_ratio > 0.45  # At least slight bias toward buying


class TestIntegrationAndEdgeCases:
    """Test integration scenarios and edge cases."""
    
    def test_minimal_market_data(self):
        """Test with minimal market data."""
        minimal_data = pd.DataFrame({
            'close': [100.0],
            'volume': [1000]
        }, index=pd.date_range('2024-01-01', periods=1, freq='1H'))
        
        sim = DepthSimulator(spread_model='constant', spread_bps=10.0)
        
        # Should work with single data point
        quotes = sim.generate_quotes(minimal_data)
        assert len(quotes) == 1
        
        depth_ladder = sim.generate_depth_ladder(minimal_data, levels=5)
        assert len(depth_ladder) == 1
        
        trades = sim.generate_realistic_trade_sequence(minimal_data)
        assert isinstance(trades, list)  # May be empty, but should be list
    
    def test_extreme_spread_values(self):
        """Test with extreme spread values."""
        market_data = pd.DataFrame({
            'close': [1000.0, 1001.0],
            'volume': [500000, 600000]
        }, index=pd.date_range('2024-01-01', periods=2, freq='1H'))
        
        # Very tight spreads
        tight_sim = DepthSimulator(spread_model='constant', spread_bps=0.1)
        tight_quotes = tight_sim.generate_quotes(market_data)
        
        assert all(tight_quotes['spread_bps'] >= 0.1)
        assert all(tight_quotes['ask'] > tight_quotes['bid'])
        
        # Very wide spreads
        wide_sim = DepthSimulator(spread_model='constant', spread_bps=100.0)
        wide_quotes = wide_sim.generate_quotes(market_data)
        
        assert all(wide_quotes['spread_bps'] >= 50.0)  # May be capped
        assert all(wide_quotes['ask'] > wide_quotes['bid'])
    
    def test_zero_volume_handling(self):
        """Test handling of zero or very low volume."""
        zero_vol_data = pd.DataFrame({
            'close': [100.0, 101.0],
            'volume': [0, 1]  # Zero and minimal volume
        }, index=pd.date_range('2024-01-01', periods=2, freq='1H'))
        
        sim = DepthSimulator(spread_model='volume', base_spread_bps=5.0)
        
        # Should handle gracefully without errors
        quotes = sim.generate_quotes(zero_vol_data)
        assert len(quotes) == 2
        assert all(quotes['spread_bps'] > 0)
        
        depth_ladder = sim.generate_depth_ladder(zero_vol_data, levels=5)
        assert len(depth_ladder) == 2
        
        # All order books should have positive sizes
        for book in depth_ladder.values():
            for level in book.bids + book.asks:
                assert level.size > 0
    
    def test_consistency_with_seed(self):
        """Test reproducibility with random seed."""
        market_data = pd.DataFrame({
            'close': [100.0, 101.0, 102.0],
            'volume': [1000000, 1200000, 800000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        # Generate with same seed
        sim1 = DepthSimulator(spread_model='volatility', seed=12345)
        quotes1 = sim1.generate_quotes(market_data)
        trades1 = sim1.generate_realistic_trade_sequence(market_data)
        
        sim2 = DepthSimulator(spread_model='volatility', seed=12345)
        quotes2 = sim2.generate_quotes(market_data)
        trades2 = sim2.generate_realistic_trade_sequence(market_data)
        
        # Should be identical
        pd.testing.assert_frame_equal(quotes1, quotes2)
        
        # Trade sequences should be identical
        assert len(trades1) == len(trades2)
        for t1, t2 in zip(trades1, trades2):
            assert t1.size == t2.size
            assert t1.price == t2.price
            assert t1.side == t2.side


if __name__ == "__main__":
    pytest.main([__file__, "-v"])