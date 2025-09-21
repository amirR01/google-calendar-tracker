# Google Calendar Tracker

A command-line tool to analyze, summarize, and visualize your Google Calendar events. Get insights into how you spend your time, discover trends, and generate beautiful charts of your activities.

## Features

- Connects to your Google Calendar using OAuth2.
- Categorizes events by color and activity type.
- Summarizes time spent per category and top activities.
- Analyzes weekly and monthly trends.
- Visualizes your data with pie and trend charts (using matplotlib).
- Fully interactive CLI for custom date ranges and trend analysis.

## Requirements

- Python 3.10 or 3.11
- Google Calendar API credentials (credentials.json)
- Poetry (for dependency management)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/amirR01/google-calendar-tracker.git
   cd google-calendar-tracker
   ```

2. **Install Poetry (if not already installed):**
   ```bash
   pip install poetry
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Set up Google Calendar API credentials:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a project and enable the Google Calendar API.
   - Create OAuth 2.0 credentials and download the credentials.json file.
   - Place credentials.json in the project root directory.

## How to Run

1. **Activate the Poetry environment:**
   ```bash
   poetry shell
   ```

2. **Run the CLI:**
   ```bash
   python cli.py
   ```

   - On first run, a browser window will open for Google authentication.
   - After authentication, a `token.json` file will be created for future use.

3. **Follow the interactive prompts:**
   - Choose analysis mode: week, month, custom range, or trends.
   - Enter date ranges or number of weeks as prompted.
   - View the summary in your terminal.
   - Optionally, display pie or trend charts for visual insights.

## Example Usage

```bash
$ poetry shell
$ python cli.py
```
- Choose "1" for weekly analysis, "2" for monthly, "3" for custom, or "4" for trends.
- Enter dates or number of weeks as prompted.
- View your time breakdown and trends.
- Choose to display charts for a visual summary.

## Notes

- Your Google Calendar data is only accessed locally and never shared.
- The tool uses event color IDs to categorize activities. You can customize event colors in Google Calendar for better tracking.
- For best results, keep your calendar events well-categorized and up-to-date.

## License

MIT License

---

Let me know if you want this README written to your README.md file or if you want to customize any section!