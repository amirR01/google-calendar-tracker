# calendar_logic.py

from auth import get_credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
import pytz
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
