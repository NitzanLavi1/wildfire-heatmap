import requests
import json
import config

MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "API-Version": "2023-10"
}

def get_board_id_by_name(board_name):
    query = """
    query {
        boards {
            id
            name
        }
    }
    """
    response = requests.post(MONDAY_API_URL, json={'query': query}, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        boards = data.get('data', {}).get('boards', [])
        print("Available boards:")
        for board in boards:
            print(f"- {board['name']} (ID: {board['id']})")
            if board['name'].lower() == board_name.lower():
                return board['id']
    else:
        print(f"Error fetching boards: {response.text}")
    return None

def get_board_items(board_id):
    query = f"""
    query {{
        boards (ids: {board_id}) {{
            name
            items_page {{
                items {{
                    id
                    name
                    column_values {{
                        text
                        column {{
                            title
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    response = requests.post(MONDAY_API_URL, json={'query': query}, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching items: {response.text}")
        return None

if __name__ == "__main__":
    board_name = "Rapid Assessment Form"
    print(f"Searching for board: '{board_name}'...")
    board_id = get_board_id_by_name(board_name)
    
    if board_id:
        print(f"Found board ID: {board_id}")
        data = get_board_items(board_id)
        if data:
            print(json.dumps(data, indent=2))
        else:
            print("Failed to fetch items.")
    else:
        print(f"Board '{board_name}' not found.")
