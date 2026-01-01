import asyncio
from fusion_pipeline import MagnitudeFusionTool

async def test_fusion_logic():
    print("--- TESTING MAGNITUDE FUSION LOGIC ---")
    tool = MagnitudeFusionTool()
    
    # 1. Create a Synthetic Multi-Sensor Scenario (Topanga Fire)
    # 2 Social Reports, 1 NASA Hotspot
    mock_signals = [
        {
            "headline": "SIGHTING: Smoke in Topanga Canyon!",
            "text": "Seeing huge smoke columns near Topanga Canyon Rd #TopangaFire",
            "source_name": "Twitter",
            "source_link": "http://twitter.com/1",
            "coordinates": [34.0935, -118.6003],
            "timestamp": "2025-12-28T10:00:00Z",
            "magnitude": 6.0
        },
        {
            "headline": "HELP: Fire moving fast in Topanga!",
            "text": "The fire is crossing the ridge in Topanga! We are packing!",
            "source_name": "Reddit",
            "source_link": "http://reddit.com/1",
            "coordinates": [34.0940, -118.6010],
            "timestamp": "2025-12-28T10:05:00Z",
            "magnitude": 7.5
        },
        {
            "headline": "Thermal Hotspot Detected (VIIRS)",
            "source_name": "NASA FIRMS (VIIRS)",
            "source_link": "http://firms.nasa.gov",
            "coordinates": [34.0930, -118.6000],
            "timestamp": "2025-12-28T09:55:00Z",
            "magnitude": 5.0,
            "text": "Satellite thermal anomaly detected."
        }
    ]
    
    # 2. Run Fusion Engine directly
    print("[Test] Clustering signals...")
    clusters = tool.engine.cluster_signals(mock_signals)
    
    for c in clusters:
        print(f"\nFinal Cluster: {c['headline']}")
        print(f"Magnitude: {c['magnitude']:.2f} (Should be boosted due to multi-sensor confirmation)")
        print(f"Reports: {c['cluster_size']}")
        print(f"Centroid: {c['coordinates']}")
        print(f"Summary: {c['raw_text']}")
        
    assert len(clusters) == 1
    assert clusters[0]['magnitude'] > 7.0 # Verify boost logic
    
    print("\n--- FUSION TEST PASSED ---")

if __name__ == "__main__":
    asyncio.run(test_fusion_logic())
