"""
DepthSim Spread Models

This module contains different spread calculation models for realistic bid-ask spread simulation:
- Constant spread model (fixed spread)
- Volatility-linked spread model (spreads widen with volatility)
- Volume-linked spread model (spreads tighten with volume)
- Combined models and custom functions
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Callable, Optional
import pandas as pd


class BaseSpreadModel(ABC):
    """Base class for spread calculation models."""
    
    @abstractmethod
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """
        Calculate spread in basis points for given market conditions.
        
        Args:
            mid_price: Current mid price
            volatility: Current volatility measure
            volume: Current volume
            **kwargs: Additional parameters for specific models
            
        Returns:
            Spread in basis points
        """
        pass


class ConstantSpreadModel(BaseSpreadModel):
    """
    Simple constant spread model.
    
    Always returns the same spread regardless of market conditions.
    Useful for baseline scenarios or markets with very stable spreads.
    """
    
    def __init__(self, spread_bps: float = 5.0):
        """
        Initialize constant spread model.
        
        Args:
            spread_bps: Fixed spread in basis points
        """
        if spread_bps <= 0:
            raise ValueError("Spread must be positive")
        
        self.spread_bps = spread_bps
    
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """Calculate constant spread."""
        return self.spread_bps


class VolatilityLinkedSpreadModel(BaseSpreadModel):
    """
    Volatility-linked spread model.
    
    Spreads widen during high volatility periods as market makers 
    demand higher compensation for increased risk.
    """
    
    def __init__(
        self, 
        base_spread_bps: float = 5.0,
        volatility_sensitivity: float = 50.0,
        min_spread_bps: float = 0.5,
        max_spread_bps: float = 100.0,
        noise_level: float = 0.5
    ):
        """
        Initialize volatility-linked spread model.
        
        Args:
            base_spread_bps: Base spread when volatility is zero
            volatility_sensitivity: How much volatility affects spread (bp per unit volatility)
            min_spread_bps: Minimum allowed spread
            max_spread_bps: Maximum allowed spread  
            noise_level: Random noise level to add realism
        """
        self.base_spread_bps = base_spread_bps
        self.volatility_sensitivity = volatility_sensitivity
        self.min_spread_bps = min_spread_bps
        self.max_spread_bps = max_spread_bps
        self.noise_level = noise_level
    
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """Calculate volatility-linked spread."""
        # Base spread plus volatility impact
        spread = self.base_spread_bps + (volatility * self.volatility_sensitivity)
        
        # Add random noise for realism
        if self.noise_level > 0:
            spread += np.random.normal(0, self.noise_level)
        
        # Apply bounds
        spread = max(min(spread, self.max_spread_bps), self.min_spread_bps)
        
        return spread


class ImbalanceAdjustedSpreadModel(BaseSpreadModel):
    """
    Spread model that adjusts based on order book imbalance.
    
    Spreads widen when there's significant bid/ask imbalance,
    reflecting increased adverse selection risk.
    """
    
    def __init__(
        self,
        base_spread_bps: float = 6.0,
        imbalance_sensitivity: float = 20.0,
        min_spread_bps: float = 0.5,
        max_spread_bps: float = 80.0,
        noise_level: float = 0.4
    ):
        """
        Initialize imbalance-adjusted spread model.
        
        Args:
            base_spread_bps: Base spread for balanced book
            imbalance_sensitivity: How much imbalance affects spread
            min_spread_bps: Minimum allowed spread
            max_spread_bps: Maximum allowed spread
            noise_level: Random noise level
        """
        self.base_spread_bps = base_spread_bps
        self.imbalance_sensitivity = imbalance_sensitivity
        self.min_spread_bps = min_spread_bps
        self.max_spread_bps = max_spread_bps
        self.noise_level = noise_level
    
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """Calculate imbalance-adjusted spread."""
        # Extract imbalance from kwargs (if available)
        imbalance = kwargs.get('imbalance', 0.0)  # -1 to 1 scale
        
        # Base spread plus imbalance impact
        spread = self.base_spread_bps + (abs(imbalance) * self.imbalance_sensitivity)
        
        # Add random noise
        if self.noise_level > 0:
            spread += np.random.normal(0, self.noise_level)
        
        # Apply bounds
        spread = max(min(spread, self.max_spread_bps), self.min_spread_bps)
        
        return spread


class VolumeLinkedSpreadModel(BaseSpreadModel):
    """
    Volume-linked spread model.
    
    Spreads tighten with higher volume as increased competition
    between market makers leads to tighter quotes.
    """
    
    def __init__(
        self,
        base_spread_bps: float = 8.0,
        volume_sensitivity: float = 0.8,
        volume_normalization: float = 1_000_000,
        min_spread_bps: float = 0.5,
        max_spread_bps: float = 50.0,
        noise_level: float = 0.3
    ):
        """
        Initialize volume-linked spread model.
        
        Args:
            base_spread_bps: Base spread for zero volume
            volume_sensitivity: How much volume tightens spreads (bp per normalized unit)
            volume_normalization: Volume level for normalization (1.0 unit)
            min_spread_bps: Minimum allowed spread
            max_spread_bps: Maximum allowed spread
            noise_level: Random noise level
        """
        self.base_spread_bps = base_spread_bps
        self.volume_sensitivity = volume_sensitivity
        self.volume_normalization = volume_normalization
        self.min_spread_bps = min_spread_bps
        self.max_spread_bps = max_spread_bps
        self.noise_level = noise_level
    
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """Calculate volume-linked spread."""
        # Normalize volume
        volume_normalized = min(volume / self.volume_normalization, 5.0)  # Cap at 5x
        
        # Base spread minus volume impact (tighter with more volume)
        spread = self.base_spread_bps - (volume_normalized * self.volume_sensitivity)
        
        # Add random noise
        if self.noise_level > 0:
            spread += np.random.normal(0, self.noise_level)
        
        # Apply bounds
        spread = max(min(spread, self.max_spread_bps), self.min_spread_bps)
        
        return spread


class VolatilityVolumeSpreadModel(BaseSpreadModel):
    """
    Combined volatility and volume spread model.
    
    Spreads respond to both volatility (widening) and volume (tightening)
    to create realistic market microstructure behavior.
    """
    
    def __init__(
        self,
        base_spread_bps: float = 6.0,
        volatility_sensitivity: float = 40.0,
        volume_sensitivity: float = 0.6,
        volume_normalization: float = 1_000_000,
        min_spread_bps: float = 0.5,
        max_spread_bps: float = 100.0,
        noise_level: float = 0.4
    ):
        """
        Initialize combined volatility-volume spread model.
        
        Args:
            base_spread_bps: Base spread 
            volatility_sensitivity: Volatility impact (bp per unit)
            volume_sensitivity: Volume impact (bp per normalized unit)
            volume_normalization: Volume normalization level
            min_spread_bps: Minimum spread
            max_spread_bps: Maximum spread
            noise_level: Random noise level
        """
        self.base_spread_bps = base_spread_bps
        self.volatility_sensitivity = volatility_sensitivity
        self.volume_sensitivity = volume_sensitivity
        self.volume_normalization = volume_normalization
        self.min_spread_bps = min_spread_bps
        self.max_spread_bps = max_spread_bps
        self.noise_level = noise_level
    
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """Calculate combined volatility-volume spread."""
        # Volatility impact (widening)
        vol_impact = volatility * self.volatility_sensitivity
        
        # Volume impact (tightening)
        volume_normalized = min(volume / self.volume_normalization, 3.0)
        volume_impact = volume_normalized * self.volume_sensitivity
        
        # Combined spread
        spread = self.base_spread_bps + vol_impact - volume_impact
        
        # Add random noise
        if self.noise_level > 0:
            spread += np.random.normal(0, self.noise_level)
        
        # Apply bounds
        spread = max(min(spread, self.max_spread_bps), self.min_spread_bps)
        
        return spread


class TimeOfDaySpreadModel(BaseSpreadModel):
    """
    Time-of-day spread model.
    
    Spreads vary based on market session (wider during low-liquidity periods
    like overnight, tighter during main trading hours).
    """
    
    def __init__(
        self,
        base_spread_bps: float = 5.0,
        overnight_multiplier: float = 2.0,
        lunch_multiplier: float = 1.3,
        open_close_multiplier: float = 0.8,
        min_spread_bps: float = 0.5,
        max_spread_bps: float = 50.0
    ):
        """
        Initialize time-of-day spread model.
        
        Args:
            base_spread_bps: Base spread during normal hours
            overnight_multiplier: Spread multiplier during overnight (8PM-6AM ET)
            lunch_multiplier: Spread multiplier during lunch (12-2PM ET)
            open_close_multiplier: Spread multiplier at open/close (high liquidity)
            min_spread_bps: Minimum spread
            max_spread_bps: Maximum spread
        """
        self.base_spread_bps = base_spread_bps
        self.overnight_multiplier = overnight_multiplier
        self.lunch_multiplier = lunch_multiplier
        self.open_close_multiplier = open_close_multiplier
        self.min_spread_bps = min_spread_bps
        self.max_spread_bps = max_spread_bps
    
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """Calculate time-of-day adjusted spread."""
        timestamp = kwargs.get('timestamp')
        if timestamp is None:
            # Default to base spread if no timestamp provided
            return self.base_spread_bps
        
        hour = timestamp.hour
        minute = timestamp.minute
        time_decimal = hour + minute / 60.0
        
        # Determine session multiplier
        if 9.5 <= time_decimal <= 10.5 or 15.5 <= time_decimal <= 16.0:
            # Market open/close - high liquidity
            multiplier = self.open_close_multiplier
        elif 12.0 <= time_decimal <= 14.0:
            # Lunch period - reduced liquidity  
            multiplier = self.lunch_multiplier
        elif time_decimal >= 20.0 or time_decimal <= 6.0:
            # Overnight - low liquidity
            multiplier = self.overnight_multiplier
        else:
            # Normal trading hours
            multiplier = 1.0
        
        spread = self.base_spread_bps * multiplier
        
        # Apply bounds
        spread = max(min(spread, self.max_spread_bps), self.min_spread_bps)
        
        return spread


class CustomSpreadModel(BaseSpreadModel):
    """
    Custom spread model using user-provided function.
    
    Allows complete customization of spread calculation logic.
    """
    
    def __init__(
        self,
        spread_function: Callable[[float, float, float], float],
        min_spread_bps: float = 0.1,
        max_spread_bps: float = 1000.0
    ):
        """
        Initialize custom spread model.
        
        Args:
            spread_function: Function that takes (mid_price, volatility, volume) and returns spread in bp
            min_spread_bps: Minimum allowed spread
            max_spread_bps: Maximum allowed spread
        """
        if not callable(spread_function):
            raise ValueError("spread_function must be callable")
        
        self.spread_function = spread_function
        self.min_spread_bps = min_spread_bps
        self.max_spread_bps = max_spread_bps
    
    def calculate_spread(self, mid_price: float, volatility: float, volume: float, **kwargs) -> float:
        """Calculate spread using custom function."""
        try:
            spread = self.spread_function(mid_price, volatility, volume)
            
            # Apply bounds
            spread = max(min(float(spread), self.max_spread_bps), self.min_spread_bps)
            
            return spread
        except Exception as e:
            raise ValueError(f"Custom spread function failed: {e}")


def get_spread_model(model_name: str, **kwargs) -> BaseSpreadModel:
    """
    Factory function to create spread models by name.
    
    Args:
        model_name: Name of the spread model
        **kwargs: Parameters for the specific model
    
    Returns:
        Initialized spread model instance
    """
    model_map = {
        'constant': ConstantSpreadModel,
        'volatility': VolatilityLinkedSpreadModel,
        'volume': VolumeLinkedSpreadModel,
        'volatility_volume': VolatilityVolumeSpreadModel,
        'time_of_day': TimeOfDaySpreadModel,
        'imbalance': ImbalanceAdjustedSpreadModel,
        'custom': CustomSpreadModel,
    }
    
    if model_name not in model_map:
        available = ', '.join(model_map.keys())
        raise ValueError(f"Unknown spread model '{model_name}'. Available: {available}")
    
    return model_map[model_name](**kwargs)