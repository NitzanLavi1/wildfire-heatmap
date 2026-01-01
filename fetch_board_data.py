import requests
import json
import config

URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "Content-Type": "application/json"
}

QUERY = f"""
query {{
  boards(ids: [{config.MONDAY_DISTRICT_BOARD_ID}]) {{
    name
    items_page(limit: 500) {{
      items {{
        id
        name
        column_values {{
          id
          text
          value
          type
        }}
      }}
    }}
  }}
}}
"""

def fetch_data():
    print(f"Fetching data from Monday.com Board ID: {config.MONDAY_DISTRICT_BOARD_ID}...")
    try:
        response = requests.post(URL, json={"query": QUERY}, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print("GraphQL Errors:", data["errors"])
            return

        # Simplify output structure if needed, but for now just dump the raw data
        with open("monday_board_dump.json", "w") as f:
            json.dump(data, f, indent=4)
        
        print("Success! Data saved to 'monday_board_dump.json'.")
        
        # Print a preview
        items = data['data']['boards'][0]['items_page']['items']
        print(f"Retrieved {len(items)} items.")
        if items:
            print(f"First Item: {items[0]['name']}")

    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_data()
