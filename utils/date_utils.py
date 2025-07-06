"""
Date utility functions for conversation parsing and organization.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import calendar


class DateUtils:
    """Utility class for date-related operations in conversation parsing."""
    
    def __init__(self):
        """Initialize the date utilities."""
        pass
    
    def get_week_info(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Get comprehensive week information for a given timestamp.
        
        Args:
            timestamp (datetime): The timestamp to analyze
            
        Returns:
            Dict[str, Any]: Week information including dates, numbers, and formatting data
        """
        # Get the start of the week (Sunday)
        days_since_sunday = (timestamp.weekday() + 1) % 7
        week_start = timestamp.date() - timedelta(days=days_since_sunday)
        week_end = week_start + timedelta(days=6)
        
        # Get week number in month
        first_day_of_month = timestamp.replace(day=1).date()
        first_sunday = first_day_of_month - timedelta(days=(first_day_of_month.weekday() + 1) % 7)
        
        # Calculate which week of the month this is
        weeks_since_first_sunday = (week_start - first_sunday).days // 7
        week_in_month = weeks_since_first_sunday + 1
        
        # Adjust if the week starts before the month
        if week_start < first_day_of_month:
            # This week spans across months, determine which month it belongs to
            if (week_end - first_day_of_month).days >= 3:
                # More days in current month, belongs to current month
                week_in_month = 1
            else:
                # More days in previous month, belongs to previous month
                prev_month_date = first_day_of_month - timedelta(days=1)
                return self.get_week_info(datetime.combine(prev_month_date, timestamp.time()))
        
        return {
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'year': timestamp.year,
            'month': timestamp.month,
            'month_name': calendar.month_name[timestamp.month],
            'week_in_month': week_in_month,
            'week_of_year': timestamp.isocalendar()[1],
            'day_of_year': timestamp.timetuple().tm_yday
        }
    
    def get_week_folder_name(self, week_info: Dict[str, Any], global_week_number: int) -> str:
        """
        Generate a standardized folder name for a week.
        
        Args:
            week_info (Dict[str, Any]): Week information from get_week_info
            global_week_number (int): Global sequential week number
            
        Returns:
            str: Formatted folder name
        """
        year = week_info['year']
        month_name = week_info['month_name']
        week_in_month = week_info['week_in_month']
        week_start = week_info['week_start']
        week_end = week_info['week_end']
        
        return f"{global_week_number}. {year} {month_name} Week {week_in_month} ({week_start} to {week_end})"
    
    def parse_date_range(self, start_date_str: str, end_date_str: str = None) -> Dict[str, Any]:
        """
        Parse date range and return useful information.
        
        Args:
            start_date_str (str): Start date string
            end_date_str (str, optional): End date string
            
        Returns:
            Dict[str, Any]: Date range information
        """
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')) if end_date_str else start_date
            
            duration = end_date - start_date
            
            return {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'duration_days': duration.days,
                'duration_hours': duration.total_seconds() / 3600,
                'same_day': start_date.date() == end_date.date(),
                'spans_weeks': self._spans_multiple_weeks(start_date, end_date),
                'spans_months': start_date.month != end_date.month or start_date.year != end_date.year
            }
        except (ValueError, TypeError) as e:
            return {
                'error': f"Could not parse date range: {e}",
                'start_date': start_date_str,
                'end_date': end_date_str
            }
    
    def _spans_multiple_weeks(self, start_date: datetime, end_date: datetime) -> bool:
        """Check if a date range spans multiple weeks."""
        # Get week start for both dates
        start_week_start = self._get_week_start(start_date)
        end_week_start = self._get_week_start(end_date)
        
        return start_week_start != end_week_start
    
    def _get_week_start(self, timestamp: datetime) -> datetime:
        """Get the start of the week (Sunday) for a given timestamp."""
        days_since_sunday = (timestamp.weekday() + 1) % 7
        return timestamp - timedelta(days=days_since_sunday)
    
    def get_time_period_classification(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Classify a timestamp into various time periods.
        
        Args:
            timestamp (datetime): The timestamp to classify
            
        Returns:
            Dict[str, Any]: Time period classifications
        """
        hour = timestamp.hour
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        
        # Time of day classification
        if 5 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        # Day type classification
        is_weekend = day_of_week >= 5
        day_type = 'weekend' if is_weekend else 'weekday'
        
        # Day name
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = day_names[day_of_week]
        
        return {
            'hour': hour,
            'time_of_day': time_of_day,
            'day_of_week': day_of_week,
            'day_name': day_name,
            'day_type': day_type,
            'is_weekend': is_weekend,
            'timestamp_iso': timestamp.isoformat()
        }
    
    def calculate_week_boundaries(self, year: int, month: int) -> Dict[int, Dict[str, str]]:
        """
        Calculate all week boundaries for a given month.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            Dict[int, Dict[str, str]]: Week boundaries indexed by week number
        """
        # Get first and last day of month
        first_day = datetime(year, month, 1).date()
        if month == 12:
            last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Find first Sunday of or before the month
        first_sunday = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
        
        weeks = {}
        week_num = 1
        current_start = first_sunday
        
        while current_start <= last_day:
            week_end = current_start + timedelta(days=6)
            
            # Only include weeks that have at least one day in the target month
            if week_end >= first_day and current_start <= last_day:
                weeks[week_num] = {
                    'start': current_start.isoformat(),
                    'end': week_end.isoformat(),
                    'overlaps_month': current_start <= last_day and week_end >= first_day
                }
                week_num += 1
            
            current_start += timedelta(days=7)
        
        return weeks
