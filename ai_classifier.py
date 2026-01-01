from transformers import pipeline
from config import AI_MODEL_NAME

class SignalTriageAI:
    """Uses DistilBERT to distinguish real eyewitness reports from noise/slang."""
    def __init__(self):
        print(f"[AI Triage] Loading model: {AI_MODEL_NAME}...")
        try:
            self.classifier = pipeline("text-classification", model=AI_MODEL_NAME)
        except Exception as e:
            print(f"[AI Triage] Error loading model: {e}. Falling back to keyword-based triage.")
            self.classifier = None

    def classify_relevance(self, text):
        """
        Returns a relevance score.
        For DistilBERT-finetuned-sst-2, 'POSITIVE' label usually means high emotion/relevance in crisis.
        We'll treat high confidence in the classification as a boost.
        """
        if not self.classifier:
            return 0.5 # Neutral fallback
            
        try:
            result = self.classifier(text[:512])[0]
            label = result['label']
            score = result['score']
            
            # Simple mapping: High confidence 'POSITIVE' (meaning critical/urgent in this context)
            if label == "POSITIVE":
                return score
            else:
                return 1.0 - score
        except Exception:
            return 0.5

if __name__ == "__main__":
    triage = SignalTriageAI()
    print(triage.classify_relevance("FLAMES VISIBLE IN MALIBU! HELP!"))
    print(triage.classify_relevance("This new mixtape is fire bro"))
