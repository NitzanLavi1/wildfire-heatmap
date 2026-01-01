import os
import json
import pandas as pd
import folium
from folium.plugins import HeatMapWithTime
from datetime import datetime
from apify_client import ApifyClient
from config import APIFY_TOKEN, ACTOR_TWITTER, HASHTAGS

def fetch_historical_data():
    """Fetches historical wildfire data from Apify actors."""
    print("Fetching historical data from Apify...")
    client = ApifyClient(APIFY_TOKEN)
    query = " OR ".join(HASHTAGS)
    
    # In a real scenario, we'd iterate over multiple sources
    # Here we simulate/fetch a batch of results
    try:
        run_input = {"searchTerms": [query], "maxItems": 100}
        run = client.actor(ACTOR_TWITTER).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Fetched {len(items)} items.")
        return items
    except Exception as e:
        print(f"Apify Error: {e}. Falling back to mock data for demonstration.")
        return generate_mock_historical_data()

def generate_mock_historical_data():
    """Generates mock data if Apify fetch fails or for demonstration."""
    import random
    mock_data = []
    # California bounding box
    # Lat: 32.5 to 42.0, Lon: -124.3 to -114.1
    
    dates = pd.date_range(start="2025-07-01", periods=14).strftime('%Y-%m-%d').tolist()
    
    for date in dates:
        num_reports = random.randint(5, 20)
        for _ in range(num_reports):
            # Focus clusters around the hubs
            hub = random.choice([(37.6017, -121.7195), (36.7378, -119.7871), (34.2805, -119.2945)])
            lat = hub[0] + random.uniform(-0.5, 0.5)
            lon = hub[1] + random.uniform(-0.5, 0.5)
            mock_data.append({
                "text": "Wildfire report",
                "timestamp": date,
                "lat": lat,
                "lon": lon
            })
    return mock_data

def process_data_for_heatmap(items):
    """Structures data for HeatMapWithTime with Dynamic Weights and Validation."""
    print("Processing data for heatmap...")
    df = pd.DataFrame(items)
    
    # 1. Coordinate Validation
    # Drop rows without valid lat/lon
    df = df.dropna(subset=['lat', 'lon'])
    
    # 2. Date Processing
    # Ensure timestamp is datetime and sort
    df['dt_obj'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['dt_obj'].dt.strftime('%Y-%m-%d')
    df = df.sort_values('dt_obj')
    
    unique_dates = df['date'].unique().tolist()
    
    heat_data = []
    for date in unique_dates:
        day_data = df[df['date'] == date]
        # Normalize weight between 0.2 and 1.0 (magnitude 0 to 10)
        points = []
        for _, row in day_data.iterrows():
            try:
                mag = float(row.get('magnitude', 5.0))
                weight = max(0.2, min(mag / 10.0, 1.0))
                points.append([float(row['lat']), float(row['lon']), weight])
            except (ValueError, TypeError):
                continue
        heat_data.append(points)
        
    return heat_data, unique_dates

def create_heatmap(heat_data, dates):
    """Generates the Master Folium map with Dark Theme and Correct Scaling."""
    print("Generating Master Folium map...")
    
    if not heat_data:
        print("Warning: No heat data to visualize.")
        return

    # 1. Base Map: Dark Matter for high contrast
    m = folium.Map(
        location=[37.2, -119.5], 
        zoom_start=6, 
        tiles='cartodb dark_matter',
        control_scale=True,
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        prefer_canvas=True
    )
    
    # 2. Fire Gradient: From deep embers to white-hot core
    fire_gradient = {
        0.2: '#b30000', # Deep Red
        0.4: '#e34a33', # Red-Orange
        0.6: '#fc8d59', # Orange
        0.7: '#fdcc8a', # Light Orange
        0.9: '#fef0d9', # Glow
        1.0: '#ffffff'  # White Hot Core
    }
    
    # 3. HeatMapWithTime Integration
    # Radius/Blur adjusted to prevent Leaflet IndexSizeError
    HeatMapWithTime(
        data=heat_data,
        index=dates,
        auto_play=False,
        max_opacity=0.9,
        radius=25,  # Increased for better visibility
        blur=1,     # Drastically reduced for sharper, visible points
        gradient=fire_gradient
    ).add_to(m)
    
    # 4. Master UI: Glassmorphism Overlay
    title_html = f'''
             <div style="position: fixed; 
                         top: 20px; right: 20px; width: 300px; height: auto; 
                         background: rgba(15, 15, 15, 0.75); 
                         backdrop-filter: blur(12px);
                         -webkit-backdrop-filter: blur(12px);
                         border: 1px solid rgba(255, 255, 255, 0.1);
                         border-radius: 16px;
                         z-index:9999; font-size:14px;
                         color: white; padding: 25px;
                         font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                         box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6);">
                 <h2 style="margin: 0 0 10px 0; color: #ff5f00; letter-spacing: 1.5px; font-weight: 800; text-transform: uppercase; font-size: 18px;">Wildfire Radar</h2>
                 <p style="margin: 0; opacity: 0.7; font-size: 11px; line-height: 1.6; font-weight: 400;">
                    Temporal Heat Analysis of California Wildfire Progression.<br>
                    Coverage: {dates[0]} to {dates[-1]}
                 </p>
                 <div style="margin-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 600; font-size: 12px; color: #eee;">Heat Intensity</span>
                    </div>
                    <div style="height: 8px; border-radius: 4px; background: linear-gradient(to right, #b30000, #fc8d59, #fdcc8a, #ffffff);"></div>
                    <div style="display: flex; justify-content: space-between; font-size: 10px; margin-top: 8px; font-weight: 600; color: #888;">
                        <span>LOW SIGNAL</span>
                        <span>CRITICAL CORE</span>
                    </div>
                 </div>
                 <div style="margin-top: 20px; font-size: 10px; color: #666; font-style: italic;">
                    Aggregated by Antigravity AI Engine
                 </div>
             </div>
             '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # 5. Full Screen View Support & Base Styles
    m.get_root().header.add_child(folium.Element("<style>html, body {width: 100%;height: 100%;margin: 0;padding: 0; background: #0b0b0b;}</style>"))
    
    output_file = 'index.html'
    m.save(output_file)
    print(f"Master Heatmap saved to {output_file}")

if __name__ == "__main__":
    # Prioritize local simulated data if it exists
    sim_file = "simulated_wildfire_feed.json"
    if os.path.exists(sim_file):
        print(f"Loading data from {sim_file}...")
        with open(sim_file, "r") as f:
            items = json.load(f)
            # Flatten coordinates if they are in [lat, lon] format
            for item in items:
                if isinstance(item.get('coordinates'), list):
                    item['lat'], item['lon'] = item['coordinates']
    elif not APIFY_TOKEN or APIFY_TOKEN.startswith("YOUR"):
        print("APIFY_TOKEN not set and no simulation file found. Using mock data.")
        items = generate_mock_historical_data()
    else:
        items = fetch_historical_data()
        # Mock coordinates for real data if missing
        for item in items:
            if 'lat' not in item or 'lon' not in item:
                item['lat'] = 34.0 + (38.0 - 34.0) * (hash(item.get('text', '')) % 1000 / 1000)
                item['lon'] = -118.0 - (122.0 - 118.0) * (hash(item.get('text', '')) % 1000 / 1000)

    heat_data, dates = process_data_for_heatmap(items)
    create_heatmap(heat_data, dates)
