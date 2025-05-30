
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

# Разрешить CORS (чтобы бот мог обращаться к серверу)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Описания цветов для каждого кода
COLOR_DESCRIPTIONS = {
    "D2077": "black",
    "D2073B": "black",
    "D2021": "dark slate gray",
    "M125": "midnight blue",
    "D2074": "black",
    "D2016": "navy blue",
    "D2090": "dark magenta",
    "D2013": "maroon",
    "D2125": "orange",
    "D2020": "gold",
    "D2014": "firebrick",
    "D2078": "black"
}

@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    color_code = data.get("color_code", "D2020")
    color_description = COLOR_DESCRIPTIONS.get(color_code, "a soft natural color")

    try:
        prompt = (
            f"A stylish young woman wearing a knitted sweater and a knitted hat, "
            f"both made from yarn in {color_description} color. She is outdoors in a natural setting, "
            f"like a park or forest. Soft natural daylight. Realistic photo."
        )

        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        return {"url": image_url}

    except Exception as e:
        return {"error": f"Failed to generate image: {str(e)}"}
