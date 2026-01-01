import asyncio
from pipeline import WildfirePipelineV3, NewsIntake, ApifyIntake

# Mock Data that mimics REAL RSS/Apify output
MOCK_NEWS_ITEM = {
    "text": "Breaking: Large vegetation fire reported in Carbon Canyon near Chino Hills. Evacuation warnings issued for Sleepy Hollow. #CarbonFire",
    "headline": "Vegetation Fire in Carbon Canyon",
    "source": "News_Google",
    "url": "http://real-news.com/carbon-fire",
    "timestamp": "2025-12-27T10:00:00Z"
}

MOCK_SOCIAL_ITEM = {
    "text": "OMG huge flames visible from my backyard in Malibu! The sky is totally orange. I'm packing my bags. #wildfire",
    "source": "Twitter",
    "url": "http://twitter.com/user/12345",
    "timestamp": "2025-12-27T10:05:00Z"
}

# Mocking the Inputs
class MockNewsIntake(NewsIntake):
    def fetch_news(self):
        print("[TEST] Fetching Mock News...")
        return [MOCK_NEWS_ITEM]

class MockApifyIntake(ApifyIntake):
    def fetch_social_data(self):
        print("[TEST] Fetching Mock Social Data...")
        return [MOCK_SOCIAL_ITEM]

async def test_full_flow():
    print("--- STARTING SYSTEM INTEGRATION TEST ---")
    
    # Instantiate Real Pipeline
    pipeline = WildfirePipelineV3()
    
    # Inject Mocks
    pipeline.news_intake = MockNewsIntake()
    pipeline.apify = MockApifyIntake()
    
    # 1. Test News Cycle (Official)
    print("\n--- Testing OFFICIAL News Flow ---")
    # This should:
    # - Extract "Carbon Canyon" / "Chino Hills"
    # - Geocode it
    # - Identify "Evacuation warnings" -> Evacuation: Active
    # - Push to Monday with High Priority, Verified Status, and "News" Tag logic
    await pipeline.run_news_cycle()
    
    # 2. Test Social Flow (Unofficial) with V11 Scoring
    print("\n--- Testing SOCIAL Flow (V11 Scoring) ---")
    
    # A. Calm Message (Should have low magnitude)
    item_calm = {
        "text": "I think I see some smoke near Malibu. #wildfire",
        "source": "Twitter",
        "url": "http://twitter.com/user/calm",
        "timestamp": "2025-12-27T10:05:00Z"
    }
    print("-> Creating Event 1 (Calm)...")
    await pipeline.process_social_message(item_calm)
    
    # B. Panic Message (Should have higher magnitude due to Urgency)
    item_panic = {
        "text": "OMG FLAMES visible in Malibu!!! HELP US! #wildfire",
        "source": "Twitter",
        "url": "http://twitter.com/user/panic",
        "timestamp": "2025-12-27T10:06:00Z"
    }
    print("-> Creating Event 2 (Panic)...")
    await pipeline.process_social_message(item_panic)
    
    # C. Cluster Effect (Add 5 more events to same location to boost Cluster Score)
    print("-> Creating Event Cluster (5 more messages)...")
    for i in range(5):
        item_cluster = {
            "text": f"More smoke seen in Malibu {i}",
            "source": "Twitter",
            "url": f"http://twitter.com/user/cluster_{i}",
            "timestamp": "2025-12-27T10:10:00Z"
        }
        await pipeline.process_social_message(item_cluster)

    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
