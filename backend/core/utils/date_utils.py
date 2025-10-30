"""
Date utilities using QuantLib for market conventions.

This module provides utilities for date handling with proper market conventions:
- Day count conventions (ACT/360, ACT/365, 30/360, etc.)
- Business day conventions (Following, Modified Following, etc.)
- Calendar adjustments (TARGET, US, UK, etc.)
"""

from datetime import date, datetime
from typing import Literal, Optional
import QuantLib as ql


# Type aliases for clarity
DayCountConvention = Literal[
    "ACT/360",
    "ACT/365",
    "ACT/ACT",
    "30/360",
    "30E/360",
    "BUS/252"
]

BusinessDayConvention = Literal[
    "Following",
    "ModifiedFollowing",
    "Preceding",
    "ModifiedPreceding",
    "Unadjusted"
]

CalendarType = Literal[
    "TARGET",  # European Central Bank
    "UnitedStates",
    "UnitedKingdom",
    "Japan",
    "NullCalendar"
]


class DateUtils:
    """Utility class for date operations with QuantLib."""
    
    # Mapping Python strings to QuantLib day count conventions
    DAY_COUNT_MAP = {
        "ACT/360": ql.Actual360(),
        "ACT/365": ql.Actual365Fixed(),
        "ACT/ACT": ql.ActualActual(ql.ActualActual.ISDA),
        "30/360": ql.Thirty360(ql.Thirty360.BondBasis),
        "30E/360": ql.Thirty360(ql.Thirty360.European),
        "BUS/252": ql.Business252()
    }
    
    # Mapping Python strings to QuantLib business day conventions
    BDC_MAP = {
        "Following": ql.Following,
        "ModifiedFollowing": ql.ModifiedFollowing,
        "Preceding": ql.Preceding,
        "ModifiedPreceding": ql.ModifiedPreceding,
        "Unadjusted": ql.Unadjusted
    }
    
    # Mapping Python strings to QuantLib calendars
    CALENDAR_MAP = {
        "TARGET": ql.TARGET(),
        "UnitedStates": ql.UnitedStates(ql.UnitedStates.NYSE),
        "UnitedKingdom": ql.UnitedKingdom(),
        "Japan": ql.Japan(),
        "NullCalendar": ql.NullCalendar()
    }
    
    @staticmethod
    def to_ql_date(py_date: date) -> ql.Date:
        """
        Convert Python date to QuantLib Date.
        
        Args:
            py_date: Python date object
            
        Returns:
            QuantLib Date object
            
        Example:
            >>> from datetime import date
            >>> py_date = date(2024, 12, 31)
            >>> ql_date = DateUtils.to_ql_date(py_date)
        """
        return ql.Date(py_date.day, py_date.month, py_date.year)
    
    @staticmethod
    def from_ql_date(ql_date: ql.Date) -> date:
        """
        Convert QuantLib Date to Python date.
        
        Args:
            ql_date: QuantLib Date object
            
        Returns:
            Python date object
        """
        return date(ql_date.year(), ql_date.month(), ql_date.dayOfMonth())
    
    @staticmethod
    def year_fraction(
        start_date: date,
        end_date: date,
        day_count: DayCountConvention = "ACT/365"
    ) -> float:
        """
        Calculate year fraction between two dates using specified day count convention.
        
        Args:
            start_date: Start date
            end_date: End date
            day_count: Day count convention
            
        Returns:
            Year fraction as float
            
        Example:
            >>> start = date(2024, 1, 1)
            >>> end = date(2025, 1, 1)
            >>> yf = DateUtils.year_fraction(start, end, "ACT/365")
            >>> # yf ≈ 1.0
        """
        ql_start = DateUtils.to_ql_date(start_date)
        ql_end = DateUtils.to_ql_date(end_date)
        dc = DateUtils.DAY_COUNT_MAP[day_count]
        
        return dc.yearFraction(ql_start, ql_end)
    
    @staticmethod
    def adjust_date(
        input_date: date,
        calendar: CalendarType = "TARGET",
        convention: BusinessDayConvention = "Following"
    ) -> date:
        """
        Adjust a date according to business day convention and calendar.
        
        Args:
            input_date: Date to adjust
            calendar: Calendar to use for holidays
            convention: Business day convention
            
        Returns:
            Adjusted date
            
        Example:
            >>> # If Dec 25, 2024 is a holiday
            >>> input_date = date(2024, 12, 25)
            >>> adjusted = DateUtils.adjust_date(input_date, "TARGET", "Following")
            >>> # adjusted will be Dec 26, 2024
        """
        ql_date = DateUtils.to_ql_date(input_date)
        cal = DateUtils.CALENDAR_MAP[calendar]
        bdc = DateUtils.BDC_MAP[convention]
        
        adjusted_ql_date = cal.adjust(ql_date, bdc)
        return DateUtils.from_ql_date(adjusted_ql_date)
    
    @staticmethod
    def is_business_day(
        check_date: date,
        calendar: CalendarType = "TARGET"
    ) -> bool:
        """
        Check if a date is a business day.
        
        Args:
            check_date: Date to check
            calendar: Calendar to use
            
        Returns:
            True if business day, False otherwise
        """
        ql_date = DateUtils.to_ql_date(check_date)
        cal = DateUtils.CALENDAR_MAP[calendar]
        
        return cal.isBusinessDay(ql_date)
    
    @staticmethod
    def add_business_days(
        start_date: date,
        num_days: int,
        calendar: CalendarType = "TARGET"
    ) -> date:
        """
        Add business days to a date.
        
        Args:
            start_date: Starting date
            num_days: Number of business days to add
            calendar: Calendar to use
            
        Returns:
            New date after adding business days
            
        Example:
            >>> start = date(2024, 1, 1)
            >>> new_date = DateUtils.add_business_days(start, 5, "TARGET")
        """
        ql_date = DateUtils.to_ql_date(start_date)
        cal = DateUtils.CALENDAR_MAP[calendar]
        
        new_ql_date = cal.advance(ql_date, ql.Period(num_days, ql.Days))
        return DateUtils.from_ql_date(new_ql_date)
    
    @staticmethod
    def business_days_between(
        start_date: date,
        end_date: date,
        calendar: CalendarType = "TARGET"
    ) -> int:
        """
        Calculate number of business days between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
            calendar: Calendar to use
            
        Returns:
            Number of business days
        """
        ql_start = DateUtils.to_ql_date(start_date)
        ql_end = DateUtils.to_ql_date(end_date)
        cal = DateUtils.CALENDAR_MAP[calendar]
        
        return cal.businessDaysBetween(ql_start, ql_end)


