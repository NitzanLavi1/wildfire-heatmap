import requests
import json
import config

API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "API-Version": "2023-10"
}
BOARD_ID = config.MONDAY_DISTRICT_BOARD_ID

# Define new columns to create
NEW_COLUMNS = [
    # Human Safety
    {"title": "Fatalities", "type": "numbers"},
    {"title": "Injured", "type": "numbers"},
    {"title": "People Threatened", "type": "numbers"},
    
    # Infrastructure
    {"title": "Structures Destroyed", "type": "numbers"},
    {"title": "Structures Threatened", "type": "numbers"},
    {"title": "Infra Impact Score", "type": "numbers"},
    
    # Fire Stats
    {"title": "Acres Burned", "type": "numbers"},
    {"title": "Containment %", "type": "numbers"},
    {"title": "AQI", "type": "numbers"},
    
    # Operational
    {"title": "Personnel Count", "type": "numbers"},
    {"title": "Apparatus Count", "type": "numbers"} 
]

def create_column(title, col_type):
    query = """
    mutation ($board_id: ID!, $title: String!, $type: ColumnType!) {
        create_column (board_id: $board_id, title: $title, column_type: $type) {
            id
            title
        }
    }
    """
    variables = {
        "board_id": int(BOARD_ID),
        "title": title,
        "type": col_type
    }
    
    response = requests.post(API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print(f"Error creating {title}: {data['errors']}")
        else:
            col_id = data['data']['create_column']['id']
            print(f"Created '{title}': {col_id}")
            return col_id
    else:
        print(f"Request failed: {response.status_code}")
    return None

if __name__ == "__main__":
    print(f"Creating {len(NEW_COLUMNS)} new columns on Board {BOARD_ID}...")
    
    results = {}
    for col in NEW_COLUMNS:
        col_id = create_column(col['title'], col['type'])
        if col_id:
            results[col['title'].upper().replace(" ", "_")] = col_id
            
    print("\n--- NEW CONFIG ENTRIES ---")
    for key, val in results.items():
        print(f'{key}_COL_ID = "{val}"')
