import requests
import json
import config
from datetime import datetime

MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "API-Version": "2023-10"
}

def simulate_push():
    district = "Simulation District"
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Payload matching state_engine.py structure
    column_values = {
        "text_mkz3w205": "Simulation: Comprehensive Metrics Test",       # Headline
        "long_text_mkz3rga9": "Testing detailed metrics integration. Certainty Score appended.\n\n[Certainty Score: 95/100]", # Deep Summary
        "numeric_mkz364ep": 8,   # Magnitude (CORRECTED STATUS ID)
        "color_mkz3fk3v": {"label": "Act"}, # Response Status (Valid: Act, Watch, Monitor, Resolved)
        "color_mkz3kz4n": {"label": "Down"}, # Power (Valid: Functional, Partially Damaged, Down)
        "color_mkz3y5ey": {"label": "Functional"}, # Water
        "color_mkz3st2m": {"label": "Partially Damaged"}, # Comms
        "text_mkz34fzt": "SIM-99", # District Code
        "location_mkz36zby": {"lat": 34.2746, "lng": -119.2290, "address": "Ventura, CA"}, # Geographic Center
        "date_mkz3zaed": {"date": date_str}           # Last Update
    }
    
    print(f"\n[SIMULATED PAYLOAD] {json.dumps(column_values, indent=2)}")
    
    # Mutation using variables
    query = """
    mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
        create_item (board_id: $board_id, item_name: $item_name, column_values: $column_values) {
            id
        }
    }
    """
    
    variables = {
        "board_id": config.MONDAY_DISTRICT_BOARD_ID,
        "item_name": district,
        "column_values": json.dumps(column_values)
    }
    
    print(f"[Monday] Sending test item: '{district}'...")
    
    try:
        response = requests.post(MONDAY_API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
        if response.status_code == 200 and 'errors' not in response.json():
            print(f"[Success] Response: {json.dumps(response.json(), indent=2)}")
        else:
             print(f"[Error] Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[Exception] {e}")

if __name__ == "__main__":
    simulate_push()
