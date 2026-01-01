import os
import time
import json
import requests
import feedparser
from datetime import datetime
from apify_client import ApifyClient
from google import genai
import config

# Configuration
MOCK_MODE = True
MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": config.MONDAY_API_KEY,
    "API-Version": "2023-10"
}

# Initialize Clients
apify_client = ApifyClient(config.APIFY_TOKEN)
# Initialize Google GenAI Client
client = genai.Client(api_key=config.GEMINI_API_KEY)

class StateEngine:
    def __init__(self):
        self.seen_signal_ids = set()

    def fetch_signals(self):
        """Fetches new signals from RSS, Twitter (Apify), and Reddit (Apify)."""
        signals = []
        print("[Intake] Fetching new signals...")

        # 1. RSS Feeds
        for source, url in config.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: # Top 5 recent
                    if entry.id not in self.seen_signal_ids:
                        signals.append({
                            "type": "RSS",
                            "source": source,
                            "text": f"{entry.title}: {entry.summary}",
                            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed) if 'published_parsed' in entry else str(datetime.now())
                        })
                        self.seen_signal_ids.add(entry.id)
            except Exception as e:
                print(f"Error fetching RSS {source}: {e}")

        # 2. Apify (Twitter/Reddit) - Simulated/Placeholder
        if config.ACTOR_TWITTER and config.APIFY_TOKEN != "YOUR_APIFY_TOKEN":
            try:
                pass 
            except Exception as e:
                print(f"Error fetching Apify: {e}")

        print(f"[Intake] Found {len(signals)} new signals.")
        return signals

    def geo_code_signal(self, signal_text):
        """Uses Gemini to extract District/County from text."""
        if config.MOCK_MODE:
            # In Mock Mode, we try to match the signal text to one of our active scenarios
            from simulation_scenarios import SCENARIOS
            for scenario in SCENARIOS:
                # Check if any signal in this scenario matches the input text
                for s in scenario['signals']:
                    if s['text'] == signal_text:
                        print(f"[Mock] Matched signal to district: {scenario['district']}")
                        return {"district": scenario['district'], "confidence": "High"}
            
            # Fallback if no exact match (shouldn't happen with controlled loop)
            return {"district": "Unknown", "confidence": "Low"}

        try:
            prompt = """
            You are a California GEO-INT expert. Extract the 'District' or 'County' name from the wildfire report. 
            Return ONLY the JSON: {"district": "Name", "confidence": "High/Medium/Low"}. 
            If unknown, return {"district": "Unknown", "confidence": "Low"}.
            Signal Text:
            """ + signal_text
            
            # Updated to use new Client SDK
            response = client.models.generate_content(
                model='gemini-2.0-flash-lite-preview',
                contents=prompt
            )
            time.sleep(2) # Modest rate limit
            content = response.text
            # Clean up potential markdown blocks
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"Error in geocoding: {e}")
            return {"district": "Unknown", "confidence": "Low"}

    def fetch_current_state(self, district_name):
        """Fetches the current item for a district from Monday.com using District Name column."""
        # Using the dedicated District Name column (text_mkz34fzt) to lookup the item
        query = f"""
        query {{
            boards (ids: {config.MONDAY_DISTRICT_BOARD_ID}) {{
                items_page (query_params: {{rules: [{{column_id: "text_mkz34fzt", compare_value: ["{district_name}"], operator: any_of}}]}}) {{
                    items {{
                        id
                        name
                        column_values {{
                            id
                            text
                            ... on LongTextValue {{
                                text
                            }}
                            ... on NumbersValue {{
                                number
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        response = requests.post(MONDAY_API_URL, json={'query': query}, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
            return items[0] if items else None
        return None

    def fetch_raw_input(self):
        """Checks the Monday board for any item with text in the Raw Input column."""
        query = f"""
        query {{
            boards (ids: {config.MONDAY_DISTRICT_BOARD_ID}) {{
                items_page (limit: 50) {{
                    items {{
                        id
                        name
                        column_values {{
                            id
                            text
                        }}
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
                
                for item in items:
                    for cv in item['column_values']:
                        if cv['id'] == config.RAW_INPUT_COLUMN_ID and cv['text'] and cv['text'].strip():
                            print(f"[Override] Found Raw Input for {item['name']}: {cv['text']}")
                            return item['name'], item, cv['text']
            return None, None, None
        except Exception as e:
            print(f"Error checking raw input: {e}")
            return None, None, None

    def clear_raw_input(self, item_id):
        """Clears the Raw Input column after processing."""
        query = """
        mutation ($item_id: ID!, $board_id: ID!, $column_values: JSON!) {
            change_multiple_column_values(item_id: $item_id, board_id: $board_id, column_values: $column_values) {
                id
            }
        }
        """
        variables = {
            "item_id": int(item_id),
            "board_id": int(config.MONDAY_DISTRICT_BOARD_ID),
            "column_values": json.dumps({config.RAW_INPUT_COLUMN_ID: ""})
        }
        try:
            requests.post(MONDAY_API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
            print(f"[Override] Cleared Raw Input for item {item_id}")
        except Exception as e:
            print(f"Error clearing raw input: {e}")

    def synthesize_state(self, district, current_state, new_signals, raw_input=None):
        """Uses Gemini to synthesize new state from old state + new signals."""
        
        current_summary = "No active reports."
        current_headline = f"{district} Status"
        
        if current_state:
            # Parse column values - simplifying extraction
            for cv in current_state['column_values']:
                if cv['id'] == 'text_mkz3w205': # Headline
                    current_headline = cv['text']
                elif cv['id'] == 'long_text_mkz3rga9': # Deep Summary
                    current_summary = cv['text']

        if raw_input:
            signals_text = f"*** PRIORITY OVERRIDE ***\nMANUAL FIELD INPUT: {raw_input}\nContext: Ignore previous contradictory signals. This is ground truth."
        else:
            signals_text = "\n".join([f"- {s['type']} ({s['source']}): {s['text']}" for s in new_signals])

        if config.MOCK_MODE:
            # Find the scenario for this district
            from simulation_scenarios import SCENARIOS
            for scenario in SCENARIOS:
                if scenario['district'] == district:
                    print(f"[Mock] Returning simulated state for {district}...")
                    return scenario['ai_state']
            
            # If no scenario match but we have raw input, proceed to AI generation normally (Hybrid Mode)
            if not raw_input:
                return None

        prompt = f"""
        Role: Tactical Fire Commander AI
        Task: Update the operational status for {district}.
        
        Current Status:
        Headline: {current_headline}
        Summary: {current_summary}
        
        New Incoming Signals:
        {signals_text}
        
        Instructions:
        1. **URGENT**: The 'headline' field must be a "SUPER SUMMARY" - a single, comprehensive sentence describing the incident itself.
           - **CRITICAL**: Do NOT include status prefixes like "Monitor:", "Act:", "Watch:", or "Critical:". Just the description.
        2. **DEEP SUMMARY**: Write a FULL PARAGRAPH (3-4 sentences) explaining the situation in detail, covering fire behavior, threats, and response operations.
        
        **PROCESS INTEGRITY RULES**:
        3. **Two-Source Rule**: Do NOT raise Critical (Mag > 7) status based on social media alone. Use multi-source corroboration (Official + Social) or Manual Input.
        4. **Digital Fencing**: Strictly ignore reports located outside of {district} county limits.
        5. **Resource Bias**: Prioritize OFFICIAL sensors (NASA, Fire Dept feeds) over high-volume social media noise. 
        6. **Data Conflict**: If sources contradict (e.g. "Road Open" vs "Road Closed"), trust the MOST RECENT OFFICIAL source.
        7. **Temporal Sync**: Discard "breaking news" that opposes ground truth from the last 20 minutes unless it is verified Official Intel.
        8. **Slang Filter**: Beware of metaphors (e.g. "this party is fire"). Verify physical threat context.

        9. Analyze the situation and extract STRICTLY NUMERICAL DATA. Estimate if necessary based on text.
        10. If "MANUAL FIELD INPUT" is present, treat it as 95% certainty ground truth (Overrides all other rules).
        11. Generate a 'Certainty Score' (0-100) based on data reliability and corroboration.
        12. Determine specific statuses:
           - Response Status: "Act", "Watch", "Monitor", "Resolved"
           - Power/Water/Comms: "Functional", "Partially Damaged", "Down"
           - District Code: Extract if available (e.g., "VNC-12")
           - Geographic Center: Approximate address or city center.
        13. **GENERATE CATEGORY SUMMARIES**:
           - For each category below, write a SHORT, qualitative sentence explaining *what is happening* (e.g., "Evacuations in progress for North Zone," "Power lines down on Hwy 1").
           - Human Safety, Infrastructure, Intensity, Environmental, Operational.

        Return JSON ONLY:
        {{
            "headline": "...",
            "deep_summary": "...",
            "magnitude": 5,
            "response_status": "Monitor",
            "power_status": "Functional",
            "water_status": "Functional",
            "comms_status": "Functional",
            "district_code": "...",
            "geographic_center": "...",
            "certainty_score": 85,
            
            "human_safety_summary": "...",
            "infrastructure_summary": "...",
            "intensity_summary": "...",
            "environmental_summary": "...",
            "operational_summary": "...",
            
            "fatalities": 0,
            "injured": 0,
            "people_threatened": 0,
            
            "structures_destroyed": 0,
            "structures_threatened": 0,
            "infra_impact_score": 0,
            
            "acres_burned": 0,
            "containment_pct": 0,
            "aqi": 0,
            
            "personnel_count": 0,
            "apparatus_count": 0
        }}
        """
        
        try:
            # Updated to use new Client SDK
            response = client.models.generate_content(
                model='gemini-2.0-flash-lite-preview',
                contents=prompt
            )
            time.sleep(2) # Rate limit check
            content = response.text
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"Error in synthesis: {e}")
            return None

    def update_monday_board(self, district, new_state, item_id=None):
        """Updates or Creates the item in Monday.com."""
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Geocoding Mapping for Demo (Static Coordinates to ensure they appear on map)
        DISTRICT_COORDINATES = {
            "Napa": {"lat": 38.5025, "lng": -122.2654, "address": "St. Helena, CA"},
            "Shasta": {"lat": 40.5866, "lng": -122.3917, "address": "Redding, CA"},
            "San Diego": {"lat": 33.1959, "lng": -117.3790, "address": "Oceanside, CA"},
            "Tahoe": {"lat": 38.9399, "lng": -119.9772, "address": "South Lake Tahoe, CA"},
            "Los Angeles": {"lat": 34.0259, "lng": -118.7798, "address": "Malibu, CA"},
            "Yosemite": {"lat": 37.8651, "lng": -119.5383, "address": "Tuolumne Meadows, CA"},
            "Riverside": {"lat": 33.9425, "lng": -117.2297, "address": "Moreno Valley, CA"},
            "Monterey": {"lat": 36.2704, "lng": -121.8081, "address": "Big Sur, CA"},
            "Alameda": {"lat": 37.8272, "lng": -122.21, "address": "Oakland Hills, CA"},
            "Siskiyou": {"lat": 41.7354, "lng": -122.6345, "address": "Yreka, CA"},
            "San Bernardino": {"lat": 33.8734, "lng": -115.9010, "address": "Joshua Tree NP, CA"}
        }
        
        # Determine Group based on Magnitude
        magnitude = new_state.get('magnitude', 0)
        group_id = config.GROUP_IDS["STABLE"] # Default
        
        if magnitude >= 7:
            group_id = config.GROUP_IDS["CRITICAL"]
        elif magnitude >= 4:
            group_id = config.GROUP_IDS["HIGH_WATCH"]
        elif magnitude >= 2:
            group_id = config.GROUP_IDS["MONITORING"]
        else:
            group_id = config.GROUP_IDS["STABLE"]
            
        # Prepare Logic for Status Columns (sending label text)
        
        # Resolve Coordinates
        coords = DISTRICT_COORDINATES.get(district, {"lat": 37.0, "lng": -119.0, "address": "California, USA"})

        column_values = {
            "text_mkz3w205": new_state.get('headline', ""),
            "long_text_mkz3rga9": f"{new_state.get('deep_summary', '')}\n\n[Certainty Score: {new_state.get('certainty_score', 'N/A')}/100]", 
            "numeric_mkz364ep": magnitude,
            "color_mkz3fk3v": {"label": new_state.get('response_status', "Monitor")}, 
            "color_mkz3kz4n": {"label": new_state.get('power_status', "Functional")}, 
            "color_mkz3y5ey": {"label": new_state.get('water_status', "Functional")}, 
            "color_mkz3st2m": {"label": new_state.get('comms_status', "Functional")}, 
            "text_mkz34fzt": district, # CRITICAL: Storing District Name here for stable lookup
            "location_mkz36zby": {"lat": coords['lat'], "lng": coords['lng'], "address": coords['address']}, 
            "date_mkz3zaed": {"date": date_str},
            
            # Extended Categories (Descriptive Summaries)
            config.HUMAN_SAFETY_COLUMN_ID: new_state.get('human_safety_summary', 'No significant activity.'),
            config.INFRASTRUCTURE_COLUMN_ID: new_state.get('infrastructure_summary', 'Stable.'),
            config.INTENSITY_COLUMN_ID: new_state.get('intensity_summary', 'Stable.'),
            config.ENVIRONMENTAL_COLUMN_ID: new_state.get('environmental_summary', 'Normal.'),
            config.OPERATIONAL_COLUMN_ID: new_state.get('operational_summary', 'Monitoring.'),

            # NEW QUANTITATIVE COLUMNS
            config.FATALITIES_COL_ID: new_state.get("fatalities", 0),
            config.INJURED_COL_ID: new_state.get("injured", 0),
            config.PEOPLE_THREATENED_COL_ID: new_state.get("people_threatened", 0),
            
            config.STRUCTURES_DESTROYED_COL_ID: new_state.get("structures_destroyed", 0),
            config.STRUCTURES_THREATENED_COL_ID: new_state.get("structures_threatened", 0),
            config.INFRA_IMPACT_SCORE_COL_ID: new_state.get("infra_impact_score", 0),
            
            config.ACRES_BURNED_COL_ID: new_state.get("acres_burned", 0),
            config.CONTAINMENT_COL_ID: new_state.get("containment_pct", 0),
            config.AQI_COL_ID: new_state.get("aqi", 0),
            
            config.PERSONNEL_COUNT_COL_ID: new_state.get("personnel_count", 0),
            config.APPARATUS_COUNT_COL_ID: new_state.get("apparatus_count", 0)
        }
        
        print(f"\n[MONDAY PAYLOAD] Group: {group_id}, Data: {json.dumps(column_values, indent=2)}")
        
        if item_id:
            # Mutation to update columns
            query = """
            mutation ($item_id: ID!, $board_id: ID!, $column_values: JSON!) {
                change_multiple_column_values(item_id: $item_id, board_id: $board_id, column_values: $column_values) {
                    id
                }
            }
            """
            variables = {
                "item_id": int(item_id),
                "board_id": int(config.MONDAY_DISTRICT_BOARD_ID),
                "column_values": json.dumps(column_values)
            }
            print(f"[Monday] Updating existing district: {district}")
            
            # Execute update first
            try:
                requests.post(MONDAY_API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
                
                # Also update the Item Name to the Super Summary
                rename_query = """
                mutation ($item_id: ID!, $name: String!) {
                    change_item_name (item_id: $item_id, name: $name) {
                        id
                    }
                }
                """
                rename_vars = {"item_id": int(item_id), "name": new_state.get('headline', district)}
                requests.post(MONDAY_API_URL, json={'query': rename_query, 'variables': rename_vars}, headers=HEADERS)

                # THEN Move item to the correct group
                if group_id: 
                    move_query = """
                    mutation ($item_id: ID!, $group_id: String!, $board_id: ID!) {
                        move_item_to_group (item_id: $item_id, group_id: $group_id, board_id: $board_id) {
                            id
                        }
                    }
                    """
                    move_vars = {
                        "item_id": int(item_id),
                        "group_id": group_id,
                        "board_id": int(config.MONDAY_DISTRICT_BOARD_ID)
                    }
                    requests.post(MONDAY_API_URL, json={'query': move_query, 'variables': move_vars}, headers=HEADERS)
                    print(f"[Monday] Moved item {item_id} to group {group_id}")

            except Exception as e:
                print(f"Monday Update Exception: {e}")

        else:
            # Mutation to create using variables in specific group
            query = """
            mutation ($board_id: ID!, $group_id: String!, $item_name: String!, $column_values: JSON!) {
                create_item (board_id: $board_id, group_id: $group_id, item_name: $item_name, column_values: $column_values) {
                    id
                }
            }
            """
            variables = {
                "board_id": int(config.MONDAY_DISTRICT_BOARD_ID),
                "group_id": group_id,
                "item_name": new_state.get('headline', district), # Use Super Summary as Name
                "column_values": json.dumps(column_values)
            }
            print(f"[Monday] Creating new district: {district} in group {group_id}")

            # Execute
            try:
                response = requests.post(MONDAY_API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
                if response.status_code != 200 or 'errors' in response.json():
                    print(f"Monday API Error: {response.text}")
            except Exception as e:
                print(f"Monday Request Exception: {e}")

    def run_cycle(self):
        print(f"\n--- Starting Cycle: {datetime.now()} ---")
        
        # 0. Check for Manual Raw Input Override
        raw_district, raw_item, raw_text = self.fetch_raw_input()
        
        if raw_district and raw_text:
            print(f"\n[Cycle] PROCESSING OVERRIDE FOR {raw_district}")
            # Synthesize directly with raw input
            # If item exists, we might need its ID, but synthesize mainly needs 'district' for scope.
            # Passing raw_item as current_state is fine.
            
            # Since we lookup by Code now, 'raw_item' is the item found.
            # But wait, if found via raw_input loop, 'raw_item' is arguably the item we want to update.
            # 'raw_district' used to be name, but now name is summary.
            # So raw_district might be "Critical: Fire..."
            # We need to extract the real district name if possible, OR just update the ID we found.
            
            # Update logic: If found by ID, we use that ID.
            # We can pass raw_district (name) but synthesize mostly ignores it for Mock.
            # For Real AI, it uses it for content generation.
            
            new_state = self.synthesize_state(raw_district, raw_item, [], raw_input=raw_text)
            
            if new_state:
                # Force update
                self.update_monday_board(raw_district, new_state, item_id=raw_item['id'])
                # Clear the input
                self.clear_raw_input(raw_item['id'])
                # Export data for Dashboard
                self.export_dashboard_data(raw_district, new_state)
            return

        # 1. Intake
        if config.MOCK_MODE:
            # Simulate diverse signals from Scenarios
            import random
            from simulation_scenarios import SCENARIOS
            # Pick one random scenario per cycle to simulate active feed
            scenario = random.choice(SCENARIOS)
            
            # Simulate
            print(f"[Cycle] Simulating signal for {scenario['district']}...")
            
            # Get current state first (to maintain continuity if needed, or just overwrite for demo)
            # In mock mode, we usually just overwrite with the scenario state + variations
            
            # Check if item exists to get ID
            current_item = self.fetch_current_state(scenario['district'])
            current_id = current_item['id'] if current_item else None
            current_state = current_item # The item itself serves as state context
            
            new_state = scenario['ai_state'] # Directly use scenario state for demo purity
            
            self.update_monday_board(scenario['district'], new_state, item_id=current_id)
            
            # Export data for Dashboard
            self.export_dashboard_data(scenario['district'], new_state)

        else:
            # REAL LIVE MODE
            # A. Get list of all monitored districts from config or dynamic
            monitored_districts = GROUP_MAPPING.keys() # Using keys as district names effectively? No, values.
            # Flatten districts
            all_districts = []
            for k, v in GROUP_MAPPING.items():
                all_districts.extend(v)
                
            for district in all_districts:
                # 1. Fetch
                signals = self.fetch_signals(district)
                if not signals:
                    continue
                    
                # 2. Get State
                current_id, current_state = self.get_district_state(district)
                
                # 3. Synthesize
                new_state = self.synthesize_state(district, current_state, signals)
                
                if new_state:
                    # 4. Certainty Check
                    score = new_state.get('certainty_score', 0)
                    if score < config.CERTAINTY_THRESHOLD:
                        print(f"Skipping {district}: Certainty Score ({score}) below threshold ({config.CERTAINTY_THRESHOLD})")
                        continue
                    
                    self.update_monday_board(district, new_state, item_id=current_id)

                # Export data for Dashboard
                self.export_dashboard_data(district, new_state)

    def export_dashboard_data(self, district, state):
        """Exports the current state to a JSON file for the dashboard."""
        status_file = "live_status.json"
        
        # Load existing data
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        
        # Determine Color
        mag = state.get('magnitude', 0)
        if mag >= 7:
            color = "#ff0000" # Red - Critical / Act
        elif mag >= 4:
            color = "#FFD700" # Gold/Yellow - Watch
        elif mag >= 2:
            color = "#0000ff" # Blue - Monitor
        else:
            color = "#00ff00" # Green - Stable

        # Update District
        data[district] = {
            "magnitude": mag,
            "color": color,
            "headline": state.get('headline', ''),
            "updated": datetime.now().isoformat()
        }
        
        # Write back to JSON
        with open(status_file, "w") as f:
            json.dump(data, f, indent=2)

        # INJECT INTO HTML (Serverless Mode)
        html_file = "index.html"
        if os.path.exists(html_file):
            try:
                with open(html_file, "r") as f:
                    html_content = f.read()
                
                # Check if injection point exists
                if "var INJECTED_DATA =" in html_content:
                    import re
                    # Replace anything between "var INJECTED_DATA =" and ";" with the new JSON
                    new_js_line = f"var INJECTED_DATA = {json.dumps(data)};"
                    
                    pattern = r"var INJECTED_DATA = .*?;"
                    
                    if re.search(pattern, html_content):
                        new_html = re.sub(pattern, new_js_line, html_content, count=1)
                        with open(html_file, "w") as f:
                            f.write(new_html)
                        print(f"[Dashboard] Injected data into {html_file}")
            except Exception as e:
                print(f"[Dashboard] Error injecting HTML: {e}")

if __name__ == "__main__":
    engine = StateEngine()
    
    # Run loop
    while True:
        engine.run_cycle()
        print("Sleeping for 10 seconds (Test Mode)...")
        time.sleep(10)
