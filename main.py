from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai

openai.api_key = "ВСТАВЬ_СЮДА_СВОЙ_API_КЛЮЧ"

app = FastAPI()

class PromptRequest(BaseModel):
    color_code: str

@app.post("/generate")
async def generate_image(data: PromptRequest):
    prompt = f"A mannequin wearing a hand-knitted sweater in yarn color {data.color_code}, nature background, soft natural lighting"

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return {"url": response["data"][0]["url"]}

    except Exception as e:
        return {"error": str(e)}
