# tracker.py

from auth import get_credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
import pytz

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

def fetch_events(service, time_min, time_max):
    all_events = []
    page_token = None

    while True:
        events_result = service.events().list(
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

def analyze_events(events):
    category_time = defaultdict(float)
    category_title_duration = defaultdict(lambda: defaultdict(float))

    for event in events:
        start = event.get('start', {}).get('dateTime')
        end = event.get('end', {}).get('dateTime')
        color_id = event.get('colorId', '0')
        summary = event.get('summary', 'Untitled').strip().lower()

        if not start or not end or color_id not in COLOR_CATEGORY_MAP:
            print("something bad happend")
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

def print_report(category_time, top_titles, start_date, end_date):
    print("\n📊 Calendar Summary:")
    print(f"🗓️  From {start_date.strftime('%A, %Y-%m-%d')} to {end_date.strftime('%A, %Y-%m-%d')}\n")

    for category, hours in sorted(category_time.items(), key=lambda x: -x[1]):
        print(f"🔸 {category}: {hours:.2f} hours")
        for title, duration in top_titles[category]:
            print(f"    - {title} ({duration:.2f}h)")
        print()



def range_input():
    print("Choose analysis mode:")
    print("  1. Week (Sunday–Saturday)")
    print("  2. Month (Calendar month)")
    print("  3. Custom date range")
    choice = input("Enter 1 / 2 / 3: ").strip()

    if choice == "1":
        mode = "week"
    elif choice == "2":
        mode = "month"
    elif choice == "3":
        mode = "range"
    else:
        print("Invalid choice.")
        return
    return mode

def get_date_range(mode):
    today = date.today()

    if mode == "week":
        # Start on Sunday
        start = today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
        end = start + timedelta(days=6)

    elif mode == "month":
        start = today.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)

    elif mode == "range":
        start_input = input("Enter start date (YYYY-MM-DD): ")
        end_input = input("Enter end date (YYYY-MM-DD): ")
        start = datetime.strptime(start_input, "%Y-%m-%d").date()
        end = datetime.strptime(end_input, "%Y-%m-%d").date()

    else:
        raise ValueError("Invalid mode")

    return start, end

def main():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    mode = range_input()

    start_date, end_date = get_date_range(mode)

    # Time zone aware ISO 8601 format
    time_min = datetime.combine(start_date, datetime.min.time()).isoformat() + 'Z'
    time_max = datetime.combine(end_date + timedelta(days=1), datetime.min.time()).isoformat() + 'Z'

    events = fetch_events(service, time_min, time_max)
    category_time, top_titles = analyze_events(events)
    print_report(category_time, top_titles, start_date, end_date)


if __name__ == '__main__':
    main()