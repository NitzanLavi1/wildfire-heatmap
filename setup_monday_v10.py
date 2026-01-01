import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def setup_monday_v10():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    print("Creating 'Suggested Location' (Status Type)...")
    
    # Try the Array of Objects format again, but very clean
    # Note: Status column usually has 3 default labels with indexes 0, 1, 5/2.
    # We will try to override.
    
    labels_payload = {
        "labels": [
            {"name": "General"}, 
            {"name": "Alameda"}, 
            {"name": "Fresno"}, 
            {"name": "Ventura"}
        ]
    }
    
    mutation = """
    mutation ($board_id: ID!, $defaults: JSON!) {
        create_column (board_id: $board_id, title: "Suggested Location", column_type: status, defaults: $defaults) {
            id
        }
    }
    """
    
    variables = {
        "board_id": int(MONDAY_BOARD_ID),
        "defaults": labels_payload
    }
    
    resp = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers)
    data = resp.json()
    
    if "data" in data and data["data"]["create_column"]:
        col_id = data["data"]["create_column"]["id"]
        print(f"Created Status Column! ID: {col_id}")
        print("\n--- UPDATE CONFIG.PY ---")
        print(f"SUGGESTED_LOC_STATUS_ID = '{col_id}'")
        return col_id
    else:
        print("Failed to create with labels:", data)
        # Fallback: Create Standard Status Column (Defaults)
        print("Fallback: Creating standard Status column...")
        mutation_fallback = """
        mutation ($board_id: ID!) {
            create_column (board_id: $board_id, title: "Suggested Location", column_type: status) {
                id
            }
        }
        """
        resp2 = requests.post(url, json={"query": mutation_fallback, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
        data2 = resp2.json()
        if "data" in data2 and data2["data"]["create_column"]:
            col_id = data2["data"]["create_column"]["id"]
            print(f"Created Standard Status Column! ID: {col_id}")
            print("IMPORTANT: You must manually rename the labels in Monday UI to: Alameda, Fresno, Ventura.")
            print("\n--- UPDATE CONFIG.PY ---")
            print(f"SUGGESTED_LOC_STATUS_ID = '{col_id}'")
            return col_id
        return None

if __name__ == "__main__":
    setup_monday_v10()
