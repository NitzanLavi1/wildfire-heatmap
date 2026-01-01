import json
import uuid
import random
from datetime import datetime, timedelta

def generate_simulation():
    """
    Simulates the JSON output of the Tri-Signal Pipeline for a scenario
    where a fire starts in Topanga Canyon and is detected by multiple sources.
    """
    
    # Base Timestamp & History Range
    now = datetime.now()
    days_back = 14
    
    simulated_data = []
    
    # helper to get random time in last N days
    def random_date(days):
        return now - timedelta(days=random.randint(0, days-1), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    
    # 1. Official Major Event (Topanga)
    simulated_data.append({
        "id": str(uuid.uuid4()),
        "headline": "BRUSH FIRE Topanga Canyon; EVACUATION ORDER.",
        "source_name": "Official LAFD",
        "source_link": "https://www.lafd.org/news/topanga",
        "coordinates": [34.0935, -118.6003],
        "evacuation_status": "Active/Warning",
        "priority": "High",
        "timestamp": random_date(days_back).isoformat(),
        "magnitude": 9.5,
        "certainty_index": "Official Source Verified",
        "raw_text": "CRITICAL: Fast moving brush fire in Topanga Canyon. Structures threatened. Mandatory Evacuations in progress for Zones 1-4. #TopangaFire"
    })

    # Scenario: South to North Progression
    # Days 0-3: South (Joshua Tree, LA area)
    # Days 4-7: Central (Ventura, Santa Barbara, Santa Cruz)
    # Days 8-11: Central-North (Fresno, Yosemite)
    # Days 12-14: North (Bay Area, Tahoe)
    
    stages = [
        {
            "days": range(0, 4),
            "locations": [
                ("Joshua Tree", 33.8734, -115.9010),
                ("Griffith Park", 34.1132, -118.3081),
                ("Getty Center", 34.0768, -118.4739)
            ],
            "intensity": 5  # reports per day
        },
        {
            "days": range(4, 8),
            "locations": [
                ("Ventura Coast", 34.2746, -119.2290),
                ("Santa Barbara", 34.4208, -119.6982),
                ("Santa Cruz", 36.9741, -122.0308)
            ],
            "intensity": 10
        },
        {
            "days": range(8, 12),
            "locations": [
                ("Fresno City", 36.7378, -119.7871),
                ("Yosemite Valley", 37.7456, -119.5936)
            ],
            "intensity": 15
        },
        {
            "days": range(12, 15),
            "locations": [
                ("Oakland Hills", 37.8044, -122.2711),
                ("Berkeley", 37.8715, -122.2730),
                ("Lake Tahoe", 39.0968, -120.0324)
            ],
            "intensity": 12
        }
    ]
    
    start_date = now - timedelta(days=14)
    sources = ["Twitter", "Telegram", "Reddit", "Facebook"]
    
    for stage in stages:
        for day in stage["days"]:
            current_day = start_date + timedelta(days=day)
            
            # Generate multiple reports for this day/stage
            for i in range(stage["intensity"]):
                loc_name, lat, lon = random.choice(stage["locations"])
                source = random.choice(sources)
                
                # Jitter coordinates
                lat += random.uniform(-0.05, 0.05)
                lon += random.uniform(-0.05, 0.05)
                
                # Time jitter within the day
                event_time = current_day + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                
                priority = "High" if i % 3 == 0 else "Medium"
                magnitude = 9.0 if priority == "High" else 6.0
                
                headline = f"Reported smoke near {loc_name}." if priority != "High" else f"FLAMES VISIBLE near {loc_name}! Urgent."
                
                simulated_data.append({
                    "id": str(uuid.uuid4()),
                    "headline": headline,
                    "raw_text": f"Fire activity spotted near {loc_name}. #wildfire {priority} intensity.",
                    "source_name": source,
                    "source_link": f"https://example.com/{source.lower()}/{day}_{i}",
                    "coordinates": [lat, lon],
                    "evacuation_status": "Unknown" if priority != "High" else "Warning",
                    "priority": priority,
                    "timestamp": event_time.isoformat(),
                    "magnitude": magnitude,
                    "certainty_index": "Likely Legitimate (Simulated Progression)"
                })
        
    # V4 SLANG FILTER TEST
    # This item should NOT appear on Monday if logic works in pipeline 
    # (But locally simulated push bypasses pipeline filters, so we just show it has low magnitude)
    simulated_data.append({
        "id": str(uuid.uuid4()),
        "headline": "Yo this new mixtape is FIRE bro!",
        "source_name": "Twitter",
        "source_link": "https://twitter.com/slang",
        "coordinates": [34.0522, -118.2437],
        "evacuation_status": "Unknown",
        "priority": "Low",
        "timestamp": now.isoformat(),
        "magnitude": 1.0, 
        "certainty_index": "Flagged as Slang: 'this new mixtape is fire'",
        "raw_text": "Yo this new mixtape is FIRE bro! Check it out at the link!"
    })
    
    return simulated_data

if __name__ == "__main__":
    from integrations import MondayIntegration
    
    data = generate_simulation()
    
    # 1. Save to JSON file
    with open("simulated_wildfire_feed.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Simulated feed saved to 'simulated_wildfire_feed.json'")

    # 2. Push to Monday.com
    print("\nPushing simulated events to monday.com...")
    monday = MondayIntegration()
    
    for event in data:
        print(f" -> Sending: {event['headline']}")
        success = monday.push_incident(event)
        if success:
            print("    [Success]")
        else:
            print("    [Failed - Check API Key]")
            
    print("\nSimulation and Push Complete.")
