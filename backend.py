from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import SuggestRequest, SuggestResponse, ReplacementItem
from openai import OpenAI
from pydantic import BaseModel
from prompts import PROMPT
import os

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

class AIResponse(BaseModel):
    suggestion: str
    replacement: list[ReplacementItem]

@app.post("/suggest", response_model=SuggestResponse)
async def suggest(request: SuggestRequest):
    try:
        # Check whether the prompt is provided  
        if request.prompt is None or request.prompt == "":
            prompt = PROMPT.format(knowledge_base=request.knowledge_base, current_text=request.text)
        else:
            prompt = request.prompt.format(knowledge_base=request.knowledge_base, current_text=request.text)
        completion = client.beta.chat.completions.parse(
            # model="gpt-4o-mini", 
            model="gpt-4o-2024-08-06", 
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=SuggestResponse
        )
        print(completion)
        return completion.choices[0].message.parsed

    except Exception as e:
        return SuggestResponse(
            status="error",
            error_message=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

