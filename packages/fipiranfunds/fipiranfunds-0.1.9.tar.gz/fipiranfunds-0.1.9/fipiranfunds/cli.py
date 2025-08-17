"""Command line interface for fipiranfunds."""

import sys
from .core import export_fund_data


def main():
    """Main CLI function."""
    print("Fipiran Funds Data Exporter")
    print("=" * 30)
    
    try:
        start_date = input("Enter start date (Jalali YYYY/MM/DD): ").strip()
        end_date = input("Enter end date (Jalali YYYY/MM/DD): ").strip()
        
        regnos_input = input("Enter registration numbers separated by comma (or press Enter for default): ").strip()
        
        if regnos_input:
            regnos = [int(x.strip()) for x in regnos_input.split(',')]
        else:
            regnos = None
        
        result = export_fund_data(start_date, end_date, regnos)
        
        if result:
            print(f"\nData successfully exported to: {result}")
        else:
            print("\nNo data was exported.")
            
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
