import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import os


def normalize_day(timestamp: str) -> str:
    """Extracts the YYYY-MM-DD day from ISO timestamp."""
    return datetime.fromisoformat(timestamp).date().isoformat()


def group_apple_watch_data(data):
    """Groups Apple Watch health data by day and type."""
    grouped = defaultdict(lambda: defaultdict(list))

    for entry in data:
        # Fallback if only one of startDate/date is present
        timestamp = entry.get("startDate") or entry.get("date")
        if not timestamp:
            continue  # skip invalid entries

        day = normalize_day(timestamp)
        type_ = entry["type"]

        grouped[day][type_].append({k: v for k, v in entry.items() if k not in ["type"]})

    return grouped


def create_sample_data():
    """Creates sample Apple Watch health data for testing."""
    sample_data = [
        {
            "type": "HeartRate",
            "startDate": "2025-07-08T10:30:00+00:00",
            "value": 68,
            "unit": "bpm"
        },
        {
            "type": "HeartRate", 
            "startDate": "2025-07-08T11:00:00+00:00",
            "value": 78,
            "unit": "bpm"
        },
        {
            "type": "HeartRate",
            "startDate": "2025-07-08T11:30:00+00:00", 
            "value": 102,
            "unit": "bpm"
        },
        {
            "type": "Steps",
            "startDate": "2025-07-08T09:00:00+00:00",
            "value": 2500,
            "unit": "count"
        },
        {
            "type": "Steps",
            "startDate": "2025-07-09T09:00:00+00:00",
            "value": 3200,
            "unit": "count"
        }
    ]
    return sample_data


def inputting_data():
    """Creates sample data file if it doesn't exist."""
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    sample_file = data_dir / "apple_watch_7day_raw_data.json"
    
    if not sample_file.exists():
        sample_data = create_sample_data()
        with sample_file.open("w") as fp:
            json.dump(sample_data, fp, indent=2)
        print(f"Created sample data file: {sample_file}")
    else:
        print(f"Data file already exists: {sample_file}")


if __name__ == "__main__":
    # Ensure data directory exists and create sample data if needed
    inputting_data()
    
    data_file = Path("./data/apple_watch_7day_raw_data.json")
    
    if data_file.exists():
        with data_file.open() as fp:
            data = json.load(fp)
            grouped_data = group_apple_watch_data(data)

        output_file = Path("./data/grouped_watch_data.json")
        with output_file.open("w") as fp:
            json.dump(grouped_data, fp, indent=2)
            
        print(f"Successfully processed {len(data)} entries")
        print(f"Grouped data saved to: {output_file}")
        
        # Print summary
        for day, types in grouped_data.items():
            print(f"\nDay: {day}")
            for type_name, entries in types.items():
                print(f"  {type_name}: {len(entries)} entries")
    else:
        print(f"Error: Data file not found at {data_file}")