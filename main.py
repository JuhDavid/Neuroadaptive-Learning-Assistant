from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import numpy as np
import logging

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing required environment variable: GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel("gemini-2.0-flash")

# Logging setup
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Neuroadaptive Learning Assistant API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt templates
PROMPT_TEMPLATES = {
    1: (
        "You are a math tutor with a focus on math from grades 5-12.\n"
        "You ask the user what topic they would like to learn/get more practice on and they said {topic} \n"
        "You will then create a math problem for them to solve within that said topic.\n"
        "The user will then provide the answer to the math problem, along with the user's answer will be their engagement level.\n"
        "Based on the engagement level and the user's answer create a new math problem with the same topic but either at a more difficult level or an easier level. \n"
        "If the answer is wrong you should also provide detailed steps on how to solve the question. \n"
        "The levels of engagement will be a number from 1-5, where 1 is not focused at all and 5 is completely focused. \n"
        "When responding only provide the math problem and nothing else and in this format. \n"
        "Question: <question in latex format and wrapped with double $ signs>\n"
    ),
    2: (
        "You are a math tutor with a focus on math from grades 5-12.\n" 
        "Based on the engagement level and the user's answer create a new math problem with the same topic: {topic} but either at a more difficult level or an easier level. \n"
        "The levels of engagement will be a number from 1-5, where 1 is not focused at all and 5 is completely focused. \n"        
        "{last_question} \n"
        "Is the user's answer: {user_answer} correct? \n"
        "If the answer is wrong you should also provide detailed steps on how to solve the question. \n"
        "<IMPORTANT WRITE ALL EQUATIONS IN LATEX SURROUNDED BY  '$$'>\n"
        "The user's response: \n"
        "User's average focus level: {focus_level}\n"
        "Respond in this format and nothing else:\n"
        "Question: {last_question}>\n"
        "User Answer: <user's answer>\n"
        "Result: <whether they were right or wrong>\n"
        "Focus Level: {focus_level}\n"
        "Explanation: <explanation>\n"
        "Whether or not you will increase the difficulty of the question or not: <yes or no>\n"
        "New Question: <new question>\n"
    )
}

# Store last question per user
user_last_question = {}

# Request and response models
class RequestModel(BaseModel):
    user_id: str
    answer: str
    topic: str
    focus_level: int  # 1 to 5

class ResponseModel(BaseModel):
    user_id: str
    focus_level: int
    adapted_response: str
    prompt_used: str

# Streaming EEG from g.hysis to LLM through LSL 
from pylsl import StreamInlet, resolve_streams
import time
import threading
engagement_score = []
def lsl_listener():
    all_streams = resolve_streams()
    for i,stream in enumerate(all_streams):
        if stream.name() == 'engagement_score1':
            eng_stream = all_streams[i]
            break
	inlet = StreamInlet(eng_stream)
    while True:
        engagement_score, timestamp = inlet.pull_sample()
        time.sleep(0.01)

lsl_thread = threading.Thread(target=lsl_listener, daemon=True)
lsl_thread.start()
# Call Gemini API
async def call_llm_api(prompt: str) -> str:
    try:
        response = MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

# Main endpoint
@app.post("/generate", response_model=ResponseModel)
async def generate_adaptive_response(req: RequestModel):
    user_id = req.user_id
    focus_level = req.focus_level  # Assume it's passed from frontend

    if req.answer:  # User is responding to previous question
        last_question = user_last_question.get(user_id, "No previous question.")
        template = PROMPT_TEMPLATES[2]
        prompt = template.format(
            last_question=last_question,
            topic=req.topic,
            user_answer=req.answer,
            focus_level=focus_level
        )
    else:  # First-time question generation
        template = PROMPT_TEMPLATES[1]
        prompt = template.format(topic=req.topic)

    llm_output = await call_llm_api(prompt)
    last_line = llm_output.splitlines()[-1]
    user_last_question[user_id] = last_line  # Update for the user

    logging.info(f"Prompt: {prompt}")
    logging.info(f"LLM Output: {llm_output}")

    return ResponseModel(
        user_id=user_id,
        focus_level=focus_level,
        adapted_response=llm_output,
        prompt_used=prompt
    )

# Run the app (optional if using uvicorn CLI)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
