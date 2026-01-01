import asyncio
from fusion_pipeline import MagnitudeFusionTool
from datetime import datetime, timezone

async def simulate_malibu_fire():
    print("--- SIMULATING MULTI-SENSOR MALIBU FIRE EVENT ---")
    tool = MagnitudeFusionTool()
    
    # 1. Synthetic Scenario: Malibu Fire (Kanan Dume area)
    mock_signals = [
        {
            "headline": "SIGHTING: Smoke near Kanan Dume!",
            "text": "Huge smoke plume visible from Zuma Beach near Kanan Dume Rd! #MalibuFire #KananFire",
            "source_name": "Twitter",
            "source": "Twitter",
            "url": "http://twitter.com/sim_1",
            "coordinates": [34.0200, -118.8100],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "magnitude": 6.5
        },
        {
            "headline": "URGENT: Fire moving towards PCH",
            "text": "The wind is pushing the Malibu fire towards PCH. Evacuations ordered for Malibu Park area.",
            "source_name": "Reddit",
            "source": "Reddit",
            "url": "http://reddit.com/sim_1",
            "coordinates": [34.0210, -118.8115],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "magnitude": 8.0
        },
        {
            "headline": "Thermal Hotspot (NASA VIIRS)",
            "source_name": "NASA FIRMS (VIIRS)",
            "source": "NASA",
            "url": "http://firms.nasa.gov/sim",
            "coordinates": [34.0205, -118.8105],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "magnitude": 5.5,
            "text": "High FRP thermal anomaly detected in Malibu Hills."
        },
        {
            "headline": "CAL FIRE: Vegetation Fire in Malibu",
            "text": "Ground units responding to a 5-acre vegetation fire near Kanan Dume Road, Malibu. Air support requested.",
            "source": "Official_CALFIRE",
            "source_name": "CAL FIRE",
            "url": "http://calfire.ca.gov/sim",
            "coordinates": [34.0200, -118.8100],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "magnitude": 9.0
        }
    ]
    
    # 2. Process through AI Triage
    print("[Simulation] Running Signal Triage...")
    filtered_signals = []
    for item in mock_signals:
        relevance = tool.triage.classify_relevance(item['text'])
        # Adjust magnitude and unify link
        item['magnitude'] = item.get('magnitude', 5.0) * (relevance + 0.5)
        item['source_link'] = item.get('url', '')
        filtered_signals.append(item)
        
    # 3. Clustering & Fusion
    print("[Simulation] clustering & Evidence Fusion...")
    clusters = tool.engine.cluster_signals(filtered_signals)
    
    # 4. Push to Monday
    print(f"[Simulation] Pushing {len(clusters)} synthesized clusters to board...")
    for cluster in clusters:
        print(f" -> Pushing: {cluster['headline']}")
        print(f"    Synthesis Preview: {cluster['raw_text']}")
        success = tool.monday.push_incident(cluster)
        if success:
            print(f"    [Success] Magnitude: {cluster['magnitude']:.2f}")
        else:
            print("    [Failed]")

    print("\n--- SIMULATION PUSH COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(simulate_malibu_fire())
