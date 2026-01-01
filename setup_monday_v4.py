import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def setup_monday_v4():
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
    
    # Check for "Magnitude Score"
    magnitude_id = None
    certainty_id = None
    
    for col in board["columns"]:
        if "Magnitude Score" in col["title"]:
            print(f"Column 'Magnitude Score' already exists (ID: {col['id']})")
            magnitude_id = col["id"]
        if "Certainty Index" in col["title"]:
             print(f"Column 'Certainty Index' already exists (ID: {col['id']})")
             certainty_id = col["id"]
            
    # 2. Create if missing
    if not magnitude_id:
        print("Creating 'Magnitude Score' column...")
        mutation_mag = """
        mutation ($board_id: ID!) {
            create_column (board_id: $board_id, title: "Magnitude Score", column_type: numbers) {
                id
            }
        }
        """
        resp = requests.post(url, json={"query": mutation_mag, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
        data = resp.json()
        if "data" in data:
            magnitude_id = data["data"]["create_column"]["id"]
            print(f"Created Magnitude! ID: {magnitude_id}")

    if not certainty_id:
        print("Creating 'Certainty Index' column...")
        mutation_cert = """
        mutation ($board_id: ID!) {
            create_column (board_id: $board_id, title: "Certainty Index", column_type: text) {
                id
            }
        }
        """
        resp = requests.post(url, json={"query": mutation_cert, "variables": {"board_id": int(MONDAY_BOARD_ID)}}, headers=headers)
        data = resp.json()
        if "data" in data:
            certainty_id = data["data"]["create_column"]["id"]
            print(f"Created Certainty! ID: {certainty_id}")

    print("\n--- UPDATE CONFIG.PY WITH THESE IDS ---")
    print(f"MAGNITUDE_COLUMN_ID = '{magnitude_id}'")
    print(f"CERTAINTY_COLUMN_ID = '{certainty_id}'")

if __name__ == "__main__":
    setup_monday_v4()
