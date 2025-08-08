# date_utils.py

from datetime import datetime, timedelta, date
from typing import Tuple

class DateRangeUtils:
    """Utility class for handling date range calculations."""
    
    @staticmethod
    def get_week_range(reference_date: date = None) -> Tuple[date, date]:
        """
        Get date range for current week (Sunday to Saturday).
        
        Args:
            reference_date: Reference date (defaults to today)
            
        Returns:
            Tuple of (start_date, end_date)
        """
        if reference_date is None:
            reference_date = date.today()
        
        # Start on Sunday
        start = reference_date - timedelta(days=reference_date.weekday() + 1) if reference_date.weekday() != 6 else reference_date
        end = start + timedelta(days=6)
        return start, end

    @staticmethod
    def get_month_range(reference_date: date = None) -> Tuple[date, date]:
        """
        Get date range for current month.
        
        Args:
            reference_date: Reference date (defaults to today)
            
        Returns:
            Tuple of (start_date, end_date)
        """
        if reference_date is None:
            reference_date = date.today()
            
        start = reference_date.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)
        return start, end

    @staticmethod
    def validate_custom_range(start_date: date, end_date: date) -> Tuple[date, date]:
        """
        Validate and return custom date range.
        
        Args:
            start_date: Custom start date
            end_date: Custom end date
            
        Returns:
            Tuple of (start_date, end_date)
            
        Raises:
            ValueError: If start_date is after end_date
        """
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        return start_date, end_date

    @staticmethod
    def dates_to_iso_range(start_date: date, end_date: date) -> Tuple[str, str]:
        """
        Convert date range to ISO format strings for API calls.
        
        Args:
            start_date: Start date
            end_date: End date (inclusive)
            
        Returns:
            Tuple of (time_min, time_max) in ISO format with 'Z' suffix
        """
        time_min = datetime.combine(start_date, datetime.min.time()).isoformat() + 'Z'
        time_max = datetime.combine(end_date + timedelta(days=1), datetime.min.time()).isoformat() + 'Z'
        return time_min, time_max
