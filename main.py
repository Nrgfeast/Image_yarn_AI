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
    "D2077": "very dark navy blue yarn",
    "D2073B": "deep twilight blue yarn",
    "D2021": "classic navy yarn",
    "M125": "medium slate grey yarn",
    "D2074": "charcoal graphite yarn",
    "D2016": "bright royal blue yarn",
    "D2090": "rich raspberry pink yarn",
    "D2013": "dark wine burgundy yarn",
    "D2125": "vivid pumpkin orange yarn",
    "D2020": "golden sunflower yellow yarn",
    "D2014": "bold scarlet red yarn",
    "D2078": "black cherry yarn (nearly black red)"
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
            f"A beautiful young woman is wearing a hand-knitted sweater and matching hat made from {color_text}. "
            f"The yarn is fine and delicate, about 3mm thick, with a close-knit texture — not bulky or chunky. "
            f"She stands outdoors in soft natural light. "
            f"The clothing is stylish, realistic, and fully knitted. Do not use any patterns or color variations."
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

@app.post("/generate_your_item")
async def generate_custom_item(request: Request):
    try:
        data = await request.json()
        color_code = data.get("color_code")
        base64_image = data.get("image_base64")

        if not base64_image or not color_code:
            return {"error": "Missing image or color"}

        if color_code not in COLOR_DESCRIPTIONS:
            return {"error": "Unknown color code"}

        color_text = COLOR_DESCRIPTIONS[color_code]

        # GPT-4o: анализ изображения
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Describe in detail the clothing item in this photo. Emphasize style, texture, shape, and type of garment."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
        )
        description = response.choices[0].message.content
        print("GPT-4o description:", description)

        # Промпт на основе описания
        prompt = (
            f"Recreate the clothing item based on the following description: {description}. "
            f"The new version should be in {color_text}. Keep the original shape, texture, and style. "
            f"Use a clean studio background. High detail."
        )

        img_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = img_response.data[0].url
        return {"url": image_url}

    except Exception as e:
        return {"error": f"Failed to generate customized item: {str(e)}"}
