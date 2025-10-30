"""
Converter for pricing requests with market conventions support.

This module converts API requests (with dates and market conventions)
into internal pricing objects with properly calculated time to maturity.
"""

from datetime import date
from typing import Tuple
from backend.schemas.trade_schemas import (
    PricingRequestSchema,
    TradeSchema,
    MarketConventionsSchema
)
from backend.core.products.option import Option
from backend.core.products.base_product import OptionType, ExerciseType
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.utils.date_utils import calculate_time_to_maturity


class PricingRequestConverter:
    """
    Converter for pricing requests with proper date handling.
    
    This converter:
    1. Extracts dates from the trade
    2. Applies market conventions (day count, business day adjustments, calendar)
    3. Calculates time to maturity
    4. Creates the appropriate product and model objects
    """
    
    @staticmethod
    def extract_dates(
        request: PricingRequestSchema
    ) -> Tuple[date, date]:
        """
        Extract trade date and expiration date from request.
        
        Args:
            request: Pricing request schema
            
        Returns:
            Tuple of (valuation_date, expiration_date)
            
        Raises:
            ValueError: If dates are missing or invalid
        """
        # Valuation date: use provided or default to trade_date
        valuation_date = request.valuation_date or request.trade.trade_date
        
        # Expiration date from the option
        if request.trade.product_type == "Option" and request.trade.option:
            expiration_date = request.trade.option.expiration_date
        else:
            raise ValueError(
                f"Cannot extract expiration date for product_type={request.trade.product_type}"
            )
        
        # Validate dates
        if expiration_date <= valuation_date:
            raise ValueError(
                f"Expiration date ({expiration_date}) must be after "
                f"valuation date ({valuation_date})"
            )
        
        return valuation_date, expiration_date
    
    @staticmethod
    def calculate_maturity(
        request: PricingRequestSchema
    ) -> float:
        """
        Calculate time to maturity using market conventions.
        
        Args:
            request: Pricing request schema
            
        Returns:
            Time to maturity in years (float)
            
        Example:
            >>> request = PricingRequestSchema(...)
            >>> T = PricingRequestConverter.calculate_maturity(request)
            >>> # T calculated with ACT/365 and business day adjustments
        """
        valuation_date, expiration_date = PricingRequestConverter.extract_dates(request)
        conventions = request.market_conventions
        
        # Calculate time to maturity with market conventions
        time_to_maturity = calculate_time_to_maturity(
            trade_date=valuation_date,
            maturity_date=expiration_date,
            day_count=conventions.day_count_convention.value,
            calendar=conventions.calendar.value,
            business_day_convention=conventions.business_day_convention.value
        )
        
        return time_to_maturity
    
    @staticmethod
    def create_option(
        request: PricingRequestSchema,
        time_to_maturity: float
    ) -> Option:
        """
        Create an option product from request.
        
        Args:
            request: Pricing request schema
            time_to_maturity: Already calculated time to maturity
            
        Returns:
            Option instance
            
        Raises:
            ValueError: If option data is missing or invalid
        """
        if not request.trade.option:
            raise ValueError("Option data is missing in trade")
        
        option_data = request.trade.option
        
        # Convert option type string to enum
        option_type = OptionType.CALL if option_data.option_type == "Call" else OptionType.PUT
        
        # Convert exercise type string to enum
        exercise_type_map = {
            "European": ExerciseType.EUROPEAN,
            "American": ExerciseType.AMERICAN,
            "Bermudan": ExerciseType.BERMUDAN
        }
        exercise_type = exercise_type_map.get(
            option_data.exercise_type, 
            ExerciseType.EUROPEAN
        )
        
        return Option(
            strike=option_data.strike,
            maturity=time_to_maturity,  # Using calculated maturity with conventions
            option_type=option_type,
            exercise_type=exercise_type,
            notional=option_data.notional.amount if option_data.notional else 1.0
        )
    
    @staticmethod
    def create_model(
        request: PricingRequestSchema
    ) -> BlackScholesModel:
        """
        Create a pricing model from request.
        
        Args:
            request: Pricing request schema
            
        Returns:
            Model instance (currently only BlackScholesModel)
            
        Raises:
            ValueError: If model parameters are missing
        """
        if request.model_type == "BlackScholes":
            if request.volatility is None or request.risk_free_rate is None:
                raise ValueError(
                    "volatility and risk_free_rate are required for BlackScholes model"
                )
            
            return BlackScholesModel(
                volatility=request.volatility,
                risk_free_rate=request.risk_free_rate,
                dividend_yield=request.dividend_yield or 0.0
            )
        
        # TODO: Add Heston, SABR, etc.
        raise ValueError(f"Unsupported model type: {request.model_type}")
    
    @staticmethod
    def convert(
        request: PricingRequestSchema
    ) -> Tuple[Option, BlackScholesModel, float]:
        """
        Main conversion method: request → (product, model, maturity).
        
        This method orchestrates the full conversion:
        1. Calculate time to maturity with market conventions
        2. Create the option product
        3. Create the pricing model
        
        Args:
            request: Pricing request schema
            
        Returns:
            Tuple of (option, model, time_to_maturity)
            
        Example:
            >>> request = PricingRequestSchema(...)
            >>> option, model, T = PricingRequestConverter.convert(request)
            >>> # Now ready for pricing
        """
        # Calculate time to maturity with conventions
        time_to_maturity = PricingRequestConverter.calculate_maturity(request)
        
        # Create product and model
        option = PricingRequestConverter.create_option(request, time_to_maturity)
        model = PricingRequestConverter.create_model(request)
        
        return option, model, time_to_maturity


def get_pricing_objects(
    request: PricingRequestSchema
) -> Tuple[Option, BlackScholesModel, float, date, date]:
    """
    Convenience function to get all pricing objects from a request.
    
    Args:
        request: Pricing request schema
        
    Returns:
        Tuple of (option, model, time_to_maturity, valuation_date, expiration_date)
    """
    converter = PricingRequestConverter()
    
    # Get dates
    valuation_date, expiration_date = converter.extract_dates(request)
    
    # Get pricing objects
    option, model, time_to_maturity = converter.convert(request)
    
    return option, model, time_to_maturity, valuation_date, expiration_date
