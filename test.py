import google.generativeai as genai

genai.configure(api_key="AIzaSyDjTkryna9S_6A8ucMTWq2QvCu9bLCl7WM")
for m in genai.list_models():
    print(m.name)
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Give me a basic 8th grade math problem.")
print(response.text)
