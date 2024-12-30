import csv
import json
import os
from datetime import datetime, timedelta
from dateutil import parser  # For handling ISO 8601 dates

def load_config(config_file='config.json'):
    if not os.path.exists(config_file):
        if os.path.exists('config.sample.json'):
            print(f"Error: {config_file} not found! Please copy config.sample.json to {config_file} and update it with your settings.")
        else:
            print(f"Error: {config_file} not found!")
        exit(1)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
            # Parse date range from config
            config['range_start'] = parse_date(config['date_range']['start']).timestamp()
            config['range_end'] = parse_date(config['date_range']['end']).timestamp()
            
            return config
    except json.JSONDecodeError:
        print(f"Error: {config_file} is not valid JSON!")
        exit(1)
    except KeyError as e:
        print(f"Error: Missing required configuration key: {e}")
        exit(1)

def parse_date(date_str):
    try:
        # Parse ISO format dates (including timezone info)
        return parser.parse(date_str)
    except (ValueError, TypeError):
        # Fallback to basic formats if ISO parsing fails
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")

def parse_duration(start, end):
    start_time = parse_date(start)
    end_time = parse_date(end)
    return (end_time - start_time).total_seconds() / 3600  # Convert to hours

def is_24_hour_event(start, end):
    start_time = parse_date(start)
    end_time = parse_date(end)
    duration = (end_time - start_time).total_seconds() / 3600  # Duration in hours
    
    return start_time.strftime('%H:%M:%S') == '00:00:00' and (duration == 24 or abs(duration - 24) < 0.001)

def categorize_event(summary, categories):
    summary_lower = summary.lower()
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() == "everything else":
                continue
            if keyword.lower() in summary_lower:
                return category
    
    # If no match found, it falls under "Everything else" which is in the Work category
    return 'work'

def process_file(filename, summary_totals, category_summaries, range_start, range_end, config):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            
            for row in csv_reader:
                calendar_id = row[0]
                
                # Only process events from allowed calendar IDs
                if calendar_id not in config['allowed_calendar_ids']:
                    continue

                summary = row[1]

                # Skip specified events
                if summary in config['skip_summaries']:
                    continue

                try:
                    start = row[3]
                    end = row[4]
                    start_date = row[5] if len(row) > 5 and row[5] else start
                    end_date = row[6] if len(row) > 6 and row[6] else end
                    status = row[7].lower() if len(row) > 7 else ''

                    # Skip canceled events
                    if status in ['cancelled', 'canceled'] or 'canceled' in summary.lower():
                        continue

                    # Skip 24-hour events
                    if is_24_hour_event(start, end):
                        continue

                    # Check if the event is within the specified date range
                    event_start = parse_date(start_date).timestamp()
                    event_end = parse_date(end_date).timestamp()

                    if range_start <= event_start <= range_end:
                        if start and end:
                            duration = parse_duration(start, end)
                            category = categorize_event(summary, config['categories'])
                            
                            if category not in summary_totals:
                                summary_totals[category] = 0
                                category_summaries[category] = []
                            
                            summary_totals[category] += duration
                            if summary not in category_summaries[category]:
                                category_summaries[category].append(summary)
                except (ValueError, IndexError) as e:
                    print(f"Error processing row: {row}")
                    print(f"Error details: {str(e)}")
                    continue
                            
    except FileNotFoundError:
        print(f"Error opening file: {filename}")

def main():
    config = load_config()
    
    summary_totals = {}
    category_summaries = {}

    files = ['calendar_events-2.csv', 'calendar_events.csv']

    for file in files:
        process_file(file, summary_totals, category_summaries, config['range_start'], config['range_end'], config)

    print(f"Total time for each category ({config['date_range']['start']} to {config['date_range']['end']}, excluding 24-hour and canceled events):")
    for category, total_hours in summary_totals.items():
        print(f"{category},{total_hours:.2f}")
        for summary in category_summaries[category]:
            print(f"  - {summary}")

if __name__ == "__main__":
    main() 