def calculate_time_to_maturity(
    trade_date: date,
    maturity_date: date,
    day_count: DayCountConvention = "ACT/365",
    calendar: CalendarType = "TARGET",
    business_day_convention: BusinessDayConvention = "Following"
) -> float:
    """
    Calculate time to maturity with market conventions.
    
    This is the main function to use for calculating time to maturity
    in option pricing and other derivatives.
    
    Args:
        trade_date: Trade/valuation date
        maturity_date: Maturity/expiry date
        day_count: Day count convention
        calendar: Calendar for business day adjustments
        business_day_convention: How to adjust non-business days
        
    Returns:
        Time to maturity in years (as float)
        
    Example:
        >>> from datetime import date
        >>> trade_date = date(2024, 1, 15)
        >>> maturity_date = date(2025, 1, 15)
        >>> T = calculate_time_to_maturity(
        ...     trade_date,
        ...     maturity_date,
        ...     day_count="ACT/365",
        ...     calendar="TARGET"
        ... )
        >>> # T ≈ 1.0
    """
    # Adjust dates if they fall on non-business days
    adjusted_trade = DateUtils.adjust_date(
        trade_date,
        calendar,
        business_day_convention
    )
    adjusted_maturity = DateUtils.adjust_date(
        maturity_date,
        calendar,
        business_day_convention
    )
    
    # Calculate year fraction
    return DateUtils.year_fraction(
        adjusted_trade,
        adjusted_maturity,
        day_count
    )


# Convenience function for backwards compatibility
def date_to_maturity(trade_date: date, maturity_date: date) -> float:
    """
    Simple conversion from dates to maturity (ACT/365, no adjustments).
    
    For backwards compatibility with existing code.
    """
    return DateUtils.year_fraction(trade_date, maturity_date, "ACT/365")
