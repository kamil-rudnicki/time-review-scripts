# Calendar Analyzer

A Python script that analyzes calendar events from CSV files and categorizes time spent on different activities. The script processes calendar events and generates a summary of time spent in various categories like work, family, personal tasks, etc.

## Features

- Processes events from multiple calendar sources
- Categorizes events based on configurable keywords
- Excludes specific events and calendars
- Handles 24-hour events and canceled events
- Supports date range filtering
- Processes ISO 8601 formatted dates with timezone information

## Prerequisites

- Python 3.x
- python-dateutil package

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CalendarAnalyzer
```

2. Install required packages:
```bash
pip3 install python-dateutil
```

3. Create your configuration file:
```bash
cp config.sample.json config.json
```

4. Edit `config.json` with your settings:
- Update `allowed_calendar_ids` with your calendar email addresses
- Customize `skip_summaries` with events you want to exclude
- Set your desired `date_range`
- Adjust `categories` and their keywords as needed

## Configuration

The `config.json` file contains the following settings:

```json
{
    "allowed_calendar_ids": ["your.email@example.com"],
    "skip_summaries": ["Event to skip"],
    "date_range": {
        "start": "YYYY-MM-DD",
        "end": "YYYY-MM-DD"
    },
    "categories": {
        "category_name": ["keyword1", "keyword2"]
    }
}
```

### Configuration Fields

- `allowed_calendar_ids`: List of email addresses whose calendar events should be processed
- `skip_summaries`: List of event summaries to ignore
- `date_range`: Start and end dates for the analysis period
- `categories`: Dictionary of categories and their associated keywords for event classification

## Usage

1. Export your calendar events to CSV files and place them in the project directory
2. Run the script:
```bash
python3 calendar_analyzer.py
```

The script will output:
- Total time spent in each category
- List of events under each category
- Any processing errors encountered

## CSV File Format

The script expects CSV files with the following columns:
1. Calendar ID (email address)
2. Event Summary
3. Description
4. Start Time
5. End Time
6. Start Date (optional)
7. End Date (optional)
8. Status
9. Organizer

Dates should be in ISO 8601 format (e.g., "2024-12-21T09:30:00+01:00")

## Error Handling

The script provides error messages for:
- Missing configuration file
- Invalid JSON in configuration
- Missing required configuration keys
- Date parsing errors
- File access issues

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License 

MIT