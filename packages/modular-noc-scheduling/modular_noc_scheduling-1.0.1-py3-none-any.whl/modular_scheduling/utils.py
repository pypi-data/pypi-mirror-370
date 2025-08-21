"""
Utility functions for NOC Scheduling Algorithm.

This module contains helper functions for date calculations, holiday processing,
and other utility operations used throughout the scheduling system.
"""

import datetime
from datetime import timedelta
from calendar import monthrange
from hijri_converter import convert
from typing import List, Tuple


def get_all_days(year: int) -> List[datetime.date]:
    """
    Generate all days in a given Gregorian year.
    
    Args:
        year: The Gregorian year
        
    Returns:
        List of datetime.date objects for every day in the year
    """
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += datetime.timedelta(days=1)
    return days


def get_specific_month_days(year: int, month: int) -> List[datetime.date]:
    """
    Generate all days in a specific month and year.
    
    Args:
        year: The Gregorian year
        month: The month (1-12)
        
    Returns:
        List of datetime.date objects for every day in the specified month
    """
    num_of_days = monthrange(year, month)[1]
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, num_of_days)
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += datetime.timedelta(days=1)
    return days


def get_weekends(month_days: List[datetime.date]) -> List[datetime.date]:
    """
    Extract weekend days from a list of dates.
    
    In this system, Friday (4) and Saturday (5) are considered weekends
    following the regional work week convention.
    
    Args:
        month_days: List of datetime.date objects
        
    Returns:
        List of weekend dates (Fridays and Saturdays)
    """
    weekends = []
    for day in month_days:
        # Friday (4) and Saturday (5) are weekend days in this region
        if day.weekday() == 4 or day.weekday() == 5:
            weekends.append(day)
    return weekends


def get_ramadan_days(hijri_year: int) -> Tuple[List[datetime.date], set]:
    """
    Calculate Ramadan dates for a given Hijri year.
    
    Ramadan is the 9th month in the Islamic calendar and requires special
    shift scheduling due to altered work patterns and religious observances.
    
    Args:
        hijri_year: The Hijri (Islamic) year
        
    Returns:
        Tuple containing:
        - List of Gregorian dates during Ramadan
        - Set of Gregorian month names that Ramadan spans
    """
    hijri_start = convert.Hijri(hijri_year, 9, 1)
    ramadan_start_gregorian = hijri_start.to_gregorian()
    ramadan_days = []
    for i in range(30):
        day = ramadan_start_gregorian + timedelta(days=i)
        ramadan_days.append(day)
    gregorian_months = {day.strftime('%B') for day in ramadan_days}
    return ramadan_days, gregorian_months


def get_day_type(day: datetime.date, weekends: List[datetime.date], holidays: List[datetime.date], ramadan_days: List[datetime.date]) -> str:
    """
    Classify a given day into one of four categories for scheduling purposes.
    
    Args:
        day: The date to classify
        weekends: List of weekend dates
        holidays: List of holiday dates
        ramadan_days: List of dates during Ramadan
        
    Returns:
        String classification: 'HOLIDAY', 'WEEKEND', 'RAMADAN', or 'WEEKDAY'
    """
    if day in holidays:
        return 'HOLIDAY'
    elif day in weekends:
        return 'WEEKEND'
    elif day in ramadan_days:
        return 'RAMADAN'
    else:
        return 'WEEKDAY'


def upload_all_holidays(year: int, holidays_file_path: str) -> List[datetime.date]:
    """
    Parse holidays from a text file and convert to datetime objects.
    
    Expected file format: Each line contains "day; month; description"
    Lines starting with 'day' are treated as headers and skipped.
    
    Args:
        year: The Gregorian year for holiday dates
        holidays_file_path: Path to the holidays text file
        
    Returns:
        List of datetime.date objects representing holidays
    """
    holidays = []
    try:
        with open(holidays_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('day'):
                    continue
                parts = line.split(';')
                if len(parts) < 2:
                    continue
                try:
                    day = int(parts[0].strip())
                    month = int(parts[1].strip())
                    date_obj = datetime.date(year, month, day)
                    holidays.append(date_obj)
                except Exception:
                    continue
    except FileNotFoundError:
        print(f"Holiday file '{holidays_file_path}' not found.")
    return holidays
