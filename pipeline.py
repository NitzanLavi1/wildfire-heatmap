import asyncio
import time
from intake import NewsIntake, ApifyIntake, TelegramIntake
from processor import WildfireProcessor
from pinpoint import WildfirePinpointer
from integrations import MondayIntegration

class WildfirePipelineV3:
    def __init__(self):
        self.news_intake = NewsIntake()
        self.apify = ApifyIntake()
        self.processor = WildfireProcessor()
        self.pinpoint = WildfirePinpointer()
        self.monday = MondayIntegration()
        self.monday = MondayIntegration()
        self.processed_urls = set()
        self.event_history = [] # For Cluster Density (Lat, Lon)

    def get_cluster_count(self, lat, lon, km_radius=10):
        """Returns number of recent events within radius."""
        from geopy.distance import geodesic
        count = 0
        for h_lat, h_lon in self.event_history:
            if geodesic((lat, lon), (h_lat, h_lon)).kilometers <= km_radius:
                count += 1
        return count

    async def run_news_cycle(self):
        """Fetches news and updates the processor's correlation buffer."""
        print("Fetching Official News...")
        news = self.news_intake.fetch_news()
        
        # 1. Update Correlation Buffer (Extract locations from Verified News)
        self.processor.update_news_buffer(news)
        
        # 2. Push High Priority News items immediately
        for item in news:
            if item['url'] in self.processed_urls: continue
            
            # Extract basic info
            locs = self.processor.extract_locations(item['text'])
            coords = (0,0)
            if locs:
                coords = self.pinpoint.get_lat_long(locs[0])
            
            evac_status = self.processor.check_evacuation_status(item['text'])
            
            data = {
                "headline": f"{item['headline']}",
                "source_name": f"OFFICIAL: {item['source']}", # e.g. OFFICIAL: CAL_FIRE
                "source_link": item['url'],
                "coordinates": coords,
                "evacuation_status": evac_status,
                "priority": "High", # Official news is always High (case sensitive)
                "timestamp": item['timestamp'],
                "raw_text": item['text'], # V5: Raw Text
                "magnitude": 8.0, # Official default
                "certainty_index": "Official Source"
            }
            self.monday.push_incident(data)
            self.processed_urls.add(item['url'])
            if coords != (0,0): self.event_history.append(coords)

    async def process_social_message(self, msg):
        """Processes social/telegram messages with correlation logic."""
        if msg['url'] in self.processed_urls: return
        self.processed_urls.add(msg['url'])

        # 1. NER
        locations = self.processor.extract_locations(msg['text'])
        if not locations: return

        # 2. Correlation (Check against News Buffer)
        priority = self.processor.correlate_with_news(locations)
        
        # 3. Geolocation & Camera Verification
        coords = self.pinpoint.get_lat_long(locations[0])
        lat, lon = coords
        
        has_camera, cam_loc = self.pinpoint.verify_with_cameras(lat, lon)
        if has_camera:
            priority = "High" # Camera verified = High
        elif not has_camera and priority == "HIGH": # From correlate_with_news text return
             priority = "High"

        # 4. Filter: Only push Medium/High events (ignore single social reports if strict)
        evac = self.processor.check_evacuation_status(msg['text'])
        
        # V4: Slang Filter / Certainty Index
        is_legit, certainty_reason = self.processor.check_certainty(msg['text'])
        if not is_legit:
            print(f"Skipping (V4 Filter): {certainty_reason}")
            return # DROP THE ITEM

        # V11: Cluster Density Calculation
        cluster_count = self.get_cluster_count(lat, lon)
            
        # V11: Smart Magnitude Score
        magnitude = self.processor.calculate_magnitude(
            text=msg['text'],
            source_type=msg['source'],
            verified_camera=has_camera,
            cluster_count=cluster_count
        )
        
        data = {
            "headline": f"{locations[0]} Report",
            "source_name": msg['source'],
            "source_link": msg['url'],
            "coordinates": coords,
            "evacuation_status": evac,
            "priority": priority,
            "timestamp": msg['timestamp'],
            "magnitude": magnitude,
            "certainty_index": certainty_reason,
            "raw_text": msg['text'] # V5: Raw Text
        }
        
        if priority != "LOW": 
            print(f"Pushing Event: {data['headline']} (Mag: {magnitude})")
            self.monday.push_incident(data)
            self.event_history.append(coords) # Add to history iff pushed


    async def run(self):
        print("Starting Wildfire Pipeline V3 (Tri-Signal)...")
        
        # Background: Telegram Listener
        # TelegramIntake needs to handle initialization carefully if sync methods are mixed
        # Assuming TelegramIntake is async ready
        telegram = TelegramIntake(callback_handler=self.process_social_message)
        # We start listening in the background. 'start_listening' is async.
        # It runs forever.
        asyncio.create_task(telegram.start_listening())
        
        # Loop: News -> Social -> Sleep
        try:
            while True:
                # A. News Cycle (Official Sources)
                try:
                    await self.run_news_cycle()
                except Exception as e:
                    print(f"News Cycle Error: {e}")
                
                # B. Apify Cycle (X/Reddit)
                try:
                    # Apify fetch is sync blocking in this implementation (simple client)
                    # To make it truly non-blocking we should run in executor, but for < 1 min taking it's OK
                    # If user wants parallel, we can optimize.
                    apify_data = self.apify.fetch_social_data()
                    for msg in apify_data:
                        await self.process_social_message(msg)
                except Exception as e:
                    print(f"Apify Cycle Error: {e}")

                print("Cycle Complete. Sleeping for 10 minutes...")
                await asyncio.sleep(600) # 10 minutes
        except asyncio.CancelledError:
            print("Stopping...")

if __name__ == "__main__":
    pipeline = WildfirePipelineV3()
    try:
        asyncio.run(pipeline.run())
    except KeyboardInterrupt:
        pass
