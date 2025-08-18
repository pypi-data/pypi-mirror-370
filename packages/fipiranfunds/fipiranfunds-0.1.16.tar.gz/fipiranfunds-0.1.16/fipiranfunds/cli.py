"""Command-line interface for fipiranfunds."""

from .core import export_fund_data
from .utils import validate_jalali_date


def get_valid_jalali_date(prompt):
    """Get a valid Jalali date from user input."""
    while True:
        date_str = input(prompt)
        if validate_jalali_date(date_str):
            return date_str
        print("Error: Invalid date format. Please use YYYY/MM/DD (e.g., 1403/12/01)")


def main():
    """Main CLI function."""
    print("=" * 60)
    print("FIPIRANFUNDS - Fund Data Exporter")
    print("=" * 60)
    
    try:
        # Get date range from user
        start_date = get_valid_jalali_date("Enter start date (YYYY/MM/DD): ")
        end_date = get_valid_jalali_date("Enter end date (YYYY/MM/DD): ")
        
        # Ask if user wants to filter by specific funds
        filter_choice = input("\nFilter by specific fund regNos? (y/n): ").lower()
        regnos = None
        
        if filter_choice == 'y':
            regno_input = input("Enter regNos separated by commas (e.g., 11098,11099): ")
            try:
                regnos = [int(x.strip()) for x in regno_input.split(',')]
                print(f"Will filter for regNos: {regnos}")
            except ValueError:
                print("Invalid regNo format. Proceeding with all funds.")
                regnos = None
        
        # Export data
        print(f"\nStarting export from {start_date} to {end_date}...")
        result = export_fund_data(start_date, end_date, regnos)
        
        if result:
            print(f"\n✅ SUCCESS! Data exported to: {result}")
        else:
            print("\n❌ FAILED: No data was exported")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()