import requests
import json
from config import MONDAY_API_KEY, MONDAY_DISTRICT_BOARD_ID

def fetch_columns():
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": MONDAY_API_KEY,
        "API-Version": "2023-10"
    }
    
    query = """
    query ($board_id: [ID!]) {
        boards (ids: $board_id) {
            columns {
                title
                id
                type
                settings_str
            }
        }
    }
    """
    
    resp = requests.post(url, json={"query": query, "variables": {"board_id": int(MONDAY_DISTRICT_BOARD_ID)}}, headers=headers)
    print(f"Raw Response: {resp.text}") # Debug
    data = resp.json()
    
    print(f"--- Columns on Board {MONDAY_DISTRICT_BOARD_ID} ---")
    for col in data["data"]["boards"][0]["columns"]:
        print(f"Title: {col['title']} | ID: {col['id']} | Type: {col['type']}")
        if col['type'] == 'color': # Status columns are type 'color' or 'status'
             print(f"  -> Settings: {col['settings_str']}")

if __name__ == "__main__":
    fetch_columns()
