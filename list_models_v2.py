from google import genai
import config

client = genai.Client(api_key=config.GEMINI_API_KEY)

try:
    print("Listing models...")
    for model in client.models.list(config={"page_size": 10}):
        print(model.name)
except Exception as e:
    print(f"Error listing models: {e}")
