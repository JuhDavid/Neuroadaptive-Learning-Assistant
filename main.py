from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Load API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing required environment variable: OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

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
    1: "You're very tired and unfocused. Provide a super simple, step-by-step answer to: {question}",
    2: "You're a bit unfocused. Provide an easy-to-follow explanation with examples for: {question}",
    3: "You're moderately focused. Provide a clear and concise answer to: {question}",
    4: "You're focused. Dive into details and technical depth for: {question}",
    5: "You're in flow state! Provide an advanced, in-depth exploration of: {question}",
}

class RequestModel(BaseModel):
    user_id: str
    question: str
    focus_level: int  # expected 1-5

class ResponseModel(BaseModel):
    user_id: str
    focus_level: int
    adapted_response: str
    prompt_used: str

async def call_llm_api(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano-2025-04-14",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful educational assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM API error: {str(e)}")

@app.post("/generate", response_model=ResponseModel)
async def generate_adaptive_response(req: RequestModel):
    if req.focus_level not in PROMPT_TEMPLATES:
        raise HTTPException(status_code=400, detail="Invalid focus level")

    template = PROMPT_TEMPLATES[req.focus_level]
    prompt = template.format(question=req.question)

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
