 """Core functionality for fetching fund data from Fipiran API."""

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor
from .utils import jalali_to_gregorian, validate_jalali_date, get_desktop_path


class FundDataFetcher:
    """Main class for fetching fund transaction data."""
    
    def __init__(self, max_workers=8, timeout=15, request_delay=0.5, retry_attempts=3):
        self.max_workers = max_workers
        self.timeout = timeout
        self.request_delay = request_delay
        self.retry_attempts = retry_attempts
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_fund_data(self, regno, date_str):
        """Fetch fund data for a specific regno and date."""
        url = f"https://api.fipiran.com/api/v1/fund/{regno}/nav/{date_str}"
        
        for attempt in range(self.retry_attempts):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return data[0]
                time.sleep(self.request_delay)
            except Exception:
                if attempt == self.retry_attempts - 1:
                    return None
                time.sleep(1)
        return None
    
    def generate_date_range(self, start_date, end_date):
        """Generate list of dates between start and end date."""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        return dates


def export_fund_data(start_jalali, end_jalali, regnos=None, output_filename=None):
    """Export fund data to CSV file on desktop."""
    
    if not validate_jalali_date(start_jalali):
        raise ValueError(f"Invalid start date format: {start_jalali}")
    if not validate_jalali_date(end_jalali):
        raise ValueError(f"Invalid end date format: {end_jalali}")
    
    start_gregorian = jalali_to_gregorian(start_jalali)
    end_gregorian = jalali_to_gregorian(end_jalali)
    
    if regnos is None:
        regnos = [11098, 11099, 11100]
    
    fetcher = FundDataFetcher()
    dates = fetcher.generate_date_range(start_gregorian, end_gregorian)
    
    all_data = []
    success_count = 0
    failed_count = 0
    
    print(f"Starting data export for {len(regnos)} funds from {start_jalali} to {end_jalali}")
    print(f"Total API calls: {len(regnos) * len(dates)}")
    
    with ThreadPoolExecutor(max_workers=fetcher.max_workers) as executor:
        futures = []
        
        for regno in regnos:
            for date in dates:
                future = executor.submit(fetcher.fetch_fund_data, regno, date)
                futures.append((future, regno, date))
        
        for future, regno, date in futures:
            try:
                result = future.result()
                if result:
                    result['regno'] = regno
                    result['fetch_date'] = date
                    all_data.append(result)
                    success_count += 1
                else:
                    failed_count += 1
            except Exception:
                failed_count += 1
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"fund_data_{start_jalali.replace('/', '')}_{end_jalali.replace('/', '')}_{timestamp}.csv"
        
        desktop_path = get_desktop_path()
        file_path = os.path.join(desktop_path, output_filename)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        print(f"\nExport completed!")
        print(f"Success: {success_count}, Failed: {failed_count}")
        print(f"File saved: {file_path}")
        print(f"Total records: {len(all_data)}")
        
        return file_path
    else:
        print("No data was fetched successfully.")
        return None
