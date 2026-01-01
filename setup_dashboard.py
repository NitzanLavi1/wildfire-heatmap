import json
import os
import re

def inject_geojson():
    geojson_file = "california_counties.geojson"
    html_file = "index.html"
    
    if not os.path.exists(geojson_file) or not os.path.exists(html_file):
        print("Error: Missing files.")
        return

    print("Reading GeoJSON...")
    with open(geojson_file, "r") as f:
        geojson_data = json.load(f)
    
    print("Reading HTML...")
    with open(html_file, "r") as f:
        html_content = f.read()

    # Create injection string
    # We use json.dumps to ensure it's valid JS object syntax
    new_js_line = f"var GEOJSON_INJECTED = {json.dumps(geojson_data)};"
    
    # Regex to find: var GEOJSON_INJECTED = <anything>;
    pattern = r"var GEOJSON_INJECTED = .*?;"
    
    if re.search(pattern, html_content):
        print("Injecting GeoJSON into HTML...")
        new_html = re.sub(pattern, new_js_line, html_content, count=1)
        
        with open(html_file, "w") as f:
            f.write(new_html)
        print("Success! index.html is now self-contained (Serverless).")
    else:
        print("Error: Injection point 'var GEOJSON_INJECTED = ...;' not found in HTML.")

if __name__ == "__main__":
    inject_geojson()
