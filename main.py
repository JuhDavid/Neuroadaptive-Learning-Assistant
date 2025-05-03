from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import numpy as np

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
    1:  "You are a math tutor with a focus on math from grades 5-12.\n"
        "You ask the user what topic they would like to learn/get more practice on and they said {topic} \n"
        "You will then create a math problem for them to solve within that said topic.\n"
        "The user will then provide the answer to the math problem, along with the user's answer will be their engagement level.\n"
        "Based on the engagement level and the user's answer create a new math problem with the same topic but either at a more difficult level or an easier level. \n"
        "If the answer is wrong you should also provide detailed steps on how to solve the question. \n"
        "The levels of engagement will be a number from 1-5, where 1 is not focused at all and 5 is completely focused. \n"
        "When responding only provide the math problem and nothing else and in this format. \n"
        "Question: <question in latex format and wrapped with double $ signs>\n",
    2:  
        "You are a math tutor with a focus on math from grades 5-12.\n" 
        "Based on the engagement level and the user's answer create a new math problem with the same topic: {topic} but either at a more difficult level or an easier level. \n"
        "The levels of engagement will be a number from 1-5, where 1 is not focused at all and 5 is completely focused. \n"        
        "{last_question} \n"
        "Is the user's answer: {user_answer} correct? \n"
        "If the answer is wrong you should also provide detailed steps on how to solve the question. \n"
        "<IMPORTANT WRITE ALL EQUATIONS IN LATEX SURROUNDED BY  '$$'>\n"
        "The user's response: \n"
        "User's average focus level: {focus_level}\n"
        "Respond in this format and nothing else :\n"
        "Question: {last_question}>\n"
        "User Answer: <user's answer>\n"
        "Result: <whether they were right or wrong> \n"
        "Focus Level: {focus_level}\n"
        "Explanation: <explanation>\n"
        "New Question: <new question>\n"
}
global lastprompt
lastprompt = "First Prompt"
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
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

@app.post("/generate", response_model=ResponseModel)
async def generate_adaptive_response(req: RequestModel):
    global lastquestion


    ### REPLACE THIS WITH FOCUS LEVEL CALCULATION 
    ### UP TO YOU ON HOW TO DECIDE HOW FOCUS IS CALCULATED BUT DO KNOW THAT THIS IS RUN WHEN THE USER PRESSES THE SUBMIT BUTTON AFTER WRITING THEIR ANSWER
    ### I RECOMMEND USING SOME SORT OF ASYNC FUNCTION THAT CONTINUALLY CALCULATES THE FOCUS LEVEL MAYBE ASK DAVID OR SOMEONE ELSE FOR HELP ON THIS
    focusLevel = np.random.randint(1, 6)  # Randomly generate a focus level between 1 and 5





    if req.answer: #If the user has already provided an answer that means that there is a previous question that was asked and the user is now providing an answer to that question.
        template = PROMPT_TEMPLATES[2] 
        prompt = template.format( last_question = lastquestion, topic=req.topic, user_answer=req.answer, focus_level=focusLevel)
    else:
        template = PROMPT_TEMPLATES[1]
        prompt = template.format(topic=req.topic)
    llm_output = await call_llm_api(prompt)
    last_line = llm_output.splitlines()[-1]  # Get the last line of the response
    lastquestion = last_line  # Extract the question from the last line
    print("Last question: ", lastquestion)
    print(prompt)
    print(llm_output)
    return ResponseModel(
        user_id=req.user_id,
        focus_level=req.focus_level,
        adapted_response=llm_output,
        prompt_used=prompt
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
