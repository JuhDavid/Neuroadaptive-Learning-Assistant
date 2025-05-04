import google.generativeai as genai

genai.configure(api_key="Your API key")
for m in genai.list_models():
    print(m.name)
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Give me a basic 8th grade math problem.")
print(response.text)
