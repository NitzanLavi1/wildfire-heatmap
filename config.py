import os

# API Configurations
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID", "YOUR_TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "YOUR_TELEGRAM_API_HASH")
MONDAY_API_KEY = os.getenv("MONDAY_API_KEY", "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYwMTE2ODU0NSwiYWFpIjoxMSwidWlkIjo5NzY5MDI3NCwiaWFkIjoiMjAyNS0xMi0yNlQxNTo0MzozNy41MjhaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MzMwNDU0ODAsInJnbiI6ImV1YzEifQ.2qe94erEyzxN7JZZ8JEy-UTxI3osqNtIMfDWA4GNuNA")
MONDAY_DISTRICT_BOARD_ID = "5089421649"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCRS73Hx3FQbe30gkyM_qayBS9A4WOP5Z8")
MOCK_MODE = True

# Tri-Signal Source Configs
# 1. RSS Feeds (Official News)
RSS_FEEDS = {
    "CAL_FIRE": "https://www.fire.ca.gov/rss", # Mock/Generic URL
    "LAFD": "https://www.lafd.org/news/rss",
    "WILDFIRE_TODAY": "https://wildfiretoday.com/feed/"
}

# 2. Social Media (Apify)
TARGET_REGION = "California"
HASHTAGS = ["#CALFire", "#CaliforniaWildfire", "#ReadyForWildfire", "#WoolseyFire", "#CampFire"]
# Actors stay the same
ACTOR_TWITTER = "apify/twitter-scraper"
ACTOR_REDDIT = "apify/reddit-scraper"

# 3. Telegram (Community)
TELEGRAM_CHANNELS = ["watch_duty", "calfire_updates", "socal_fire_watch"]

# Verification / Geolocation
# Mock list of ALERTCalifornia Camera Locations (Lat, Lon)
ALERT_CALIFORNIA_CAMERAS = [
    (34.106, -118.668), # Topanga
    (34.420, -119.698), # Santa Barbara
    (36.270, -121.808), # Big Sur
    (39.728, -121.805)  # Chico/Paradise
]
CAMERA_CHECK_RADIUS_KM = 15

# Keywords for Evacuation / Priority
EVACUATION_KEYWORDS = ["evacuation", "evacuate", "immediate threat", "warning", "order"]

# Group Routing Configuration
SUGGESTED_LOC_COLUMN_ID = "text_mkz1x76c"

GROUP_IDS = {
    "CRITICAL": "group_mkz3vxgh",      # Magnitude 7-10
    "HIGH_WATCH": "group_mkz3c00k",    # Magnitude 4-7
    "MONITORING": "group_mkz3xrd9",    # Magnitude 2-4
    "STABLE": "group_mkz33q7s"         # Magnitude 0-1
}

GROUP_MAPPING = {
    "group_mkz0tj87": ["Alameda", "Oakland", "Berkeley", "East Bay"],
    "topics": ["Fresno", "Yosemite", "Madera", "Kings Canyon"],
    "group_title": ["Ventura", "Malibu", "Topanga", "Santa Barbara", "Oxnard", "Ojai"]
}

# V4/V5/V6 Configuration
MAGNITUDE_COLUMN_ID = "numeric_mkz2drbb"
CERTAINTY_COLUMN_ID = "text_mkz2d2tp"
POST_COLUMN_ID = "long_text_mkz2vg7x"
VERIFICATION_COLUMN_ID = "color_mkz2ajkv"
GENERAL_DISPATCH_GROUP_ID = "topics" # Using first available group
SUGGESTED_LOC_STATUS_ID = "status"
DATE_COLUMN_ID = "date4"

# New Board Column IDs
SOURCE_LINK_COLUMN_ID = "link_mkz2k9z2"
LOCATION_COLUMN_ID = "location_mkz28te7"
EVACUATION_COLUMN_ID = "text_mkz2x52k"
RAW_INPUT_COLUMN_ID = "long_text1qliuvah"

# Extended AI Categories (Old Text Columns - Keeping for reference/backward capability if needed)
HUMAN_SAFETY_COLUMN_ID = "long_text_mkz3adbt"
INFRASTRUCTURE_COLUMN_ID = "long_text_mkz3c9j4"
INTENSITY_COLUMN_ID = "long_text_mkz3tf8n"
ENVIRONMENTAL_COLUMN_ID = "long_text_mkz35pkj"
OPERATIONAL_COLUMN_ID = "long_text_mkz3e21g"

# Quantitative Data Columns (New v2 Schema)
FATALITIES_COL_ID = "numeric_mkz3yn42"
INJURED_COL_ID = "numeric_mkz323p7"
PEOPLE_THREATENED_COL_ID = "numeric_mkz3m09a"
STRUCTURES_DESTROYED_COL_ID = "numeric_mkz3gahm"
STRUCTURES_THREATENED_COL_ID = "numeric_mkz3v9y6"
INFRA_IMPACT_SCORE_COL_ID = "numeric_mkz3c5mn"
ACRES_BURNED_COL_ID = "numeric_mkz3mcdv"
CONTAINMENT_COL_ID = "numeric_mkz3zkff"
AQI_COL_ID = "numeric_mkz36ms1"
PERSONNEL_COUNT_COL_ID = "numeric_mkz3wmna"
APPARATUS_COUNT_COL_ID = "numeric_mkz3kpty"

# V11 Smart Magnitude Scoring
MAGNITUDE_WEIGHTS = {
    "urgency": 0.3,   # AI Sentiment/Panic
    "severity": 0.3,  # Keyword matches
    "media": 0.15,    # Visual proof
    "cluster": 0.15,  # Multiple reports
    "source": 0.1     # Credibility
}

SEVERITY_KEYWORDS = {
    "evacuation": 5, "evacuate": 5, "trapped": 5,
    "flames": 4, "fire": 3, "burning": 3, "ignited": 3,
    "smoke": 2, "ash": 1, "smell": 1
}

# V8 Geospatial Routing
# Centroids for the major locations to check proximity against
KNOWN_LOCATIONS = {
    "Alameda": (37.6017, -121.7195),
    "Fresno": (36.7378, -119.7871),
    "Ventura": (34.2746, -119.2290)
}

# Certainty / Slang Filters
# Terms that imply the word "fire" is slang or not a wildfire
SLANG_FILTERS = [
    "this song is fire", "mix tape", "dumpster fire", "so fire", "fire outfit",
    "fired from", "shots fired", "rapid fire", "friendly fire"
]
BOT_KEYWORDS = ["crypto", "nft", "giveaway", "follow me", "check out my"]

# Magnitude Fusion Tool: Phase 1 Configuration
NASA_FIRMS_API_KEY = os.getenv("NASA_FIRMS_API_KEY", "YOUR_NASA_FIRMS_KEY")
NASA_FIRMS_AREA_CA = [-124.4, 32.5, -114.1, 42.0] # [W, S, E, N] California Bounding Box

AI_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
SPACY_MODEL = "en_core_web_sm"

# ST-DBSCAN Parameters
CLUSTERING_DISTANCE_KM = 2.0
CLUSTERING_TIME_WINDOW_MINS = 15
TEMPORAL_DECAY_RATE = 1.0 # Points per 30 mins

# Monday.com API Complexity tracking
MONDAY_COMPLEXITY_BUDGET = 10000000 

# Filtering Rules
CERTAINTY_THRESHOLD = 60 # Minimum score (0-100) to push to board
