
from fastapi import FastAPI, Request
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI

app = FastAPI()
client = OpenAI()

COLOR_DESCRIPTIONS = {
    "D2077": "deep wine red",
    "D2073B": "raspberry pink",
    "D2021": "warm terracotta",
    "M125": "soft mint green",
    "D2074": "dusty rose",
    "D2016": "pale beige",
    "D2090": "sky blue",
    "D2013": "light gray",
    "D2125": "soft lavender",
    "D2020": "classic black",
    "D2014": "creamy white",
    "D2078": "deep navy blue"
}

@app.post("/generate_your_item")
async def generate_custom_item(request: Request):
    try:
        data = await request.json()
        print("🟢 Получен запрос в /generate_your_item с ключами:", list(data.keys()))

        color_code = data.get("color_code")
        base64_image = data.get("image_base64")

        if not base64_image or not color_code:
            print("🔴 Отсутствует image_base64 или color_code")
            return {"error": "Missing image or color"}

        if color_code not in COLOR_DESCRIPTIONS:
            print(f"🔴 Неизвестный код цвета: {color_code}")
            return {"error": "Unknown color code"}

        color_text = COLOR_DESCRIPTIONS[color_code]

        # GPT-4o: анализ изображения
        print("📷 Отправляем изображение на GPT-4o для описания...")
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
        print("📝 GPT-4o описание:", description)

        # Промпт на основе описания
        prompt = (
            f"Recreate the clothing item based on the following description: {description}. "
            f"The new version should be in {color_text}. Keep the original shape, texture, and style. "
            f"Use a clean studio background. High detail."
        )

        print("🎨 Отправляем запрос на DALL·E...")
        img_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = img_response.data[0].url
        print("✅ Изображение готово:", image_url)
        return {"url": image_url}

    except Exception as e:
        print("🔥 Ошибка во время генерации:", e)
        return {"error": f"Failed to generate customized item: {str(e)}"}
