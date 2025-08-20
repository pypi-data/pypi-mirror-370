"""Helper functions for CloudSense"""

from datetime import datetime, timedelta
from typing import Tuple, Union


# Service name mapping for performance
SERVICE_NAMES = {
    'Amazon Elastic Compute Cloud - Compute': 'EC2 - Compute',
    'Amazon Simple Storage Service': 'Amazon S3',
    'Stable Diffusion 3.5 Large v1.0 (Amazon Bedrock Edition)': 'Bedrock: SD 3.5 Large',
    'Claude Opus 4 (Amazon Bedrock Edition)': 'Bedrock: Claude Opus 4',
    'Claude Sonnet 4 (Amazon Bedrock Edition)': 'Bedrock: Claude Sonnet 4',
    'Amazon Virtual Private Cloud': 'VPC',
    'Amazon Elastic File System': 'Amazon EFS',
    'AmazonCloudWatch': 'CloudWatch',
    'Amazon DynamoDB': 'DynamoDB',
    'Amazon Route 53': 'Route53'
}

# Reverse mapping for efficient lookups
REVERSE_SERVICE_NAMES = {v: k for k, v in SERVICE_NAMES.items()}

# EBS category mapping
EBS_CATEGORIES = {
    'VolumeUsage.gp3': 'EBS gp3 Storage',
    'VolumeUsage.io2': 'EBS io2 Storage', 
    'VolumeUsage.piops': 'EBS io1 Storage',
    'VolumeP-IOPS.io2': 'EBS io2 IOPS',
    'VolumeP-IOPS.piops': 'EBS io1 IOPS',
    'SnapshotUsage': 'EBS Snapshots'
}


def normalize_service_name(service: str) -> str:
    """
    Normalize service name using mapping
    
    Args:
        service: Original AWS service name
        
    Returns:
        str: Normalized display name
    """
    return SERVICE_NAMES.get(service, service)


def get_original_service_name(display_name: str) -> str:
    """
    Get original service name from display name
    
    Args:
        display_name: Display name of service
        
    Returns:
        str: Original AWS service name
    """
    return REVERSE_SERVICE_NAMES.get(display_name, display_name)


def categorize_ebs_usage(usage_type: str) -> str:
    """
    Categorize EBS usage type
    
    Args:
        usage_type: AWS usage type string
        
    Returns:
        str: Categorized usage type
    """
    for pattern, category in EBS_CATEGORIES.items():
        if pattern in usage_type:
            return category
    return 'Other EBS'


def parse_date_params(days: Union[int, None] = None, 
                     specific_date: Union[str, None] = None, 
                     month: Union[str, None] = None) -> Tuple[datetime, datetime]:
    """
    Parse and validate date parameters using local time
    
    Args:
        days: Number of days to look back
        specific_date: Specific date in ISO format
        month: Month specification (current, previous, or YYYY-MM)
        
    Returns:
        Tuple[datetime, datetime]: Start date and end date
    """
    local_now = datetime.now()
    
    if specific_date:
        start_date = datetime.fromisoformat(specific_date).date()
        return start_date, start_date + timedelta(days=1)
    elif month:
        if month == 'current':
            today = local_now.date()
            return today.replace(day=1), today + timedelta(days=1)
        elif month == 'previous':
            today = local_now.date()
            start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            return start, today.replace(day=1)
        else:
            year, month_num = month.split('-')
            start = datetime(int(year), int(month_num), 1).date()
            if start.month == 12:
                end = datetime(start.year + 1, 1, 1).date()
            else:
                end = datetime(start.year, start.month + 1, 1).date()
            return start, end
    else:
        end = local_now.date() + timedelta(days=1)
        return end - timedelta(days=(days or 30)+1), end


def format_currency(amount: float) -> str:
    """
    Format currency amount with proper precision
    
    Args:
        amount: Dollar amount to format
        
    Returns:
        str: Formatted currency string
    """
    if amount < 0.01:
        return f"${amount:.4f}"
    elif amount < 1:
        return f"${amount:.3f}"
    else:
        return f"${amount:.2f}"


def calculate_daily_average(total_cost: float, days: int) -> float:
    """
    Calculate daily average cost
    
    Args:
        total_cost: Total cost amount
        days: Number of days
        
    Returns:
        float: Daily average
    """
    if days <= 0:
        return 0.0
    return total_cost / days


def calculate_monthly_projection(daily_avg: float, days_in_month: int = 30) -> float:
    """
    Calculate monthly cost projection
    
    Args:
        daily_avg: Daily average cost
        days_in_month: Number of days to project for
        
    Returns:
        float: Projected monthly cost
    """
    return daily_avg * days_in_month
