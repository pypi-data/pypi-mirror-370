"""Data mapping and transformation functions."""

def map_fund_data(raw_data):
    """Map raw API data to standardized format."""
    if not raw_data:
        return None
    
    mapped = {
        'regno': raw_data.get('regno'),
        'fetch_date': raw_data.get('fetch_date'),
        'nav': raw_data.get('nav'),
        'total_value': raw_data.get('totalValue'),
        'estimated_earning': raw_data.get('estimatedEarning'),
        'date': raw_data.get('date')
    }
    
    return mapped
