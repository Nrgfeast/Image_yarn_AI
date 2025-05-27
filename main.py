from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import time

REPLICATE_API_TOKEN = "r8_8avES9n9VW93xTWCPjq8LqgV2flJuNP3Cwm05"  # ЗАМЕНИ на свой

app = FastAPI()

class PromptData(BaseModel):
    color_code: str

@app.post("/generate")
async def generate_image(data: PromptData):
    prompt = f"A generated model wearing a hand-knitted sweater in yarn color {data.color_code}, standing in nature, cinematic lighting, high quality"

    try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "version": "a9758cbf0b28ec9c980e7a7ac0e5f7b219b1e90ec541e649530ee23c57c189b1",  # SDXL 1.0
                "input": {
                    "prompt": prompt,
                    "width": 512,
                    "height": 512
                }
            }
        )

        if response.status_code != 201:
            return { "error": f"Failed to start generation: {response.text}" }

        prediction = response.json()
        prediction_url = prediction["urls"]["get"]

        for _ in range(30):
            time.sleep(2)
            result = requests.get(prediction_url, headers={ "Authorization": f"Token {REPLICATE_API_TOKEN}" }).json()
            if result["status"] == "succeeded":
                return { "url": result["output"][0] }
            elif result["status"] == "failed":
                return { "error": "Generation failed." }

        return { "error": "Timed out waiting for generation." }

    except Exception as e:
        return { "error": str(e) }
