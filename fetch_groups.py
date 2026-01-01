import requests
import json
import config

MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "API-Version": "2023-10"
}

def fetch_groups(board_id):
    query = f"""
    query {{
        boards (ids: {board_id}) {{
            groups {{
                id
                title
            }}
        }}
    }}
    """
    try:
        response = requests.post(MONDAY_API_URL, json={'query': query}, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"API Errors: {data['errors']}")
                return

            boards = data.get('data', {}).get('boards', [])
            if boards:
                print(f"Groups for Board {board_id}:")
                for group in boards[0]['groups']:
                    print(f"ID: {group['id']}, Title: {group['title']}")
            else:
                print("No board found.")
        else:
            print(f"HTTP Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    fetch_groups(config.MONDAY_DISTRICT_BOARD_ID)
