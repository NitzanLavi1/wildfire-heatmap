import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def get_groups():
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    
    # Query to fetch groups from the specific board
    query = """
    query ($board_id: [ID!]) {
        boards (ids: $board_id) {
            groups {
                title
                id
            }
        }
    }
    """
    
    variables = {
        "board_id": int(MONDAY_BOARD_ID) if MONDAY_BOARD_ID.isdigit() else None
    }
    
    if not variables["board_id"]:
        print("Error: Invalid Board ID in config.py")
        return

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        data = response.json()
        
        if "errors" in data:
            print("Error fetching groups:", data["errors"])
            return

        groups = data["data"]["boards"][0]["groups"]
        print(f"\nFound {len(groups)} groups on Board {MONDAY_BOARD_ID}:\n")
        print(f"{'Group Name':<30} | {'Group ID'}")
        print("-" * 50)
        for group in groups:
            print(f"{group['title']:<30} | {group['id']}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    get_groups()
