import requests
import json
from datetime import datetime
from geopy.distance import geodesic
from config import (
    MONDAY_API_KEY, MONDAY_BOARD_ID, GROUP_MAPPING, 
    SUGGESTED_LOC_COLUMN_ID, MAGNITUDE_COLUMN_ID, 
    CERTAINTY_COLUMN_ID, POST_COLUMN_ID, 
    VERIFICATION_COLUMN_ID, GENERAL_DISPATCH_GROUP_ID, 
    SUGGESTED_LOC_STATUS_ID, KNOWN_LOCATIONS, 
    DATE_COLUMN_ID, MONDAY_COMPLEXITY_BUDGET,
    SOURCE_LINK_COLUMN_ID, LOCATION_COLUMN_ID, EVACUATION_COLUMN_ID
)

class MondayIntegration:
    def __init__(self):
        self.api_url = "https://api.monday.com/v2"
        self.headers = {"Authorization": MONDAY_API_KEY}
        self.complexity_used = 0

    def determine_closest_location_and_group(self, event_lat, event_lon):
        """
        Calculates distance to Known Locations (Alameda, Fresno, Ventura)
        and returns the closest one + its group ID.
        """
        if not event_lat or not event_lon:
            return GENERAL_DISPATCH_GROUP_ID, "General"

        closest_loc = "General"
        min_dist = float('inf')
        
        for name, coords in KNOWN_LOCATIONS.items():
            dist = geodesic((event_lat, event_lon), coords).kilometers
            if dist < min_dist:
                min_dist = dist
                closest_loc = name
                
        group_id = GENERAL_DISPATCH_GROUP_ID
        if closest_loc == "Alameda": group_id = "group_mkz0tj87"
        elif closest_loc == "Fresno": group_id = "topics"
        elif closest_loc == "Ventura": group_id = "group_title"
        
        return group_id, closest_loc

    def push_incident(self, event_data):
        """
        Pushes a complex JSON object to Monday.com with Geospatial Routing & Status Dropdown.
        """
        source_name = event_data.get("source_name", "Unknown")
        is_official = "Official" in source_name or "OFFICIAL" in source_name or "NASA" in source_name
        
        # Extract coordinates
        coords = event_data.get('coordinates', (0,0))
        lat, lon = coords
            
        # 1. Calculate Closest Location (Geospatial)
        qs_group_id, suggested_location = self.determine_closest_location_and_group(lat, lon)
        
        # 2. Smart Status Mapping
        status_label = None
        priority = event_data.get("priority", "Low").capitalize()
        # Default Board Labels
        priority_map = {"High": "Stuck", "Medium": "Working on it", "Low": "Done"}
        mapped_priority = priority_map.get(priority, "Working on it")

        if suggested_location == "Alameda": status_label = "Alameda"
        elif suggested_location == "Ventura": status_label = "Ventura"
        elif suggested_location == "Fresno": status_label = "Fresno"
        
        # 3. Routing Logic
        verification_status_label = "Working on it" # Default for TBD
        final_group_id = GENERAL_DISPATCH_GROUP_ID 
        
        if is_official:
            verification_status_label = "Done" # Confirmed
            final_group_id = qs_group_id 
        else:
             verification_status_label = "Working on it"
             final_group_id = GENERAL_DISPATCH_GROUP_ID
        
        query = """
        mutation ($board_id: ID!, $group_id: String!, $item_name: String!, $column_values: JSON!) {
            create_item (board_id: $board_id, group_id: $group_id, item_name: $item_name, column_values: $column_values) {
                id
            }
        }
        """
        
        location_value = None
        if lat and lon:
             location_value = {
                 "lat": str(lat), 
                 "lng": str(lon), 
                 "address": f"Coords: {lat}, {lon}"
             }

        # 4. Date Formatting
        event_date_str = ""
        raw_ts = event_data.get("timestamp")
        if raw_ts:
            try:
                # Assuming ISO format
                dt_obj = datetime.fromisoformat(raw_ts.replace('Z', '+00:00'))
                event_date_str = dt_obj.strftime('%Y-%m-%d')
            except Exception:
                event_date_str = ""

        column_values = {
            "status": {"label": mapped_priority}, 
            EVACUATION_COLUMN_ID: event_data.get("evacuation_status", "Unknown"),
            SOURCE_LINK_COLUMN_ID: {"url": event_data.get("source_link", ""), "text": source_name},
            LOCATION_COLUMN_ID: location_value,
            # For this board, we'll skip suggested_loc_status if it's not present or map it to status
            MAGNITUDE_COLUMN_ID: round(event_data.get("magnitude", 1), 2),
            CERTAINTY_COLUMN_ID: event_data.get("certainty_index", "N/A"),
            POST_COLUMN_ID: {"text": event_data.get("raw_text", event_data.get("headline", ""))},
            VERIFICATION_COLUMN_ID: {"label": verification_status_label},
            DATE_COLUMN_ID: {"date": event_date_str} if event_date_str else {}
        }

        if MONDAY_API_KEY.startswith("YOUR"): return True

        variables = {
            "board_id": int(MONDAY_BOARD_ID) if MONDAY_BOARD_ID.isdigit() else 12345,
            "group_id": final_group_id,
            "item_name": event_data.get("headline", "Use Headline"),
            "column_values": json.dumps(column_values)
        }

        try:
            resp = requests.post(
                self.api_url, 
                json={"query": query, "variables": variables}, 
                headers=self.headers
            )
            response_json = resp.json()
            
            # 5. Complexity Tracking
            if "extensions" in response_json and "complexity" in response_json["extensions"]:
                cost = response_json["extensions"]["complexity"]["before"]
                self.complexity_used += cost
                if self.complexity_used > MONDAY_COMPLEXITY_BUDGET:
                    print("[CRITICAL] Monday API Complexity Budget Exceeded!")
            
            if "errors" in response_json:
                print(f"    [Monday API Error]: {response_json['errors'][0]['message']}")
                return False
            return resp.status_code == 200
        except Exception as e:
            print(f"    [Request Exception]: {e}")
            return False
