from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class PromptData(BaseModel):
    color_code: str

@app.post("/generate")
async def generate_image(data: PromptData):
    prompt = f"A mannequin in a hand-knitted sweater in yarn color {data.color_code}, outdoor natural background, soft lighting"
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return {"url": response["data"][0]["url"]}
    except Exception as e:
        return {"error": str(e)}
