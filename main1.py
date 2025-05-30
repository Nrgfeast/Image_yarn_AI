
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


@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    color_code = data.get("color_code", "neutral gray")

    try:
        prompt = (
            f"A stylish young woman wearing a knitted sweater and a knitted hat, "
            f"both made from yarn of color {color_code}. She is outdoors in a natural setting, "
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
