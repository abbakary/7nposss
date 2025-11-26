"""
Time utilities for calculating order duration and overdue status.
Overdue threshold: 9 calendar hours (simple calculation).
"""

from datetime import datetime, timedelta
from django.utils import timezone


# Simple overdue threshold: 9 calendar hours
OVERDUE_THRESHOLD_HOURS = 9


def calculate_estimated_duration(started_at: datetime, completed_at: datetime) -> int | None:
    """
    Calculate estimated duration in minutes from started_at to completed_at.
    Uses working hours calculation (8 AM - 5 PM).
    
    Args:
        started_at: Order start datetime
        completed_at: Order completion datetime
        
    Returns:
        Estimated duration in minutes (int), or None if dates are invalid
    """
    if not started_at or not completed_at:
        return None
    
    working_hours = calculate_working_hours_between(started_at, completed_at)
    if working_hours <= 0:
        return None
    
    # Convert hours to minutes
    minutes = int(working_hours * 60)
    return minutes


def is_order_overdue(started_at: datetime, now: datetime = None) -> bool:
    """
    Check if an in-progress order has exceeded the 9-hour working hour threshold.
    
    Args:
        started_at: Order start datetime
        now: Current datetime (defaults to timezone.now())
        
    Returns:
        True if order has been in progress for 9+ working hours, False otherwise
    """
    if not started_at:
        return False
    
    if now is None:
        now = timezone.now()
    
    # Calculate working hours elapsed
    working_hours_elapsed = calculate_working_hours_between(started_at, now)
    
    return working_hours_elapsed >= OVERDUE_THRESHOLD_HOURS


def get_order_overdue_status(order) -> dict:
    """
    Get the overdue status of an order.
    
    Args:
        order: Order instance
        
    Returns:
        Dictionary with:
        - is_overdue (bool): Whether the order is overdue
        - working_hours_elapsed (float): Working hours since start
        - overdue_hours (float): How many hours over the threshold (0 if not overdue)
    """
    result = {
        'is_overdue': False,
        'working_hours_elapsed': 0.0,
        'overdue_hours': 0.0,
    }
    
    if not order.started_at:
        return result
    
    now = timezone.now()
    working_hours = calculate_working_hours_between(order.started_at, now)
    result['working_hours_elapsed'] = round(working_hours, 2)
    
    if working_hours >= OVERDUE_THRESHOLD_HOURS:
        result['is_overdue'] = True
        result['overdue_hours'] = round(working_hours - OVERDUE_THRESHOLD_HOURS, 2)
    
    return result


def format_working_hours(hours: float) -> str:
    """
    Format working hours as a human-readable string.
    
    Args:
        hours: Number of working hours (float)
        
    Returns:
        Formatted string like "9h 30m" or "2h 15m"
    """
    if hours < 0:
        return "0h"
    
    total_minutes = int(hours * 60)
    hours_part = total_minutes // 60
    minutes_part = total_minutes % 60
    
    if hours_part == 0 and minutes_part == 0:
        return "0h"
    elif hours_part == 0:
        return f"{minutes_part}m"
    elif minutes_part == 0:
        return f"{hours_part}h"
    else:
        return f"{hours_part}h {minutes_part}m"


def estimate_completion_time(started_at: datetime, estimated_minutes: int = None) -> dict:
    """
    Estimate the completion time based on start time and estimated duration.
    
    Args:
        started_at: Order start datetime
        estimated_minutes: Estimated duration in minutes (defaults to 9 hours)
        
    Returns:
        Dictionary with:
        - estimated_end (datetime): Estimated completion datetime
        - estimated_hours (float): Estimated duration in hours
        - formatted (str): Human-readable format
    """
    if not started_at:
        return None
    
    if estimated_minutes is None:
        estimated_minutes = OVERDUE_THRESHOLD_HOURS * 60
    
    estimated_hours = estimated_minutes / 60.0
    
    # Simple approximation: add estimated hours to start time
    # In reality, we'd need to account for working hours cutoff
    estimated_end = started_at + timedelta(hours=estimated_hours)
    
    return {
        'estimated_end': estimated_end,
        'estimated_hours': estimated_hours,
        'formatted': format_working_hours(estimated_hours),
    }
