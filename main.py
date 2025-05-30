
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

COLOR_DESCRIPTIONS = {
    "D2077": "deep moss green (RGB #556B2F)",
    "D2073B": "charcoal black (RGB #2F2F2F), matte",
    "D2021": "ruby red (RGB #8B0000), knitted wool",
    "M125": "mustard yellow (RGB #D4AF37), matte yarn",
    "D2074": "warm woolen gray (RGB #A9A9A9)",
    "D2016": "burgundy (RGB #800020), rich knit",
    "D2090": "natural cotton beige (RGB #F5F5DC)",
    "D2013": "washed denim blue (RGB #3C6382)",
    "D2125": "pastel lilac (RGB #C8A2C8)",
    "D2020": "dusty rose (RGB #DCAE96)",
    "D2014": "deep maroon (RGB #4B0000)",
    "D2078": "pale pink (RGB #FFD1DC)",
}

@app.post("/generate")
async def generate_image(request: Request):
    try:
        data = await request.json()
        color_code = data.get("color_code")
        if not color_code or color_code not in COLOR_DESCRIPTIONS:
            return {"error": "Invalid color code"}

        prompt = (
            f"A fashion model wearing a hand-knitted wool sweater and a knitted hat, "
            f"both in {COLOR_DESCRIPTIONS[color_code]}. She is outdoors in a natural setting, "
            f"standing in sunlight. The sweater and hat are clearly visible. Do not use any other colors."
        )

        response = openai.Image.create(
            prompt=prompt,
            model="dall-e-3",
            n=1,
            size="1024x1024"
        )

        image_url = response["data"][0]["url"]
        return {"url": image_url}
    except Exception as e:
        return {"error": f"Failed to generate image: {str(e)}"}
