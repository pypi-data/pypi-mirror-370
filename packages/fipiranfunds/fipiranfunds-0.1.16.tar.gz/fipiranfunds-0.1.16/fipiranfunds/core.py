"""Core functionality for fetching fund data from Fipiran API."""

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor
import urllib3
from .utils import jalali_to_gregorian, validate_jalali_date, get_desktop_path

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FundDataFetcher:
    """Main class for fetching fund transaction data."""
    
    def __init__(self, max_workers=8, timeout=30, request_delay=1, retry_attempts=3):
        self.max_workers = max_workers
        self.timeout = timeout
        self.request_delay = request_delay
        self.retry_attempts = retry_attempts
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://fund.fipiran.ir/',
            'Origin': 'https://fund.fipiran.ir',
            'Connection': 'keep-alive'
        })
    
    def fetch_fund_data(self, date_str):
        """Fetch fund data for a specific date."""
        url = f"https://fund.fipiran.ir/api/v1/fund/fundcompare?date={date_str}"
        
        for attempt in range(self.retry_attempts):
            try:
                print(f"Fetching data from: {url}")
                response = self.session.get(url, timeout=self.timeout, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and 'items' in data and isinstance(data['items'], list):
                        items = data['items']
                        print(f"Received {len(items)} fund records from API")
                        return items
                    else:
                        print("API response does not contain expected data structure")
                        return None
                else:
                    print(f"API request failed with status code: {response.status_code}")
                    
                time.sleep(self.request_delay)
                
            except Exception as e:
                print(f"API request error (attempt {attempt + 1}): {str(e)}")
                if attempt == self.retry_attempts - 1:
                    return None
                time.sleep(2)
                
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
    
    # Convert datetime objects to strings
    start_gregorian_str = start_gregorian.strftime('%Y-%m-%d')
    end_gregorian_str = end_gregorian.strftime('%Y-%m-%d')
    
    fetcher = FundDataFetcher()
    dates = fetcher.generate_date_range(start_gregorian_str, end_gregorian_str)
    
    all_data = []
    success_count = 0
    failed_count = 0
    
    print(f"Starting data export from {start_jalali} to {end_jalali}")
    print(f"Gregorian dates: {start_gregorian_str} to {end_gregorian_str}")
    print(f"Total dates to process: {len(dates)}")
    
    for i, date_str in enumerate(dates, 1):
        print(f"\nProcessing date {i}/{len(dates)}: {date_str}")
        
        try:
            result = fetcher.fetch_fund_data(date_str)
            if result:
                # Add date info to each record
                for record in result:
                    record['fetch_date'] = date_str
                all_data.extend(result)
                success_count += 1
                print(f"✓ Successfully fetched {len(result)} records for {date_str}")
            else:
                failed_count += 1
                print(f"✗ No data fetched for {date_str}")
                
        except Exception as e:
            failed_count += 1
            print(f"✗ Error fetching data for {date_str}: {str(e)}")
        
        # Add delay between requests
        if i < len(dates):
            time.sleep(1)
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Filter by regnos if specified
        if regnos:
            df = df[df['regNo'].isin(regnos)]
            print(f"Filtered data to {len(df)} records matching specified regNos")
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"fund_data_{start_jalali.replace('/', '')}_{end_jalali.replace('/', '')}_{timestamp}.csv"
        
        desktop_path = get_desktop_path()
        file_path = os.path.join(desktop_path, output_filename)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        print(f"\n" + "="*60)
        print(f"EXPORT COMPLETED!")
        print(f"Success: {success_count} dates, Failed: {failed_count} dates")
        print(f"File saved: {file_path}")
        print(f"Total records: {len(df)}")
        print(f"="*60)
        
        return file_path
    else:
        print("No data was fetched successfully.")
        return None