"""
Basic tests for DepthSim package functionality.

This module contains fundamental tests to ensure the core DepthSim
functionality works correctly after the refactor from MockFlow.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from depthsim import DepthSimulator
from depthsim.models import OrderBook, OrderBookLevel, Quote, Trade, TradeType, SpreadModel
from depthsim.spread_models import (
    ConstantSpreadModel, 
    VolatilityLinkedSpreadModel,
    ImbalanceAdjustedSpreadModel
)


class TestDepthSimulatorBasic:
    """Test basic DepthSimulator functionality."""
    
    def test_depthsim_imports(self):
        """Test that all main components can be imported."""
        from depthsim import DepthSimulator, OrderBook, OrderBookLevel
        from depthsim.spread_models import ConstantSpreadModel, VolatilityLinkedSpreadModel
        
        assert DepthSimulator is not None
        assert OrderBook is not None
        assert OrderBookLevel is not None
        assert ConstantSpreadModel is not None
        assert VolatilityLinkedSpreadModel is not None
    
    def test_basic_depth_simulator_creation(self):
        """Test creating a basic DepthSimulator."""
        sim = DepthSimulator()
        assert sim is not None
        assert sim.depth_levels == 10  # default value
    
    def test_generate_quotes_basic(self):
        """Test basic quote generation from market data."""
        # Create simple market data
        market_data = pd.DataFrame({
            'close': [100.0, 101.0, 102.0, 101.5, 103.0],
            'volume': [1000000, 1200000, 800000, 1500000, 900000]
        }, index=pd.date_range('2024-01-01', periods=5, freq='1H'))
        
        sim = DepthSimulator(spread_model='constant', spread_bps=5.0)
        quotes = sim.generate_quotes(market_data)
        
        # Basic validation
        assert len(quotes) == 5
        assert 'bid' in quotes.columns
        assert 'ask' in quotes.columns
        assert 'mid' in quotes.columns
        assert 'spread_bps' in quotes.columns
        
        # Verify ask > bid for all quotes
        assert all(quotes['ask'] > quotes['bid'])
        
        # Verify mid price matches close price
        np.testing.assert_array_almost_equal(quotes['mid'].values, market_data['close'].values)
    
    def test_spread_models(self):
        """Test different spread models."""
        market_data = pd.DataFrame({
            'close': [100.0] * 5,
            'volume': [1000000] * 5
        }, index=pd.date_range('2024-01-01', periods=5, freq='1H'))
        
        # Test constant spread
        sim_constant = DepthSimulator(spread_model='constant', spread_bps=10.0)
        quotes_constant = sim_constant.generate_quotes(market_data)
        
        # All spreads should be approximately 10bp (allowing for minor rounding)
        assert all(abs(quotes_constant['spread_bps'] - 10.0) < 0.1)
        
        # Test volatility model with zero volatility (should be close to base)
        sim_vol = DepthSimulator(spread_model='volatility', base_spread_bps=8.0)
        quotes_vol = sim_vol.generate_quotes(market_data)
        
        # With zero volatility, spreads should be close to base
        assert all(quotes_vol['spread_bps'] >= 0.5)  # Minimum bound
        assert all(quotes_vol['spread_bps'] <= 20.0)  # Reasonable upper bound for this case
    
    def test_depth_ladder_generation(self):
        """Test order book depth ladder generation."""
        market_data = pd.DataFrame({
            'close': [50000.0, 50100.0],
            'volume': [2000000, 1800000]
        }, index=pd.date_range('2024-01-01', periods=2, freq='1H'))
        
        sim = DepthSimulator(spread_model='constant', spread_bps=5.0, depth_levels=5)
        depth_ladder = sim.generate_depth_ladder(market_data, levels=5)
        
        assert len(depth_ladder) == 2  # Two timestamps
        
        for timestamp, order_book in depth_ladder.items():
            assert isinstance(order_book, OrderBook)
            assert len(order_book.bids) == 5
            assert len(order_book.asks) == 5
            
            # Verify bid prices are descending
            bid_prices = [level.price for level in order_book.bids]
            assert bid_prices == sorted(bid_prices, reverse=True)
            
            # Verify ask prices are ascending
            ask_prices = [level.price for level in order_book.asks]
            assert ask_prices == sorted(ask_prices)
            
            # Verify no crossed market
            assert order_book.best_bid < order_book.best_ask
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        sim = DepthSimulator()
        
        # Test missing columns
        invalid_data = pd.DataFrame({
            'price': [100.0, 101.0],  # Wrong column name
            'volume': [1000000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=2, freq='1H'))
        
        with pytest.raises(ValueError, match="Price column 'close' not found"):
            sim.generate_quotes(invalid_data)
    
    def test_reproducibility(self):
        """Test that results are reproducible with same seed."""
        market_data = pd.DataFrame({
            'close': [100.0, 101.0, 102.0],
            'volume': [1000000, 1200000, 800000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        # Generate quotes with same seed
        sim1 = DepthSimulator(spread_model='volatility', seed=42)
        quotes1 = sim1.generate_quotes(market_data)
        
        sim2 = DepthSimulator(spread_model='volatility', seed=42)
        quotes2 = sim2.generate_quotes(market_data)
        
        # Results should be identical
        pd.testing.assert_frame_equal(quotes1, quotes2)
    
    def test_new_spread_models_basic(self):
        """Test basic functionality of new spread models."""
        market_data = pd.DataFrame({
            'close': [100.0, 101.0, 102.0],
            'volume': [1000000, 1200000, 800000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1h'))
        
        # Test imbalance model
        sim_imbalance = DepthSimulator(spread_model='imbalance', base_spread_bps=6.0)
        quotes_imbalance = sim_imbalance.generate_quotes(market_data)
        
        assert len(quotes_imbalance) == 3
        assert all(quotes_imbalance['spread_bps'] >= 0.5)  # Above minimum
        
        # Test time-of-day model
        sim_tod = DepthSimulator(spread_model='time_of_day', base_spread_bps=5.0)
        quotes_tod = sim_tod.generate_quotes(market_data)
        
        assert len(quotes_tod) == 3
        assert all(quotes_tod['spread_bps'] > 0)
    
    def test_l2_depth_snapshots_basic(self):
        """Test basic L2 depth snapshot functionality."""
        market_data = pd.DataFrame({
            'close': [50000.0, 50100.0],
            'volume': [2000000, 1800000]
        }, index=pd.date_range('2024-01-01', periods=2, freq='1h'))
        
        sim = DepthSimulator(spread_model='constant', spread_bps=5.0)
        snapshots = sim.generate_l2_depth_snapshots(market_data, levels=10)
        
        assert len(snapshots) == 2
        
        for timestamp, book in snapshots.items():
            assert isinstance(book, OrderBook)
            assert len(book.bids) > 0
            assert len(book.asks) > 0
            assert book.best_bid < book.best_ask
    
    def test_market_impact_basic(self):
        """Test basic market impact simulation."""
        market_data = pd.DataFrame({
            'close': [50000.0],
            'volume': [2000000]
        }, index=pd.date_range('2024-01-01', periods=1, freq='1h'))
        
        sim = DepthSimulator(spread_model='constant', spread_bps=5.0)
        depth_ladder = sim.generate_depth_ladder(market_data, levels=15)
        test_book = next(iter(depth_ladder.values()))
        
        # Test small buy order
        impact = sim.simulate_market_impact(10000, 'buy', test_book)
        
        assert isinstance(impact, dict)
        assert 'average_price' in impact
        assert 'impact_bps' in impact
        assert 'executed_size' in impact
        assert impact['impact_bps'] >= 0
        assert impact['executed_size'] > 0


class TestSpreadModels:
    """Test spread model functionality."""
    
    def test_constant_spread_model(self):
        """Test constant spread model."""
        model = ConstantSpreadModel(spread_bps=7.5)
        
        spread = model.calculate_spread(100.0, 0.02, 1000000)
        assert spread == 7.5
        
        # Should be same regardless of inputs
        spread2 = model.calculate_spread(200.0, 0.05, 500000)
        assert spread2 == 7.5
    
    def test_volatility_linked_spread_model(self):
        """Test volatility-linked spread model."""
        model = VolatilityLinkedSpreadModel(
            base_spread_bps=5.0,
            volatility_sensitivity=50.0,
            noise_level=0.0  # No noise for predictable testing
        )
        
        # Low volatility
        spread_low = model.calculate_spread(100.0, 0.01, 1000000)
        
        # High volatility
        spread_high = model.calculate_spread(100.0, 0.05, 1000000)
        
        # High volatility should produce wider spread
        assert spread_high > spread_low
        
        # Both should be within reasonable bounds
        assert 0.5 <= spread_low <= 100.0
        assert 0.5 <= spread_high <= 100.0


class TestOrderBookModels:
    """Test order book data structures."""
    
    def test_order_book_level_creation(self):
        """Test OrderBookLevel creation and validation."""
        level = OrderBookLevel(price=100.0, size=5000, orders=3)
        
        assert level.price == 100.0
        assert level.size == 5000
        assert level.orders == 3
    
    def test_order_book_level_validation(self):
        """Test OrderBookLevel validation."""
        # Invalid price
        with pytest.raises(ValueError, match="Price must be positive"):
            OrderBookLevel(price=0.0, size=5000, orders=3)
        
        # Invalid size
        with pytest.raises(ValueError, match="Size cannot be negative"):
            OrderBookLevel(price=100.0, size=-1000, orders=3)
    
    def test_order_book_properties(self):
        """Test OrderBook properties and calculations."""
        bids = [
            OrderBookLevel(100.0, 5000, 2),
            OrderBookLevel(99.5, 3000, 1)
        ]
        asks = [
            OrderBookLevel(100.5, 4000, 2),
            OrderBookLevel(101.0, 6000, 3)
        ]
        
        book = OrderBook(
            bids=bids,
            asks=asks,
            mid_price=100.25,
            spread=0.5,
            spread_bps=50.0
        )
        
        assert book.best_bid == 100.0
        assert book.best_ask == 100.5
        assert book.total_bid_size == 8000
        assert book.total_ask_size == 10000
        assert not book.is_crossed
        
        # Test depth imbalance calculation
        expected_imbalance = (8000 - 10000) / (8000 + 10000)
        assert abs(book.depth_imbalance - expected_imbalance) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])