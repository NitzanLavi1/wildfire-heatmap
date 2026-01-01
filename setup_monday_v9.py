import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def setup_monday_v9():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    print("Creating 'Suggested Location' (Tags) column...")
    mutation = """
    mutation ($board_id: ID!) {
        create_column (board_id: $board_id, title: "Suggested Location", column_type: tags) {
            id
        }
    }
    """
    
    resp = requests.post(url, json={"query": mutation, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
    data = resp.json()
    
    if "data" in data and data["data"]["create_column"]:
        col_id = data["data"]["create_column"]["id"]
        print(f"Created Tags Column! ID: {col_id}")
        print("\n--- UPDATE CONFIG.PY ---")
        print(f"SUGGESTED_LOC_TAGS_ID = '{col_id}'")
    else:
        print("Failed to create column:", data)

if __name__ == "__main__":
    setup_monday_v9()
