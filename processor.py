import nltk
from config import EVACUATION_KEYWORDS

class WildfireProcessor:
    def __init__(self):
        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('chunkers/maxent_ne_chunker')
            nltk.data.find('corpora/words')
        except LookupError:
            print("Downloading NLTK data...")
            nltk.download('punkt')
            nltk.download('punkt_tab')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('averaged_perceptron_tagger_eng')
            nltk.download('maxent_ne_chunker')
            nltk.download('maxent_ne_chunker_tab')
            nltk.download('words')

        self.news_location_buffer = set() # Store verified locations from News

    def update_news_buffer(self, news_items):
        """Extracts locations from news and adds to buffer."""
        for item in news_items:
            locs = self.extract_locations(item['text'])
            for loc in locs:
                self.news_location_buffer.add(loc.lower())

    def extract_locations(self, text):
        """Extracts locations using NLTK."""
        try:
            tokens = nltk.word_tokenize(text)
            tags = nltk.pos_tag(tokens)
            chunks = nltk.ne_chunk(tags)
            
            locations = set()
            for chunk in chunks:
                if hasattr(chunk, 'label') and chunk.label() in ['GPE', 'LOCATION']:
                    # Reconstruct the location string
                    loc_name = " ".join(c[0] for c in chunk)
                    locations.add(loc_name)
            return list(locations)
        except Exception as e:
            print(f"NER Error: {e}")
            return []

    def check_evacuation_status(self, text):
        """Determines if evacuation is mentioned."""
        if any(kw in text.lower() for kw in EVACUATION_KEYWORDS):
            return "Active/Warning"
        return "Unknown"

    def correlate_with_news(self, social_locations):
        """
        Returns 'HIGH' if any social location matches a location 
        already seen in reliable news feeds.
        """
        for loc in social_locations:
            if loc.lower() in self.news_location_buffer:
                return "HIGH"
        return "MEDIUM" # Default starting priority for social chatter

    # V11 SMART SCORING METHODS
    def calculate_urgency(self, text):
        """
        Calculates Urgency/Panic Score (0-10) based on heuristics.
        """
        score = 0
        text = text.lower()
        
        # 1. Panic Words
        panic_words = ["omg", "help", "emergency", "urgent", "terrifying", "scary", "trapped"]
        for word in panic_words:
            if word in text: score += 2
            
        # 2. Intensifiers
        intensifiers = ["huge", "massive", "giant", "enormous", "out of control"]
        for word in intensifiers:
            if word in text: score += 1.5
            
        # 3. Punctuation & Caps (Simple Proxy)
        if "!" in text: score += 1
        if "!!!" in text: score += 2
        
        return min(score, 10.0)

    def calculate_severity(self, text):
        """
        Calculates Severity Score (0-10) based on Keyword Matrix.
        """
        from config import SEVERITY_KEYWORDS
        score = 0
        text = text.lower()
        
        for word, weight in SEVERITY_KEYWORDS.items():
            if word in text:
                score += weight
                
        return min(score, 10.0)

    def calculate_magnitude(self, text, source_type, verified_camera=False, cluster_count=0):
        """
        V11: Calculates Weighted Magnitude Score (1-10) using 5 Drivers.
        """
        from config import MAGNITUDE_WEIGHTS
        
        # 1. Driver Scores (Normalized 0-10)
        
        # A. Urgency (AI/Heuristic)
        s_urgency = self.calculate_urgency(text)
        
        # B. Severity (Keywords)
        s_severity = self.calculate_severity(text)
        
        # C. Media Verification
        s_media = 10.0 if verified_camera else 0.0
        
        # D. Cluster Density
        # Algo: If > 5 reports nearby, Score = 10. If 1 report, Score = 0.
        s_cluster = min(cluster_count * 2.0, 10.0)
        
        # E. Source Credibility
        s_source = 2.0 # Default (Social)
        if "OFFICIAL" in source_type or "News_" in source_type:
            s_source = 10.0
        elif "Telegram" in source_type:
            s_source = 7.0
            
        # 2. Weighted Sum
        final_score = (
            (s_urgency * MAGNITUDE_WEIGHTS["urgency"]) +
            (s_severity * MAGNITUDE_WEIGHTS["severity"]) +
            (s_media * MAGNITUDE_WEIGHTS["media"]) +
            (s_cluster * MAGNITUDE_WEIGHTS["cluster"]) +
            (s_source * MAGNITUDE_WEIGHTS["source"])
        )
        
        # Cap and Round
        return round(min(final_score, 10.0), 1)

    def check_certainty(self, text):
        """
        Checks for slang, bots, or misleading context. 
        Returns (Is_Legit (Bool), Reason (Str))
        """
        text_lower = text.lower()
        from config import SLANG_FILTERS, BOT_KEYWORDS
        
        for slang in SLANG_FILTERS:
            if slang in text_lower:
                return False, f"Flagged as Slang: '{slang}'"
                
        for bot in BOT_KEYWORDS:
            if bot in text_lower:
                return False, f"Flagged as Bot: '{bot}'"
                
        return True, "Likely Legitimate"
