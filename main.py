from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# # Load API key
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise RuntimeError("Missing required environment variable: OPENAI_API_KEY")

# openai.api_key = OPENAI_API_KEY


genai.configure(api_key='AIzaSyDjTkryna9S_6A8ucMTWq2QvCu9bLCl7WM')  # Replace with your Gemini API key

app = FastAPI(title="Neuroadaptive Learning Assistant API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt templates by focus level
PROMPT_TEMPLATES = {
    1:  "You are a math tutor with a focus on math from grades 5-12.\n..."
        "You ask the user what topic they would like to learn/get more practice on and they said {topic} \n..."
        "You will then create a math problem for them to solve within that said topic.\n"
        "The user will then provide the answer to the math problem, along with the user's answer will be their engagement level.\n"
        "Based on the engagement level and the user's answer create a new math problem with the same topic but either at a more difficult level or an easier level. \n"
        "If the answer is wrong you should also provide detailed steps on how to solve the question. \n"
        "The levels of engagement will be a number from 1-5, where 1 is not focused at all and 5 is completely focused. \n"
        "The user's response will be in this format: \n"
        "User Answer: <number or equation>\n"
        "User's average focus level: <number> \n"
        "Respond in this format:\n"
        "Result: <Correct / Incorrect> \n"
        "Explanation: <explanation in plain text>\n"
        "New Question: <new question in plain text>\n",
    2:  "Reiterate the question that you asked the user.\n"
        "Is the user's answer correct? If not provide a step by step guide on how to get the correct answer.\n"
        "Based on the engagement level and the user's answer create a new math problem with the same topic: {topic} but either at a more difficult level or an easier level. \n"
        "If the answer is wrong you should also provide detailed steps on how to solve the question. \n"
        "The levels of engagement will be a number from 1-5, where 1 is not focused at all and 5 is completely focused. \n"
        "The user's response will be in this format: \n"
        "User Answer: {user_answer}\n"
        "User's average focus level: {focus_level}\n"
        "Respond in this format:\n"
        "Question asked: <question in plain text>\n"
        "Result: <Correct / Incorrect> \n"
        "Focus Level: {focus_level}\n"
        "Explanation: <explanation in plain text>\n"
        "New Question: <new question in plain text>\n"
}

class RequestModel(BaseModel):
    user_id: str
    answer: str
    topic: str
    focus_level: int  # expected 1-5

class ResponseModel(BaseModel):
    user_id: str
    focus_level: int
    adapted_response: str
    prompt_used: str

async def call_llm_api(prompt: str) -> str:
    try:
        response = genai.generate_text(
            model="gemini-1",  # Replace with the appropriate Gemini model
            prompt=prompt,
            max_output_tokens=500,
            temperature=0.7
        )
        return response.candidates[0]["output"].strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

@app.post("/generate", response_model=ResponseModel)
async def generate_adaptive_response(req: RequestModel):
    if req.answer:
        template = PROMPT_TEMPLATES[2]
        prompt = template.format(topic=req.topic, user_answer=req.answer, focus_level=req.focus_level)
    else:
        template = PROMPT_TEMPLATES[1]
        prompt = template.format(topic=req.topic)

    llm_output = await call_llm_api(prompt)

    return ResponseModel(
        user_id=req.user_id,
        focus_level=req.focus_level,
        adapted_response=llm_output,
        prompt_used=prompt
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
