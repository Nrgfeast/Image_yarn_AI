from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class GenerateRequest(BaseModel):
    color_code: str

@app.post("/generate")
async def generate_image(req: GenerateRequest):
    prompt = prompt = (
    f"A beautiful young woman with a Californian appearance wearing a knitted wool sweater "
    f"and a knitted hat, both in color {color_code}. She is outdoors in a natural setting, "
    f"like a forest or park, with soft daylight. The photo is high-resolution, natural style, "
    f"realistic fashion photography. The sweater and hat are clearly hand-knitted, with visible yarn texture."
)
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            style="natural"
        )
        image_url = response.data[0].url
        return {"url": image_url}
    except Exception as e:
        return JSONResponse(content={"error": f"ERROR FROM OPENAI: {str(e)}"}, status_code=500)
