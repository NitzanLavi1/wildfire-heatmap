import requests
import json
import os
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

def update_labels():
    board_id = MONDAY_BOARD_ID
    headers = {"Authorization": MONDAY_API_KEY}
    api_url = "https://api.monday.com/v2"

    mappings = [
        ("status", {"0": "Low", "1": "Medium", "2": "High"}),
        ("color_mkz2ajkv", {"0": "TBD", "1": "Confirmed"})
    ]

    for col_id, labels in mappings:
        print(f"Updating {col_id}...")
        settings = json.dumps({"labels": labels})
        query = """
        mutation ($board_id: ID!, $column_id: String!, $settings: String!) {
            update_column_settings (board_id: $board_id, column_id: $column_id, settings: $settings) {
                id
            }
        }
        """
        variables = {"board_id": str(board_id), "column_id": col_id, "settings": settings}
        resp = requests.post(api_url, json={"query": query, "variables": variables}, headers=headers)
        print(f"Response: {resp.status_code}, {resp.text}")

if __name__ == "__main__":
    update_labels()
