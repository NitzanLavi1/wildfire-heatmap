import pandas as pd
import numpy as np
import spacy
from sklearn.cluster import DBSCAN
from geopy.distance import geodesic
from datetime import datetime, timedelta
from config import CLUSTERING_DISTANCE_KM, CLUSTERING_TIME_WINDOW_MINS, SPACY_MODEL, TEMPORAL_DECAY_RATE

# Load spaCy for NER
try:
    nlp = spacy.load(SPACY_MODEL)
except Exception:
    # Fallback if model not downloaded
    nlp = None

class MagnitudeFusionEngine:
    """The 'Gatekeeper' Engine: Clustering, NER, and Evidence Fusion."""
    
    def __init__(self):
        self.active_clusters = {} # Storage for persistent clusters
        
    def extract_micro_locations(self, text):
        """Uses spaCy NER to find canyons, roads, and specific landmarks."""
        if not nlp: return []
        doc = nlp(text)
        # GPE (Countries, cities, states), LOC (Non-GPE locations, mountain ranges, bodies of water), 
        # FAC (Buildings, airports, highways, bridges, etc.)
        entities = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
        return entities

    def cluster_signals(self, signals):
        """
        Groups reports using Spatio-Temporal DBSCAN logic.
        signals: List of dictionaries with 'coordinates' [lat, lon] and 'timestamp'.
        """
        if not signals: return []
        
        df = pd.DataFrame(signals)
        df['dt'] = pd.to_datetime(df['timestamp'])
        
        # Convert coords to radians for Haversine distance
        coords = np.radians(df['coordinates'].tolist())
        
        # Time to numerical (minutes since epoch)
        times = (df['dt'].astype(np.int64) // 10**9 // 60).values.reshape(-1, 1)
        
        # ST-DBSCAN Implementation (Custom Distance Matrix)
        # We'll use a simplified version: Cluster by space, then filter by time
        kms_per_radian = 6371.0
        epsilon_space = CLUSTERING_DISTANCE_KM / kms_per_radian
        
        db = DBSCAN(eps=epsilon_space, min_samples=1, metric='haversine').fit(coords)
        df['cluster_id'] = db.labels_
        
        clusters = []
        for cid in df['cluster_id'].unique():
            cluster_df = df[df['cluster_id'] == cid]
            
            # Further refine by time window
            # If time gap > window, split cluster (simplified: take median)
            if cluster_df['dt'].max() - cluster_df['dt'].min() > timedelta(minutes=CLUSTERING_TIME_WINDOW_MINS):
                # For this implementation, we just keep them together if space matches
                pass 

            # Synthesis Logic
            centroid_lat = cluster_df['coordinates'].apply(lambda x: x[0]).mean()
            centroid_lon = cluster_df['coordinates'].apply(lambda x: x[1]).mean()
            
            # Evidence Fusion (The Gatekeeper)
            sources = cluster_df['source_name'].unique()
            base_magnitude = cluster_df['magnitude'].max()
            
            # Boost logic: If multiple types agree (Remote Sensing + Social)
            has_remote = any("NASA" in s for s in sources)
            has_social = any(s in ["Twitter", "Reddit", "Telegram"] for s in sources)
            has_official = any("News" in s or "Official" in s for s in sources)
            
            boost = 0
            if has_remote and (has_social or has_official):
                boost += 2.0 # Multi-modal confirmation
            elif has_social and has_official:
                boost += 1.5
                
            final_magnitude = min(10.0, base_magnitude + boost)
            
            # Summarization
            summary_text = "Cluster Synthesis:\n"
            micro_locs = set()
            for text in cluster_df['text'].unique():
                micro_locs.update(self.extract_micro_locations(text))
            
            summary_text += f"- Reports: {len(cluster_df)}\n"
            summary_text += f"- Sources: {', '.join(sources)}\n"
            if micro_locs:
                summary_text += f"- Extracted Entities: {', '.join(list(micro_locs)[:5])}\n"
            
            clusters.append({
                "headline": f"INCIDENT CLUSTER: {cluster_df.iloc[0]['headline']}",
                "coordinates": [centroid_lat, centroid_lon],
                "magnitude": final_magnitude,
                "raw_text": summary_text,
                "timestamp": cluster_df['dt'].max().isoformat(),
                "priority": "High" if final_magnitude > 8.0 else "Medium",
                "source_link": cluster_df.iloc[0]['source_link'],
                "cluster_size": len(cluster_df)
            })
            
        return clusters

    def apply_temporal_decay(self, clusters):
        """Reduces magnitude based on inactivity."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        for c in clusters:
            # Ensure dt is aware
            dt = pd.to_datetime(c['timestamp'])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            mins_old = (now - dt).total_seconds() / 60
            decay_amount = (mins_old / 30.0) * TEMPORAL_DECAY_RATE
            c['magnitude'] = max(1.0, c['magnitude'] - decay_amount)
        return clusters
