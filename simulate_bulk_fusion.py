import asyncio
from fusion_pipeline import MagnitudeFusionTool
from datetime import datetime, timezone, timedelta

async def run_bulk_simulation():
    print("--- STARTING BULK MULTI-SENSOR INTELLIGENCE SIMULATION ---")
    tool = MagnitudeFusionTool()
    
    # Define scenarios
    scenarios = [
        # Scenario 1: Napa Valley (Vineyard Fire)
        {
            "name": "Napa Vineyard Fire",
            "signals": [
                {
                    "headline": "SIGHTING: Smoke in St. Helena Hills",
                    "text": "Huge smoke column spotted near St. Helena vineyard. Winds picking up. #NapaFire",
                    "source": "Twitter", "coordinates": [38.5065, -122.4600], "mag": 6.0
                },
                {
                    "headline": "NASA Thermal: Napa Valley",
                    "text": "Satellite thermal hotspot detected in Napa foothills.",
                    "source": "NASA", "coordinates": [38.5060, -122.4610], "mag": 5.0
                },
                {
                    "headline": "Official: Fire at 50 acres",
                    "text": "CAL FIRE responding to vegetation fire in St. Helena. 0% containment.",
                    "source": "Official_CALFIRE", "coordinates": [38.5065, -122.4600], "mag": 8.5
                }
            ]
        },
        # Scenario 2: Lake Tahoe (Forest Fire)
        {
            "name": "Tahoe Basin Incident",
            "signals": [
                {
                    "headline": "SIGHTING: Fire near South Lake Tahoe",
                    "text": "Seeing active flames in the forest near Echo Lake! Evacuating now.",
                    "source": "Twitter", "coordinates": [38.8350, -120.0320], "mag": 7.5
                },
                {
                    "headline": "NASA Thermal: Tahoe Forest",
                    "text": "Multiple thermal anomalies detected in the Eldorado National Forest.",
                    "source": "NASA", "coordinates": [38.8360, -120.0350], "mag": 6.0
                }
            ]
        },
        # Scenario 3: San Diego (Brush Fire)
        {
            "name": "San Diego Brush Fire",
            "signals": [
                {
                    "headline": "SIGHTING: Smoke near I-15 San Diego",
                    "text": "Brush fire starting near I-15 and Miramar. Lots of smoke.",
                    "source": "Twitter", "coordinates": [32.8800, -117.1100], "mag": 5.5
                },
                {
                    "headline": "Official: I-15 Traffic Advisory",
                    "text": "SD Fire responding to brush fire near freeway. Expect delays.",
                    "source": "Official_SDFire", "coordinates": [32.8805, -117.1105], "mag": 7.0
                }
            ]
        }
    ]

    for scenario in scenarios:
        print(f"\n[Scenario] Processing {scenario['name']}...")
        processed_signals = []
        for s in scenario['signals']:
            # AI Triage
            relevance = tool.triage.classify_relevance(s['text'])
            processed_signals.append({
                "headline": s['headline'],
                "text": s['text'],
                "source_name": s['source'],
                "source_link": "http://simulated-source.com",
                "coordinates": s['coordinates'],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "magnitude": s['mag'] * (relevance + 0.5)
            })
        
        # Fusion
        clusters = tool.engine.cluster_signals(processed_signals)
        
        # Push to Monday
        for cluster in clusters:
            print(f" -> Syncing synthesized cluster (Mag: {cluster['magnitude']:.2f})...")
            success = tool.monday.push_incident(cluster)
            if success:
                print(f"    [Success] {cluster['headline']}")
            else:
                print(f"    [Failed]")

    print("\n--- BULK SIMULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_bulk_simulation())
