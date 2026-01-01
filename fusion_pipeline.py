import asyncio
import json
from intake import NewsIntake, ApifyIntake
from nasa_firms import NasaFirmsIntake
from ai_classifier import SignalTriageAI
from fusion_engine import MagnitudeFusionEngine
from integrations import MondayIntegration
from config import MONDAY_COMPLEXITY_BUDGET

class MagnitudeFusionTool:
    """The California Wildfire Magnitude Fusion Tool Orchestrator."""
    
    def __init__(self):
        self.news = NewsIntake()
        self.apify = ApifyIntake()
        self.firms = NasaFirmsIntake()
        self.triage = SignalTriageAI()
        self.engine = MagnitudeFusionEngine()
        self.monday = MondayIntegration()

    async def run_cycle(self):
        print("\n=== STARTING MAGNITUDE FUSION CYCLE ===")
        
        # 1. Multi-Modal Intake
        print("[Intake] Fetching signals from all sensors...")
        official_news = self.news.fetch_news()
        social_reports = self.apify.fetch_social_data()
        thermal_hotspots = self.firms.fetch_thermal_hotspots()
        
        # 2. AI Triage (Social Reports)
        print("[AI Triage] Filtering social human sensors...")
        filtered_social = []
        for item in social_reports:
            relevance = self.triage.classify_relevance(item['text'])
            if relevance > 0.4: # Filter noise
                # Adjust magnitude based on AI confidence
                item['magnitude'] = item.get('magnitude', 5.0) * (relevance + 0.5)
                item['source_name'] = item.get('source', 'Social')
                # Unify link key
                item['source_link'] = item.get('url', '')
                filtered_social.append(item)
        
        # 3. Ground Truth Pre-processing
        for item in official_news:
            item['magnitude'] = 8.0 # High base for official news
            item['source_name'] = item['source']
            item['source_link'] = item.get('url', '')
            # Coordinates are usually extracted in pipeline, here we assume centroid if missing
            # In a real run, NER/Geocoding happens in FusionEngine
            item['coordinates'] = [36.0, -119.0] # Mock 
            
        all_signals = thermal_hotspots + official_news + filtered_social
        
        # 4. Spatio-Temporal Clustering & Evidence Fusion
        print("[Fusion] Grouping signals into Incident Clusters...")
        # Note: In real scenarios, coordinates must be present.
        # Ensure all signals have coordinates for clustering.
        valid_signals = [s for s in all_signals if 'coordinates' in s and s['coordinates']]
        
        clusters = self.engine.cluster_signals(valid_signals)
        
        # 5. Temporal Decay
        print("[Decay] Adjusting magnitude based on signal freshness...")
        decayed_clusters = self.engine.apply_temporal_decay(clusters)
        
        # 6. Monday.com Integration
        print(f"[Monday] Pushing {len(decayed_clusters)} clusters to board...")
        for cluster in decayed_clusters:
            print(f" -> Syncing: {cluster['headline']} (Mag: {cluster['magnitude']:.2f})")
            success = self.monday.push_incident(cluster)
            if success:
                print(f"    [Success] Complexity Used: {self.monday.complexity_used}")
            else:
                print("    [Failed]")

        print("=== CYCLE COMPLETE ===\n")

async def main():
    tool = MagnitudeFusionTool()
    while True:
        await tool.run_cycle()
        print("Waiting 15 minutes for next cycle...")
        await asyncio.sleep(900) # 15 min cycles

if __name__ == "__main__":
    asyncio.run(main())
