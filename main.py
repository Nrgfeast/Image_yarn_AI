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
    prompt = f"A stylish knitted garment made of yarn in the color {req.color_code}, worn outdoors by a model"
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
