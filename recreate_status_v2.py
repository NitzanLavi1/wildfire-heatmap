import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID, SUGGESTED_LOC_DROPDOWN_ID

def try_fix_status_labels():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    # 1. DELETE existing column (It failed to create last time so it might be gone or half-broken, but delete to be safe if ID exists)
    # The previous script printed "Deleting column..." but failed to create the new one, so the old ID is gone!
    # We need to create a new one regardless.
    
    print("Creating 'Suggested Location' (Status) with Labels ARRAY...")
    
    labels_config = {
        "labels": ["General", "Alameda", "Fresno", "Ventura"]
    }
    
    mutation_create = """
    mutation ($board_id: ID!, $defaults: JSON!) {
        create_column (board_id: $board_id, title: "Suggested Location", column_type: status, defaults: $defaults) {
            id
            settings_str
        }
    }
    """
    
    resp = requests.post(url, json={"query": mutation_create, "variables": {"board_id": int(MONDAY_BOARD_ID), "defaults": labels_config}}, headers=headers)
    data = resp.json()
    
    if "data" in data and data["data"]["create_column"]:
        new_col_id = data["data"]["create_column"]["id"]
        print(f"Created 'Suggested Location'! ID: {new_col_id}")
        
        # Print settings to verify
        print(f"Settings: {data['data']['create_column']['settings_str']}")
        
        print("\n--- UPDATE CONFIG.PY ---")
        print(f"SUGGESTED_LOC_DROPDOWN_ID = '{new_col_id}'")
    else:
        print("Failed to create:", data)

if __name__ == "__main__":
    try_fix_status_labels()
