import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing required environment variable: GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# List available models
print("Available models:")
for m in genai.list_models():
    print(m.name)

# Test basic generation
response = model.generate_content("Give me a basic 8th grade math problem.")
print("Response from model:")
print(response.text)
