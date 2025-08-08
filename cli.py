# cli.py

from calendar_logic import CalendarAnalyzer
from date_utils import DateRangeUtils
from visualization import CalendarVisualizer
from datetime import datetime, date
from typing import Tuple, Dict, List

class CalendarTrackerCLI:
    """Command Line Interface for the Calendar Tracker."""
    
    def __init__(self):
        """Initialize the CLI with calendar analyzer and visualizer."""
        self.analyzer = CalendarAnalyzer()
        self.visualizer = CalendarVisualizer()
    
    def display_menu(self) -> str:
        """
        Display the main menu and get user choice.
        
        Returns:
            User's menu choice
        """
        print("Choose analysis mode:")
        print("  1. Week (Sunday–Saturday)")
        print("  2. Month (Calendar month)")
        print("  3. Custom date range")
        choice = input("Enter 1 / 2 / 3: ").strip()
        return choice
    
    def ask_for_visualization(self) -> bool:
        """
        Ask user if they want to see a pie chart.
        
        Returns:
            True if user wants visualization, False otherwise
        """
        while True:
            choice = input("\nWould you like to see a pie chart? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def get_date_range_from_user(self) -> Tuple[str, Tuple[date, date]]:
        """
        Get date range based on user choice.
        
        Returns:
            Tuple of (mode, (start_date, end_date))
        """
        choice = self.display_menu()
        
        if choice == "1":
            mode = "week"
            start_date, end_date = DateRangeUtils.get_week_range()
        elif choice == "2":
            mode = "month"
            start_date, end_date = DateRangeUtils.get_month_range()
        elif choice == "3":
            mode = "custom"
            start_date, end_date = self._get_custom_dates()
        else:
            print("Invalid choice.")
            raise ValueError("Invalid menu choice")
        
        return mode, (start_date, end_date)
    
    def _get_custom_dates(self) -> Tuple[date, date]:
        """
        Get custom date range from user input.
        
        Returns:
            Tuple of (start_date, end_date)
        """
        while True:
            try:
                start_input = input("Enter start date (YYYY-MM-DD): ").strip()
                end_input = input("Enter end date (YYYY-MM-DD): ").strip()
                
                start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_input, "%Y-%m-%d").date()
                
                return DateRangeUtils.validate_custom_range(start_date, end_date)
            
            except ValueError as e:
                print(f"Invalid date format or range: {e}")
                print("Please use YYYY-MM-DD format and ensure start date is before end date.")
    
    def print_report(self, category_time: Dict[str, float], top_titles: Dict[str, List[Tuple[str, float]]], 
                     start_date: date, end_date: date) -> None:
        """
        Print the analysis report to console.
        
        Args:
            category_time: Dictionary of category -> total hours
            top_titles: Dictionary of category -> list of top activities
            start_date: Analysis start date
            end_date: Analysis end date
        """
        print("\n📊 Calendar Summary:")
        print(f"🗓️  From {start_date.strftime('%A, %Y-%m-%d')} to {end_date.strftime('%A, %Y-%m-%d')}\n")

        # Calculate total hours
        total_hours = sum(category_time.values())
        
        # Sort categories by time spent (highest first)
        sorted_categories = sorted(category_time.items(), key=lambda x: -x[1])
        
        for category, hours in sorted_categories:
            # Calculate percentage
            percentage = (hours / total_hours * 100) if total_hours > 0 else 0
            print(f"🔸 {category}: {percentage:.1f}% ({hours:.2f} hours)")
            for title, duration in top_titles[category]:
                print(f"    - {title} ({duration:.2f}h)")
            print()

    def run(self) -> None:
        """
        Main CLI loop - run the complete application.
        """
        try:
            print("🗓️ Welcome to Google Calendar Tracker!\n")
            
            # Get user preferences
            mode, (start_date, end_date) = self.get_date_range_from_user()
            
            print(f"\n🔄 Analyzing {mode} data...")
            
            # Perform analysis
            category_time, top_titles = self.analyzer.analyze_calendar_range(start_date, end_date)
            
            # Display results
            self.print_report(category_time, top_titles, start_date, end_date)
            
            # Ask if user wants to see pie chart
            if self.ask_for_visualization():
                chart_title = f"Time Distribution: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                self.visualizer.create_pie_chart(category_time, chart_title)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please check your credentials and internet connection.")

def main():
    """Main entry point for the CLI application."""
    cli = CalendarTrackerCLI()
    cli.run()

if __name__ == '__main__':
    main()
