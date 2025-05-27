from fastapi import FastAPI
from pydantic import BaseModel
import openai

# ВРЕМЕННЫЙ тестовый ключ (в реальности — никогда так не делать)
openai.api_key = "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"

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
        print("OPENAI RESPONSE:", response)

        if "data" in response and response["data"]:
            return {"url": response["data"][0]["url"]}
        else:
            return {"error": "No image returned from OpenAI"}

    except Exception as e:
        print("ERROR FROM OPENAI:", e)
        return {"error": str(e)}
