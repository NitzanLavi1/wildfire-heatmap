import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID, SUGGESTED_LOC_DROPDOWN_ID

def create_text_column_fallback():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    # 1. DELETE existing column (just in case ID lingers)
    # We ignore errors here.
    
    print("Creating 'Suggested Location' (TEXT FALLBACK)...")
    
    mutation_create = """
    mutation ($board_id: ID!) {
        create_column (board_id: $board_id, title: "Suggested Location", column_type: text) {
            id
        }
    }
    """
    
    resp = requests.post(url, json={"query": mutation_create, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
    data = resp.json()
    
    if "data" in data and data["data"]["create_column"]:
        new_col_id = data["data"]["create_column"]["id"]
        print(f"Created 'Suggested Location'! ID: {new_col_id}")
        print("\n--- UPDATE CONFIG.PY ---")
        print(f"SUGGESTED_LOC_DROPDOWN_ID = '{new_col_id}'")
    else:
        print("Failed to create:", data)

if __name__ == "__main__":
    create_text_column_fallback()
