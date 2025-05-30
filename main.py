
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

COLOR_DESCRIPTIONS = {
    "D2077": "deep midnight navy yarn",
    "D2073B": "stormy navy yarn",
    "D2021": "steel blue yarn",
    "M125": "indigo wool yarn",
    "D2074": "charcoal grey yarn",
    "D2016": "vivid royal blue yarn",
    "D2090": "deep magenta yarn",
    "D2013": "dark wine red yarn",
    "D2125": "vibrant orange yarn",
    "D2020": "golden yellow yarn",
    "D2014": "scarlet red yarn",
    "D2078": "black cherry yarn"
}

@app.post("/generate")
async def generate_image(request: Request):
    try:
        data = await request.json()
        color_code = data.get("color_code")

        if color_code not in COLOR_DESCRIPTIONS:
            return {"error": "Unknown color code"}

        color_text = COLOR_DESCRIPTIONS[color_code]

        prompt = (
            f"A stylish young woman wearing a thick hand-knitted sweater and a knitted hat, "
            f"both made from yarn in {color_text}. She is standing outdoors in soft natural light. "
            f"The knit texture is clearly visible and cozy. Do not use any other colors."
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        return {"url": image_url}

    except Exception as e:
        return {"error": f"Failed to generate image: {str(e)}"}
