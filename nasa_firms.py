import requests
import pandas as pd
from datetime import datetime
from config import NASA_FIRMS_API_KEY, NASA_FIRMS_AREA_CA

class NasaFirmsIntake:
    """Retrieves Thermal Hotspots from NASA FIRMS API."""
    def __init__(self):
        self.api_key = NASA_FIRMS_API_KEY
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
        self.area = ",".join(map(str, NASA_FIRMS_AREA_CA))

    def fetch_thermal_hotspots(self, instrument="VIIRS_SNPP", day_range=1):
        """
        Fetches CSV data from FIRMS and converts to list of incidents.
        Instrument options: VIIRS_SNPP, VIIRS_NOAA20, MODIS_NRT
        """
        if self.api_key == "YOUR_NASA_FIRMS_KEY":
            print("[NASA FIRMS] Skipping real fetch: API Key placeholder.")
            return []

        url = f"{self.base_url}/{self.api_key}/{instrument}/{self.area}/{day_range}"
        
        try:
            print(f"[NASA FIRMS] Fetching {instrument} hotspots for CA...")
            response = requests.get(url)
            if response.status_code != 200:
                print(f"[NASA FIRMS] API Error: {response.status_code}")
                return []
            
            # FIRMS returns CSV
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            hotspots = []
            for _, row in df.iterrows():
                # FIRMS intensity is measured by FRP (Fire Radiative Power)
                # Magnitude mapping: Map FRP 0-500 to 1-10 scale
                frp = float(row.get('frp', 1.0))
                magnitude = min(10.0, max(1.0, 1.0 + (frp / 50.0)))
                
                hotspots.append({
                    "headline": f"Thermal Hotspot Detected ({instrument})",
                    "source_name": f"NASA FIRMS ({instrument})",
                    "source_link": "https://firms.modaps.eosdis.nasa.gov/map/",
                    "coordinates": [float(row['latitude']), float(row['longitude'])],
                    "priority": "High" if magnitude > 7 else "Medium",
                    "timestamp": f"{row['acq_date']}T{row['acq_time'][:2]}:{row['acq_time'][2:]}:00Z",
                    "magnitude": magnitude,
                    "certainty_index": f"Satellite Confidence: {row.get('confidence', 'N/A')}",
                    "type": "remote_sensing"
                })
            
            print(f"[NASA FIRMS] Found {len(hotspots)} hotspots.")
            return hotspots
            
        except Exception as e:
            print(f"[NASA FIRMS] Exception: {e}")
            return []

if __name__ == "__main__":
    # Test fetch
    firms = NasaFirmsIntake()
    data = firms.fetch_thermal_hotspots()
    print(data[:2])
