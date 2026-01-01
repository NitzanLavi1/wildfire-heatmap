import requests
import json
from config import MONDAY_API_KEY, MONDAY_DISTRICT_BOARD_ID

MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "API-Version": "2023-10"
}

def fetch_all_items():
    print(f"Fetching items from board {MONDAY_DISTRICT_BOARD_ID}...")
    query = f"""
    query {{
        boards (ids: {MONDAY_DISTRICT_BOARD_ID}) {{
            items_page (limit: 500) {{
                items {{
                    id
                    name
                }}
            }}
        }}
    }}
    """
    try:
        response = requests.post(MONDAY_API_URL, json={'query': query}, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
            return items
        else:
            print(f"Error fetching items: {response.text}")
            return []
    except Exception as e:
        print(f"Exception fetching items: {e}")
        return []

def delete_item(item_id, item_name):
    query = """
    mutation ($item_id: ID!) {
        delete_item (item_id: $item_id) {
            id
        }
    }
    """
    variables = {"item_id": int(item_id)}
    try:
        response = requests.post(MONDAY_API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
        if response.status_code == 200:
            print(f"Deleted: {item_name} ({item_id})")
        else:
            print(f"Failed to delete {item_name}: {response.text}")
    except Exception as e:
        print(f"Exception deleting item {item_id}: {e}")

def clear_board():
    items = fetch_all_items()
    if not items:
        print("No items found to delete.")
        return

    print(f"Found {len(items)} items. Deleting...")
    for item in items:
        delete_item(item['id'], item['name'])
    
    print("Board cleared!")

if __name__ == "__main__":
    clear_board()
