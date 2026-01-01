import feedparser
from apify_client import ApifyClient
from telethon import TelegramClient, events
from config import (
    APIFY_TOKEN, ACTOR_TWITTER, ACTOR_REDDIT, HASHTAGS, 
    TARGET_REGION, TELEGRAM_API_ID, TELEGRAM_API_HASH, 
    TELEGRAM_CHANNELS, RSS_FEEDS
)

class NewsIntake:
    def __init__(self):
        self.feeds = RSS_FEEDS

    def fetch_news(self):
        """Fetches and parses RSS feeds."""
        news_items = []
        for source_name, url in self.feeds.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: # Top 5 latest
                    news_items.append({
                        "text": entry.title + " " + entry.description,
                        "headline": entry.title,
                        "source": f"News_{source_name}",
                        "url": entry.link,
                        "timestamp": entry.get("published", "")
                    })
            except Exception as e:
                print(f"RSS Error ({source_name}): {e}")
        return news_items

class ApifyIntake:
    def __init__(self):
        self.client = ApifyClient(APIFY_TOKEN)

    def fetch_social_data(self):
        """Fetches data from X and Reddit."""
        query = " OR ".join(HASHTAGS)
        results = []
        
        # Twitter Scraper
        try:
            run_input = {"searchTerms": [query], "maxItems": 20}
            run = self.client.actor(ACTOR_TWITTER).call(run_input=run_input)
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append({
                    "text": item.get("full_text", "") or item.get("text", ""),
                    "source": "Twitter",
                    "url": item.get("url", ""),
                    "timestamp": item.get("created_at", "")
                })
        except Exception:
            pass # Silent fail for mock

        return results

class TelegramIntake:
    def __init__(self, callback_handler):
        self.client = TelegramClient('anon', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.callback = callback_handler

    async def start_listening(self):
        @self.client.on(events.NewMessage(chats=TELEGRAM_CHANNELS))
        async def handler(event):
            msg_data = {
                "text": event.message.message,
                "source": f"Telegram ({event.chat.title})",
                "url": f"https://t.me/c/{event.chat_id}/{event.message.id}", 
                "timestamp": str(event.message.date)
            }
            await self.callback(msg_data)
        await self.client.start()
        await self.client.run_until_disconnected()
