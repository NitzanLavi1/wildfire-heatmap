import requests
import json
import config

MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "API-Version": "2023-10"
}

NEW_COLUMNS = [
    {"title": "Human Life & Safety", "type": "long_text"},
    {"title": "Infrastructure Status", "type": "long_text"},
    {"title": "Disaster Intensity", "type": "long_text"},
    {"title": "Environmental Factors", "type": "long_text"},
    {"title": "Operational Response", "type": "long_text"}
]

def create_columns(board_id):
    for col in NEW_COLUMNS:
        query = """
        mutation ($board_id: ID!, $title: String!, $column_type: ColumnType!) {
            create_column (board_id: $board_id, title: $title, column_type: $column_type) {
                id
                title
            }
        }
        """
        variables = {
            "board_id": int(board_id),
            "title": col["title"],
            "column_type": col["type"]
        }
        
        try:
            response = requests.post(MONDAY_API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'create_column' in data['data']:
                    new_col = data['data']['create_column']
                    print(f"Created Column: {new_col['title']} -> ID: {new_col['id']}")
                else:
                    print(f"Error creating {col['title']}: {data}")
            else:
                print(f"HTTP Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    create_columns(config.MONDAY_DISTRICT_BOARD_ID)
