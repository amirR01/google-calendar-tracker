# cli.py

from calendar_logic import CalendarAnalyzer
from date_utils import DateRangeUtils
from visualization import CalendarVisualizer
from datetime import datetime, date
from typing import Tuple, Dict, List, Any, Union

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
        print("  4. Weekly trends (last N weeks)")
        choice = input("Enter 1 / 2 / 3 / 4: ").strip()
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
    
    def get_number_of_weeks(self) -> int:
        """
        Get the number of weeks for trend analysis from user.
        
        Returns:
            Number of weeks to analyze
        """
        while True:
            try:
                num_weeks = input("How many weeks to analyze? (2-12): ").strip()
                weeks = int(num_weeks)
                if 2 <= weeks <= 12:
                    return weeks
                else:
                    print("Please enter a number between 2 and 12.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_date_range_from_user(self) -> Union[Tuple[str, Tuple[date, date]], Tuple[str, int]]:
        """
        Get date range or trend parameters based on user choice.
        
        Returns:
            Tuple of (mode, parameters) where parameters can be (start_date, end_date) or num_weeks
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
        elif choice == "4":
            mode = "trends"
            num_weeks = self.get_number_of_weeks()
            return mode, num_weeks
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

    def print_trend_report(self, trend_data: Dict[str, Any]) -> None:
        """
        Print the trend analysis report to console.
        
        Args:
            trend_data: Dictionary containing weekly data and trends
        """
        weekly_data = trend_data['weekly_data']
        trends = trend_data['trends']
        summary = trend_data['summary']
        
        print(f"\n📈 Weekly Trends Analysis ({summary['total_weeks']} weeks)")
        print(f"🗓️  From {weekly_data[0]['week_start'].strftime('%Y-%m-%d')} to {weekly_data[-1]['week_end'].strftime('%Y-%m-%d')}\n")
        
        # Show trend summary
        if summary['increasing_categories']:
            print("📈 Increasing categories:")
            for category in summary['increasing_categories']:
                change = trends[category]['trend_change']
                percentage = trends[category]['percentage_change']
                print(f"  ▲ {category}: +{change:.1f}h ({percentage:+.1f}%)")
            print()
        
        if summary['decreasing_categories']:
            print("📉 Decreasing categories:")
            for category in summary['decreasing_categories']:
                change = trends[category]['trend_change']
                percentage = trends[category]['percentage_change']
                print(f"  ▼ {category}: {change:.1f}h ({percentage:+.1f}%)")
            print()
        
        if summary['most_improved'] and trends[summary['most_improved']]['trend_change'] > 0.5:
            print(f"🏆 Most improved: {summary['most_improved']} (+{trends[summary['most_improved']]['trend_change']:.1f}h)")
        
        if summary['most_declined'] and trends[summary['most_declined']]['trend_change'] < -0.5:
            print(f"⚠️  Most declined: {summary['most_declined']} ({trends[summary['most_declined']]['trend_change']:.1f}h)")
        
        print(f"\n📊 Weekly breakdown:")
        for i, week_data in enumerate(weekly_data):
            total = week_data['total_hours']
            print(f"Week {i+1} ({week_data['week_start'].strftime('%m/%d')}-{week_data['week_end'].strftime('%m/%d')}): {total:.1f} total hours")
        print()

    def run(self) -> None:
        """
        Main CLI loop - run the complete application.
        """
        try:
            print("🗓️ Welcome to Google Calendar Tracker!\n")
            
            # Get user preferences
            mode_result = self.get_date_range_from_user()
            
            if mode_result[0] == "trends":
                # Handle trends analysis
                mode, num_weeks = mode_result
                print(f"\n🔄 Analyzing trends over last {num_weeks} weeks...")
                
                # Perform trend analysis
                trend_data = self.analyzer.analyze_weekly_trends(num_weeks)
                
                # Display results
                self.print_trend_report(trend_data)
                
                # Ask if user wants to see trend chart
                if self.ask_for_visualization():
                    chart_title = f"Weekly Trends Analysis: Last {num_weeks} Weeks"
                    self.visualizer.create_trend_chart(trend_data, chart_title)
            
            else:
                # Handle regular analysis
                mode, (start_date, end_date) = mode_result
                print(f"\n🔄 Analyzing {mode} data...")
                
                # Perform analysis
                category_time, top_titles = self.analyzer.analyze_calendar_range(start_date, end_date)
                
                # Display results
                self.print_report(category_time, top_titles, start_date, end_date)
                
                # Ask if user wants to see pie chart
                if self.ask_for_visualization():
                    chart_title = f"Time Distribution: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                    self.visualizer.create_pie_chart(category_time, top_titles, chart_title)
            
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
