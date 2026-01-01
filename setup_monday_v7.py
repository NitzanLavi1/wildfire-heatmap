import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def setup_monday_v7():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    # 1. Create Dropdown Column
    print("Creating 'Suggested Location' Dropdown column...")
    mutation = """
    mutation ($board_id: ID!) {
        create_column (board_id: $board_id, title: "Suggested Location (Drop)", column_type: dropdown) {
            id
        }
    }
    """
    
    resp = requests.post(url, json={"query": mutation, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
    data = resp.json()
    
    if "data" in data:
        col_id = data["data"]["create_column"]["id"]
        print(f"Created Dropdown Column! ID: {col_id}")
        
        print("\n--- UPDATE CONFIG.PY ---")
        print(f"SUGGESTED_LOC_DROPDOWN_ID = '{col_id}'")
    else:
        print("Failed to create column (it might already exist?):", data)
        # Try to find it if failed
        query_cols = """
        query ($board_id: [ID!]) {
            boards (ids: $board_id) {
                columns {
                    title
                    id
                    type
                }
            }
        }
        """
        resp2 = requests.post(url, json={"query": query_cols, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
        for col in resp2.json()["data"]["boards"][0]["columns"]:
            if "Suggested Location (Drop)" in col["title"]:
                print(f"Found existing ID: {col['id']}")

if __name__ == "__main__":
    setup_monday_v7()
