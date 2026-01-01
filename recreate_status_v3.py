import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID, SUGGESTED_LOC_DROPDOWN_ID

def try_fix_status_labels_v3():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    print("Creating 'Suggested Location' (Status) with Labels OBJECT LIST...")
    
    # Try Colors?
    # General (Grey), Alameda (Green), Fresno (Orange), Ventura (Red)
    labels_config = {
        "labels": [
            {"name": "General", "color": "#c4c4c4"},
            {"name": "Alameda", "color": "#009d62"},
            {"name": "Fresno", "color": "#fdab3d"},
            {"name": "Ventura", "color": "#e2445c"}
        ]
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
        
        print("\n--- UPDATE CONFIG.PY ---")
        print(f"SUGGESTED_LOC_DROPDOWN_ID = '{new_col_id}'")
    else:
        print("Failed to create:", data)

if __name__ == "__main__":
    try_fix_status_labels_v3()
