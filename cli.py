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
    
    def display_analysis_mode_menu(self) -> str:
        """
        Display the analysis mode menu and get user choice.
        
        Returns:
            User's analysis mode choice
        """
        print("Choose analysis mode:")
        print("  1. General Analysis")
        print("  2. Weekly Trends")
        print("  3. Category-based Analysis")
        choice = input("Enter 1 / 2 / 3: ").strip()
        return choice
    
    def display_timeframe_menu(self) -> str:
        """
        Display the timeframe menu for general and category analysis.
        
        Returns:
            User's timeframe choice
        """
        print("\nChoose timeframe:")
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
    
    def get_category_choice(self) -> str:
        """
        Display available categories and get user's choice.
        
        Returns:
            Selected category name
        """
        categories = list(self.analyzer.get_category_mapping().values())
        categories = list(set(categories))  # Remove duplicates
        categories.sort()  # Sort alphabetically
        
        print("\nAvailable categories:")
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")
        
        while True:
            try:
                choice = input(f"Select category (1-{len(categories)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(categories):
                    return categories[idx]
                else:
                    print(f"Please enter a number between 1 and {len(categories)}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_analysis_parameters(self) -> Tuple[str, Any]:
        """
        Get analysis parameters based on user's choices.
        
        Returns:
            Tuple of (analysis_type, parameters) where parameters vary by type:
            - For 'general': (timeframe_mode, (start_date, end_date))
            - For 'trends': num_weeks
            - For 'category': (category_name, timeframe_mode, (start_date, end_date))
        """
        analysis_choice = self.display_analysis_mode_menu()
        
        if analysis_choice == "1":  # General Analysis
            timeframe_choice = self.display_timeframe_menu()
            timeframe_mode, date_range = self._get_date_range_by_choice(timeframe_choice)
            return "general", (timeframe_mode, date_range)
            
        elif analysis_choice == "2":  # Weekly Trends
            num_weeks = self.get_number_of_weeks()
            return "trends", num_weeks
            
        elif analysis_choice == "3":  # Category-based Analysis
            category = self.get_category_choice()
            timeframe_choice = self.display_timeframe_menu()
            timeframe_mode, date_range = self._get_date_range_by_choice(timeframe_choice)
            return "category", (category, timeframe_mode, date_range)
            
        else:
            print("Invalid choice.")
            raise ValueError("Invalid analysis mode choice")
    
    def _get_date_range_by_choice(self, choice: str) -> Tuple[str, Tuple[date, date]]:
        """
        Helper method to get date range based on timeframe choice.
        
        Args:
            choice: Timeframe choice ('1', '2', or '3')
            
        Returns:
            Tuple of (mode, (start_date, end_date))
        """
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
            print("Invalid timeframe choice.")
            raise ValueError("Invalid timeframe choice")
        
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

    def print_category_report(self, category_data: Dict[str, Any], start_date: date, end_date: date) -> None:
        """
        Print the category analysis report to console.
        
        Args:
            category_data: Dictionary containing category analysis results
            start_date: Analysis start date
            end_date: Analysis end date
        """
        print(f"\n📊 Category Analysis: {category_data['category_name']}")
        print(f"🗓️  From {start_date.strftime('%A, %Y-%m-%d')} to {end_date.strftime('%A, %Y-%m-%d')}\n")
        
        print(f"📈 Overall Statistics:")
        print(f"   • Total time in {category_data['category_name']}: {category_data['category_total_hours']:.2f} hours")
        print(f"   • Percentage of total calendar time: {category_data['category_percentage']:.1f}%")
        print(f"   • Number of different event types: {category_data['total_events_in_category']}")
        print(f"   • Total calendar time (all categories): {category_data['total_calendar_hours']:.2f} hours\n")
        
        if category_data['top_events']:
            print(f"🎯 Event Types in {category_data['category_name']}:")
            for i, (event_title, hours) in enumerate(category_data['top_events'], 1):
                percentage = category_data['event_type_percentages'].get(event_title, 0)
                print(f"   {i:2d}. {event_title}")
                print(f"       ⏱️  {hours:.2f} hours ({percentage:.1f}% of category)")
            print()
        else:
            print(f"❌ No events found in {category_data['category_name']} for this timeframe.\n")

    def run(self) -> None:
        """
        Main CLI loop - run the complete application.
        """
        try:
            print("🗓️ Welcome to Google Calendar Tracker!\n")
            
            # Get user preferences
            analysis_type, parameters = self.get_analysis_parameters()
            
            if analysis_type == "general":
                # Handle general analysis (original functionality)
                timeframe_mode, (start_date, end_date) = parameters
                print(f"\n🔄 Analyzing {timeframe_mode} data...")
                
                # Perform analysis
                category_time, top_titles = self.analyzer.analyze_calendar_range(start_date, end_date)
                
                # Display results
                self.print_report(category_time, top_titles, start_date, end_date)
                
                # Ask if user wants to see pie chart
                if self.ask_for_visualization():
                    chart_title = f"General Analysis: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                    self.visualizer.create_pie_chart(category_time, top_titles, chart_title)
            
            elif analysis_type == "trends":
                # Handle trends analysis
                num_weeks = parameters
                print(f"\n🔄 Analyzing trends over last {num_weeks} weeks...")
                
                # Perform trend analysis
                trend_data = self.analyzer.analyze_weekly_trends(num_weeks)
                
                # Display results
                self.print_trend_report(trend_data)
                
                # Ask if user wants to see trend chart
                if self.ask_for_visualization():
                    chart_title = f"Weekly Trends Analysis: Last {num_weeks} Weeks"
                    self.visualizer.create_trend_chart(trend_data, chart_title)
            
            elif analysis_type == "category":
                # Handle category-based analysis
                category_name, timeframe_mode, (start_date, end_date) = parameters
                print(f"\n🔄 Analyzing '{category_name}' category for {timeframe_mode} period...")
                
                # Perform category analysis
                category_data = self.analyzer.analyze_category_breakdown(start_date, end_date, category_name)
                
                # Display results
                self.print_category_report(category_data, start_date, end_date)
                
                # Ask if user wants to see visualization (if there's data to show)
                if category_data['top_events'] and self.ask_for_visualization():
                    chart_title = f"Category Analysis: {category_name} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
                    self.visualizer.create_category_chart(category_data, chart_title)
            
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
