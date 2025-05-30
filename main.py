from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Разрешаем запросы откуда угодно (можно ограничить при необходимости)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Человеческие описания цветов пряжи (продолжай использовать предыдущую таблицу)
COLOR_DESCRIPTIONS = {
    "D2077": "pale golden yellow yarn",
    "D2073B": "light pink yarn",
    "D2021": "deep red wine yarn",
    "M125": "muted beige yarn",
    "D2074": "soft tangerine orange yarn",
    "D2016": "creamy peach yarn",
    "D2090": "cool pastel mint yarn",
    "D2013": "gentle blue yarn",
    "D2125": "light lilac purple yarn",
    "D2020": "burgundy rose yarn",
    "D2014": "deep brown yarn",
    "D2078": "medium grey yarn"
}

@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    color_code = data.get("color_code", "")
    description = COLOR_DESCRIPTIONS.get(color_code, "yarn of a unique color")

    prompt = (
        f"A stylish young woman wearing a finely knitted sweater and a knitted hat, "
        f"both made from {description}. The yarn is delicate and about 3mm thick, "
        f"giving a soft and elegant texture. She is outdoors in a natural setting, "
        f"with realistic lighting and fashionable composition."
    )

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return {"url": response.data[0].url}
    except Exception as e:
        return {"error": f"Failed to generate image: {e}"}