import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID, SUGGESTED_LOC_DROPDOWN_ID

def recreate_status_with_labels():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    # 1. DELETE existing column
    print(f"Deleting column {SUGGESTED_LOC_DROPDOWN_ID}...")
    delete_query = """
    mutation ($board_id: ID!, $col_id: String!) {
        delete_column (board_id: $board_id, column_id: $col_id) {
            id
        }
    }
    """
    requests.post(url, json={"query": delete_query, "variables": {"board_id": int(MONDAY_BOARD_ID), "col_id": SUGGESTED_LOC_DROPDOWN_ID}}, headers=headers)
    
    # 2. CREATE new Status column with Labels
    print("Creating 'Suggested Location' (Status) with Labels...")
    
    # Define labels map
    # Monday Status defaults format often uses indexes.
    # We will try passing 'settings_str' if possible, or 'defaults'.
    # A known trick is to just create it and hope for the best, or use a complex settings object.
    # But let's try 'defaults' with the specific JSON structure Monday uses.
    
    # Valid Status defaults JSON: {"labels": {"0": "General", "1": "Alameda", "5": "Fresno", "10": "Ventura"}, "labels_positions_text_mode": ...}
    
    labels_config = {
        "labels": {
            "0": "General", # Grey/Default
            "1": "Alameda", # Green
            "2": "Fresno", # Orange
            "3": "Ventura"  # Red
        }
    }
    
    mutation_create = """
    mutation ($board_id: ID!, $defaults: JSON!) {
        create_column (board_id: $board_id, title: "Suggested Location", column_type: status, defaults: $defaults) {
            id
        }
    }
    """
    
    status_vars = {
        "board_id": int(MONDAY_BOARD_ID),
        "defaults": json.dumps(labels_config) # Pass as JSON string if type is JSON? No, type is JSON, pass as dict.
    }
    # Wait, 'defaults' argument in create_column expects specific format. 
    # If the API definition expects JSON scalar, we pass simple JSON.
    
    # Let's try passing the dict directly if the variable type is JSON.
    
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
    recreate_status_with_labels()
