# calendar_logic.py

from auth import get_credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
from date_utils import DateRangeUtils

# === Color Category Mapping (Finalized) ===
COLOR_CATEGORY_MAP = {
    '2':  'Professional Tasks',     # Basil (Green)
    '7':  'Meetings',               # Blueberry (Blue)
    '3':  'Social Connections',     # Grape (Purple)
    '5':  'Emotional Recharge',     # Banana (Yellow)
    '1':  'Self-Maintenance',       # Lavender
    '0':  'Self-Maintenance',       # Lavender
    '6':  'Life Admin',             # Tangerine
    '8':  'Mental Struggles',       # Graphite
    '11': 'Romance'                 # Tomato (Love Red)
}

class CalendarAnalyzer:
    """Main class for calendar data analysis and processing."""
    
    def __init__(self):
        """Initialize the calendar analyzer with Google Calendar service."""
        self.creds = get_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def fetch_events(self, time_min: str, time_max: str) -> List[Dict[str, Any]]:
        """
        Fetch all calendar events within the specified time range.
        
        Args:
            time_min: Start time in ISO format
            time_max: End time in ISO format
            
        Returns:
            List of calendar events
        """
        all_events = []
        page_token = None

        while True:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=250,
                pageToken=page_token
            ).execute()

            items = events_result.get('items', [])
            all_events.extend(items)

            page_token = events_result.get('nextPageToken')
            if not page_token:
                break

        return all_events

    def analyze_events(self, events: List[Dict[str, Any]]) -> Tuple[Dict[str, float], Dict[str, List[Tuple[str, float]]]]:
        """
        Analyze events and calculate time spent per category and top activities.
        
        Args:
            events: List of calendar events
            
        Returns:
            Tuple containing:
            - Dictionary of category -> total hours
            - Dictionary of category -> list of top 3 (title, hours) tuples
        """
        category_time = defaultdict(float)
        category_title_duration = defaultdict(lambda: defaultdict(float))

        for event in events:
            start = event.get('start', {}).get('dateTime')
            end = event.get('end', {}).get('dateTime')
            color_id = event.get('colorId', '0')
            summary = event.get('summary', 'Untitled').strip().lower()

            if not start or not end or color_id not in COLOR_CATEGORY_MAP:
                print("Warning: Skipping invalid event")
                continue

            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            duration = (end_dt - start_dt).total_seconds() / 3600

            category = COLOR_CATEGORY_MAP[color_id]
            category_time[category] += duration
            category_title_duration[category][summary] += duration

        # Get top 3 titles by duration for each category
        top_titles = {
            category: sorted(titles.items(), key=lambda x: -x[1])[:3]
            for category, titles in category_title_duration.items()
        }

        return category_time, top_titles

    def analyze_calendar_range(self, start_date: date, end_date: date) -> Tuple[Dict[str, float], Dict[str, List[Tuple[str, float]]]]:
        """
        Perform complete analysis for a date range.
        
        Args:
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            Tuple containing:
            - Dictionary of category -> total hours
            - Dictionary of category -> list of top 3 (title, hours) tuples
        """
        # Convert dates to ISO format with timezone
        time_min, time_max = DateRangeUtils.dates_to_iso_range(start_date, end_date)

        events = self.fetch_events(time_min, time_max)
        return self.analyze_events(events)

    def get_category_mapping(self) -> Dict[str, str]:
        """
        Get the color category mapping.
        
        Returns:
            Dictionary mapping color IDs to category names
        """
        return COLOR_CATEGORY_MAP.copy()
    
    def analyze_weekly_trends(self, num_weeks: int) -> Dict[str, Any]:
        """
        Analyze trends over the last N weeks for each category.
        
        Args:
            num_weeks: Number of weeks to analyze (including current week)
            
        Returns:
            Dictionary containing:
            - weekly_data: List of weekly breakdowns
            - trends: Dictionary with trend analysis for each category
            - summary: Overall trend summary
        """
        weekly_data = []
        all_category_hours = defaultdict(list)
        
        today = date.today()
        # Find the most recent Saturday (0=Monday, 6=Sunday)
        days_since_saturday = (today.weekday() - 5) % 7  # Saturday is 5
        last_saturday = today - timedelta(days=days_since_saturday) if today.weekday() != 5 else today
        
        for week_offset in range(num_weeks - 1, -1, -1):  # Go backwards from oldest to newest
            week_end = last_saturday - timedelta(days=(week_offset) * 7)
            week_start = week_end - timedelta(days=6)
            # Get week data
            category_time, top_titles = self.analyze_calendar_range(week_start, week_end)
            # Store weekly data
            week_info = {
                'week_start': week_start,
                'week_end': week_end,
                'category_time': category_time,
                'top_titles': top_titles,
                'total_hours': sum(category_time.values())
            }
            weekly_data.append(week_info)
        # Collect data for trend analysis - ensure all categories have the same number of data points
        for category in COLOR_CATEGORY_MAP.values():
            category_hours = []
            for week_data in weekly_data:
                category_hours.append(week_data['category_time'].get(category, 0.0))
            all_category_hours[category] = category_hours
        
        # Calculate trends
        trends = {}
        for category, hours_list in all_category_hours.items():
            if len(hours_list) >= 2:
                # Calculate trend (positive = increasing, negative = decreasing)
                recent_avg = sum(hours_list[-2:]) / 2  # Last 2 weeks average
                older_avg = sum(hours_list[:-2]) / max(1, len(hours_list) - 2) if len(hours_list) > 2 else hours_list[0]
                trend_change = recent_avg - older_avg
                
                # Calculate percentage change
                percentage_change = (trend_change / older_avg * 100) if older_avg > 0 else 0
                
                trends[category] = {
                    'hours_list': hours_list,
                    'trend_change': trend_change,
                    'percentage_change': percentage_change,
                    'recent_avg': recent_avg,
                    'older_avg': older_avg,
                    'direction': 'increasing' if trend_change > 0.5 else 'decreasing' if trend_change < -0.5 else 'stable'
                }
            else:
                trends[category] = {
                    'hours_list': hours_list,
                    'trend_change': 0,
                    'percentage_change': 0,
                    'recent_avg': hours_list[0] if hours_list else 0,
                    'older_avg': hours_list[0] if hours_list else 0,
                    'direction': 'stable'
                }
        
        # Generate summary
        increasing_categories = [cat for cat, data in trends.items() if data['direction'] == 'increasing']
        decreasing_categories = [cat for cat, data in trends.items() if data['direction'] == 'decreasing']
        
        summary = {
            'total_weeks': num_weeks,
            'increasing_categories': increasing_categories,
            'decreasing_categories': decreasing_categories,
            'most_improved': max(trends.items(), key=lambda x: x[1]['trend_change'])[0] if trends else None,
            'most_declined': min(trends.items(), key=lambda x: x[1]['trend_change'])[0] if trends else None
        }
        
        return {
            'weekly_data': weekly_data,
            'trends': trends,
            'summary': summary
        }
    
    def analyze_category_breakdown(self, start_date: date, end_date: date, target_category: str) -> Dict[str, Any]:
        """
        Analyze detailed breakdown for a specific category, showing event types and their time distribution.
        
        Args:
            start_date: Analysis start date
            end_date: Analysis end date
            target_category: The category to analyze in detail
            
        Returns:
            Dictionary containing:
            - category_total_hours: Total hours spent in this category
            - category_percentage: Percentage of total time this category represents
            - event_types: Dictionary of event title -> hours spent
            - event_type_percentages: Dictionary of event title -> percentage within category
            - top_events: Top 10 events by time spent
            - total_calendar_hours: Total hours across all categories for context
        """
        # Convert dates to ISO format with timezone
        time_min, time_max = DateRangeUtils.dates_to_iso_range(start_date, end_date)
        
        # Fetch all events
        all_events = self.fetch_events(time_min, time_max)
        
        # Process all events to get context
        all_category_time = defaultdict(float)
        category_events = defaultdict(lambda: defaultdict(float))
        
        for event in all_events:
            start = event.get('start', {}).get('dateTime')
            end = event.get('end', {}).get('dateTime')
            color_id = event.get('colorId', '0')
            summary = event.get('summary', 'Untitled').strip()

            if not start or not end or color_id not in COLOR_CATEGORY_MAP:
                continue

            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            duration = (end_dt - start_dt).total_seconds() / 3600

            category = COLOR_CATEGORY_MAP[color_id]
            all_category_time[category] += duration
            
            # Track individual events for the target category
            if category == target_category:
                category_events[category][summary] += duration
        
        # Calculate statistics for target category
        category_total_hours = all_category_time.get(target_category, 0.0)
        total_calendar_hours = sum(all_category_time.values())
        category_percentage = (category_total_hours / total_calendar_hours * 100) if total_calendar_hours > 0 else 0
        
        # Get event types within the target category
        event_types = dict(category_events[target_category]) if target_category in category_events else {}
        
        # Calculate percentages for each event type within the category
        event_type_percentages = {}
        if category_total_hours > 0:
            for event_title, hours in event_types.items():
                event_type_percentages[event_title] = (hours / category_total_hours * 100)
        
        # Get top events sorted by time spent
        top_events = sorted(event_types.items(), key=lambda x: -x[1])[:10]
        
        return {
            'category_name': target_category,
            'category_total_hours': category_total_hours,
            'category_percentage': category_percentage,
            'event_types': event_types,
            'event_type_percentages': event_type_percentages,
            'top_events': top_events,
            'total_calendar_hours': total_calendar_hours,
            'total_events_in_category': len(event_types)
        }
