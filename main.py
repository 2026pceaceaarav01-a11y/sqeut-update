import os
import json
from fastapi import FastAPI, HTTPException
import google.generativeai as genai
from pydantic import BaseModel

app = FastAPI()

# You will set this in the Render.com Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class TaskResponse(BaseModel):
    title: str
    description: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/generate-task", response_model=TaskResponse)
def generate_task():
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server.")
        
    try:
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        prompt = """
        Generate a daily quest or habit for the user to complete today.
        Return ONLY a JSON object with the following schema:
        {
          "title": "Short catchy title of the quest",
          "description": "A 1-2 sentence description of what to do"
        }
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response from Gemini
        task_data = json.loads(response.text)
        
        return TaskResponse(
            title=task_data.get("title", "Unknown Task"),
            description=task_data.get("description", "No description provided.")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
