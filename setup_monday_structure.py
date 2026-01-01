import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def setup_monday_board():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    # 1. Fetch Board Column Structure to see if it exists
    query_cols = """
    query ($board_id: [ID!]) {
        boards (ids: $board_id) {
            columns {
                title
                id
                type
            }
            groups {
                title
                id
            }
        }
    }
    """
    
    resp = requests.post(url, json={"query": query_cols, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
    data = resp.json()
    board = data["data"]["boards"][0]
    
    # Check for "Suggested Location"
    sugg_loc_id = None
    for col in board["columns"]:
        if "Suggested Location" in col["title"]:
            print(f"Column 'Suggested Location' already exists (ID: {col['id']})")
            sugg_loc_id = col["id"]
            break
            
    # 2. If not exists, Create it
    if not sugg_loc_id:
        print("Creating 'Suggested Location' column...")
        mutation_create = """
        mutation ($board_id: ID!) {
            create_column (board_id: $board_id, title: "Suggested Location", column_type: text) {
                id
            }
        }
        """
        resp_create = requests.post(url, json={"query": mutation_create, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
        data_create = resp_create.json()
        if "data" in data_create:
            sugg_loc_id = data_create["data"]["create_column"]["id"]
            print(f"Created successfully! ID: {sugg_loc_id}")
        else:
            print("Failed to create column:", data_create)
            
    print("\n--- CONFIGURATION DATA ---")
    print(f"SUGGESTED_LOC_COLUMN_ID = '{sugg_loc_id}'")
    
    print("\nGROUPS:")
    for group in board["groups"]:
        print(f"{group['title']}: {group['id']}")

if __name__ == "__main__":
    setup_monday_board()
