import requests
import json
import config

MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "API-Version": "2023-10"
}

def inspect_board(board_id):
    query = f"""
    query {{
        boards (ids: {board_id}) {{
            name
            columns {{
                id
                title
                type
                settings_str
            }}
        }}
    }}
    """
    response = requests.post(MONDAY_API_URL, json={'query': query}, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        boards = data.get('data', {}).get('boards', [])
        if boards:
            print(f"Board: {boards[0]['name']}")
            for col in boards[0]['columns']:
                print(f"ID: {col['id']}, Title: {col['title']}, Type: {col['type']}")
                if col['type'] == 'status' or col['type'] == 'color':
                     print(f"  Settings: {col.get('settings_str', '{}')}")
    else:
        print(f"Error fetching board info: {response.text}")

if __name__ == "__main__":
    board_id = "5089421649"
    print(f"Inspecting Board ID: {board_id}...")
    inspect_board(board_id)
