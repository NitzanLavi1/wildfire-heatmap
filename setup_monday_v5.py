import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def setup_monday_v5():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    # 1. Fetch Board Column Structure
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
    
    resp = requests.post(url, json={"query": query_cols, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
    data = resp.json()
    board = data["data"]["boards"][0]
    
    # Check for "Post" column
    post_col_id = None
    
    for col in board["columns"]:
        if "Post" in col["title"]:
            print(f"Column 'Post' already exists (ID: {col['id']})")
            post_col_id = col['id']
            break
            
    # 2. Create if missing
    if not post_col_id:
        print("Creating 'Post' column (Long Text)...")
        mutation = """
        mutation ($board_id: ID!) {
            create_column (board_id: $board_id, title: "Post", column_type: long_text) {
                id
            }
        }
        """
        resp = requests.post(url, json={"query": mutation, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
        data = resp.json()
        if "data" in data:
            post_col_id = data["data"]["create_column"]["id"]
            print(f"Created 'Post' Column! ID: {post_col_id}")
        else:
            print("Failed to create column:", data)

    print("\n--- UPDATE CONFIG.PY WITH THIS ID ---")
    print(f"POST_COLUMN_ID = '{post_col_id}'")

if __name__ == "__main__":
    setup_monday_v5()
