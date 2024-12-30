import csv
import json
from datetime import datetime, timedelta

def load_config():
    """Load configuration from config.json."""
    with open('config.json', 'r') as f:
        return json.load(f)

# Configuration for categories and their colors
CATEGORIES = {
    'work': {'color': 'rgb(40, 205, 65)', 'name': 'Work'},  # green
    'morning routine': {'color': 'rgb(255, 59, 48)', 'name': 'Morning Routine'},  # red
    'kids': {'color': 'rgb(255, 149, 0)', 'name': 'Kids'},  # orange
    'personal tasks': {'color': 'rgb(0, 122, 255)', 'name': 'Personal Tasks'},  # blue
    'lunch': {'color': 'rgb(88, 86, 214)', 'name': 'Purple'},  # purple
    'chores': {'color': 'rgb(255, 204, 0)', 'name': 'Chores'},  # yellow
    'relaxation': {'color': 'rgb(89, 173, 196)', 'name': 'Relaxation'},  # light blue
    'waste': {'color': 'rgb(85, 190, 240)', 'name': 'Waste'},  # sky blue
    'commute': {'color': 'rgb(0, 199, 190)', 'name': 'Commute'},  # turquoise
    'going to sleep': {'color': 'rgb(175, 82, 222)', 'name': 'Going to Sleep'},  # violet
    'sleep': {'color': 'rgb(255, 45, 85)', 'name': 'Sleep'},  # pink
    'everything else': {'color': 'rgb(162, 132, 94)', 'name': 'Everything Else'},  # brown
    'meditation': {'color': 'rgb(142, 142, 147)', 'name': 'Meditation'},  # gray
    'family': {'color': 'rgb(255, 59, 48)', 'name': 'Family'}  # red (same as morning routine)
}

def get_category_info(summary, config):
    """Get category and color based on event summary."""
    summary_lower = summary.lower()
    
    # Find matching category from config
    for category, keywords in config['categories'].items():
        for keyword in keywords:
            if keyword.lower() == "everything else":
                continue
            if keyword.lower() in summary_lower:
                return category, CATEGORIES.get(category, CATEGORIES['everything else'])
    
    # If no match found, it falls under "Everything else" which is in the Work category
    return 'work', CATEGORIES['work']

def parse_calendar_data(csv_files, config):
    """Parse calendar data from CSV files."""
    events_by_day = {}
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'Start' not in row or not row['Start']:
                        continue
                    
                    # Only process events from allowed calendar IDs
                    if row['Calendar ID'] not in config['allowed_calendar_ids']:
                        continue
                    
                    # Skip specified events
                    if row['Summary'] in config['skip_summaries']:
                        continue
                        
                    start = datetime.fromisoformat(row['Start'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(row['End'].replace('Z', '+00:00'))
                    
                    day_key = start.date()
                    if day_key not in events_by_day:
                        events_by_day[day_key] = []
                    
                    category, category_info = get_category_info(row['Summary'], config)
                    events_by_day[day_key].append({
                        'summary': row['Summary'],
                        'category': category,
                        'category_name': category_info['name'],
                        'color': category_info['color'],
                        'start': start,
                        'end': end
                    })
        except FileNotFoundError:
            print(f"Warning: {csv_file} not found, skipping...")
            continue
    
    return events_by_day

def minutes_to_pixels(minutes):
    """Convert minutes to pixels for timeline."""
    return (minutes / 1440) * 100  # 1440 minutes in a day, convert to percentage

def format_time(dt):
    """Format datetime to HH:MM."""
    return dt.strftime("%H:%M")

def generate_html(events_by_day):
    """Generate HTML visualization."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .calendar {
                display: flex;
                flex-direction: column;
                gap: 1px;
                background: #ddd;
            }
            .row {
                display: flex;
                background: white;
                height: 25px;
                position: relative;
            }
            .date-cell {
                width: 100px;
                padding: 4px 10px;
                font-size: 12px;
                border-right: 1px solid #ddd;
                flex-shrink: 0;
            }
            .day-cell {
                width: 80px;
                padding: 4px;
                font-size: 12px;
                border-right: 1px solid #ddd;
                flex-shrink: 0;
            }
            .timeline {
                position: relative;
                flex-grow: 1;
                border-top: 1px solid #eee;
            }
            .event {
                position: absolute;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                min-width: 20px;
                box-sizing: border-box;
                border-right: 1px solid rgba(0,0,0,0.1);
                cursor: default;
            }
            .timeline-header {
                position: relative;
                height: 20px;
                border-bottom: 1px solid #ddd;
            }
            .hour-marker {
                position: absolute;
                font-size: 10px;
                color: #666;
                transform: translateX(-50%);
            }
            /* Tooltip styles */
            .event:hover::after {
                content: attr(data-tooltip);
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 1000;
            }
        </style>
    </head>
    <body>
    <div class="calendar">
        <div class="row">
            <div class="date-cell">Date</div>
            <div class="day-cell">Day</div>
            <div class="timeline timeline-header">
    """
    
    # Add hour markers
    for hour in range(24):
        position = (hour / 24) * 100
        html += f'<div class="hour-marker" style="left: {position}%">{hour:02d}</div>'
    
    html += """
            </div>
        </div>
    """
    
    # Sort days
    sorted_days = sorted(events_by_day.keys())
    
    for day in sorted_days:
        events = events_by_day[day]
        day_str = day.strftime("%d.%m.%Y")
        weekday = day.strftime("%A")
        
        html += f'<div class="row"><div class="date-cell">{day_str}</div><div class="day-cell">{weekday}</div><div class="timeline">'
        
        # Generate events
        for event in events:
            start_minutes = event['start'].hour * 60 + event['start'].minute
            end_minutes = event['end'].hour * 60 + event['end'].minute
            
            start_percent = minutes_to_pixels(start_minutes)
            width_percent = minutes_to_pixels(end_minutes - start_minutes)
            
            tooltip = f"{event['category_name']}: {format_time(event['start'])} - {format_time(event['end'])}"
            
            html += f'<div class="event" style="left: {start_percent}%; width: {width_percent}%; background-color: {event["color"]}" data-tooltip="{tooltip}">{event["category"][:1].upper()}</div>'
        
        html += '</div></div>'
    
    html += """
    </div>
    </body>
    </html>
    """
    
    return html

def main():
    config = load_config()
    files = ['calendar_events-2.csv', 'calendar_events.csv']
    events = parse_calendar_data(files, config)
    html = generate_html(events)
    
    with open('calendar_visualization.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    main() 