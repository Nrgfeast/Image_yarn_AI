
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
    "D2077": ("warm golden yellow", (218, 168, 35)),
    "D2073B": ("dusty olive green", (153, 158, 110)),
    "D2021": ("light plum purple", (183, 145, 168)),
    "M125": ("classic red", (164, 64, 65)),
    "D2074": ("neutral light grey", (182, 178, 173)),
    "D2016": ("soft peach pink", (243, 192, 177)),
    "D2090": ("rose beige", (212, 175, 166)),
    "D2013": ("deep cherry red", (145, 64, 67)),
    "D2125": ("terracotta orange", (196, 107, 82)),
    "D2020": ("bold crimson", (155, 50, 60)),
    "D2014": ("muted burgundy", (137, 73, 86)),
    "D2078": ("greyish stone", (185, 183, 180)),
}

@app.post("/generate")
async def generate_image(request: Request):
    try:
        data = await request.json()
        color_code = data.get("color_code")

        if color_code not in COLOR_DESCRIPTIONS:
            return {"error": "Unknown color code"}

        color_name, rgb = COLOR_DESCRIPTIONS[color_code]
        r, g, b = rgb

        prompt = (
            f"A beautiful young woman wearing a knitted sweater and a knitted hat, "
            f"both made from yarn in a precise color with RGB ({r}, {g}, {b}) — described as {color_name}. "
            f"The texture is thick and clearly knitted. She is standing outdoors in a natural setting, "
            f"shot in soft natural lighting, realistic photography, front view."
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
