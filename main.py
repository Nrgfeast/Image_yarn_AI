from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import random

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
    "D2078": "black cherry yarn (nearly black red)",
    "D2029": "royal violet yarn with rich blue undertones",
    "M232": "dusty plum yarn with muted purple-brown tone",
    "D2034": "pale taupe grey yarn with warm beige haze",
    "D2000": "deep chestnut brown yarn with reddish warmth",
    "D2068": "soft lavender grey yarn with cool undertone",
    "D2116": "black spruce green yarn with forest depth",
    "M993": "dark mossy pine yarn with earthy depth",
    "M152": "fresh emerald green yarn with vibrant sheen",
    "D2040": "muted olive yarn with natural hazel tone",
    "D2039": "icy arctic blue yarn with frosted fuzz",
    "D2095": "spring meadow green yarn with leaf softness",
    "M193": "luminous chartreuse yarn with neon glow",
    "D2033": "deep ocean blue yarn with denim intensity",
    "M122": "dusty blue-grey yarn with soft overcast tone",
    "D2044": "classic slate grey yarn with bluish tint",
    "M267": "weathered steel yarn with stonewashed finish",
    "M102": "foggy morning blue yarn with cool mist",
    "M264": "powdered lilac yarn with porcelain base",
    "M270": "hazy periwinkle yarn with gentle pastel glow",
    "M195": "clear sky blue yarn with breezy vibrancy",
    "M243": "deep rosewood yarn with earthy red warmth",
    "D2067": "bold mulberry yarn with rich purple tone",
    "D2066": "classic raspberry pink yarn with a satin sheen",
    "M234": "dusty coral yarn with soft salmon undertone",
    "D2033": "muted beige yarn with a grounded wheat hue",
    "D2085": "camel sand yarn with warm tan depth",
    "D2028": "honey oat yarn with creamy softness",
    "M306": "pastel buttermilk yarn with golden warmth",
    "D2084": "ash lilac yarn with a foggy violet veil",
    "M233": "mauve grey yarn with whispery purple shadows",
    "M110": "faded lavender yarn with gentle plum tint",
    "M143": "powder rose yarn with a quiet vintage hue",
    "M130": "rosy blossom yarn with fresh floral blush",
    "D2089": "pink quartz yarn with dusty undertone",
    "M137": "silver violet yarn with a cool iris glow",
    "M107": "misty lilac yarn with soft bluish frost",
    "D2024": "charcoal moss yarn with deep olive undertone",
    "M272": "steel mist yarn with cool grey-blue hue",
    "M273": "aged straw yarn with muted parchment tone",
    "M238": "powdered rose beige yarn with vintage softness",
    "D2019": "soft stone yarn with a foggy limestone feel",
    "M240": "frosted cloud yarn with whispering blue tint",
    "M219": "pale almond yarn with milky warm glow",
    "M315": "baby ice blue yarn with arctic pastel tone",
    "M254": "stormy sky yarn with a marine grey finish",
    "D2027": "overcast silver yarn with soft steel reflection",
    "D2030": "driftwood taupe yarn with sandy beige hue",
    "D2103": "light oat yarn with a buttery linen touch",
    "D2042": "faded sage yarn with quiet herbal tone",
    "D2003": "ivory chalk yarn with bone-white clarity",
    "D2098": "linen cream yarn with subtle milk warmth",
    "D2018": "porcelain white yarn with clean daylight edge"
}

@app.post("/generate")
@app.post("/generate")
async def generate_image(request: Request):
    try:
        data = await request.json()
        color_code = data.get("color_code")
        gender = data.get("gender", "gender_woman")  # По умолчанию — женская одежда

        if color_code not in COLOR_DESCRIPTIONS:
            return {"error": "Unknown color code"}

        color_text = COLOR_DESCRIPTIONS[color_code]

        # Выбор описания по полу
        if gender == "gender_man":
            subject = "A confident young man is wearing a modern knitted pullover made from"
            intro = "He is in the full figure is clearly visible from head to toe, standing outdoors in soft natural light with a realistic masculine build."
        elif gender == "gender_kids":
            if random.random() < 0.55:
                subject = "A smiling young boy is dressed in a handmade knitted sweater made from"
                intro = "He is standing outside in full body view, head to toe visible, with casual posture and natural lighting."
            else:
                subject = "A cheerful little girl is wearing a hand-knitted outfit made from"
                intro = "She is captured in full-body standing view, with playful posture in natural soft daylight."
        else:  # gender_woman (по умолчанию)
            subject = "A beautiful young woman is wearing a hand-knitted sweater and matching hat made from"
            intro = "She is standing outdoors, visible in full body from head to toe, with soft natural light."

        prompt = (
            f"{subject} {color_text}. "
            f"The yarn is fine and delicate, about 3mm thick, with a close-knit texture — not bulky or chunky. "
            f"{intro} "
            f"The clothing is stylish, realistic, and entirely knitted. Avoid patterns, logos, or color variations."
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
        print("🟢 Запрос в /generate_your_item с ключами:", list(data.keys()))

        color_code = data.get("color_code")
        base64_image = data.get("image_base64")

        if not base64_image or not color_code:
            return {"error": "Missing image or color"}

        if color_code not in COLOR_DESCRIPTIONS:
            return {"error": "Unknown color code"}

        color_text = COLOR_DESCRIPTIONS[color_code]

        # GPT-4o: анализ изображения
        gpt_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Describe in detail the clothing item in this photo. Include type (e.g. jacket, dress), material (e.g. knitted, cotton), texture, and structure. Focus especially on whether the item is knitted."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
        )
        description = gpt_response.choices[0].message.content

        # Сборка промпта для DALL·E
        prompt = (
            f"Recreate the clothing item from the following description: {description}. "
            f"The new version must be in {color_text} (yarn shade code {color_code}). "
            f"Keep the original shape, texture, material, and garment type. "
            f"Render the item in ultra-realistic detail, with a plain studio background."
        )

        image_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = image_response.data[0].url
        return {"url": image_url}

    except Exception as e:
        return {"error": f"Failed to generate custom item: {str(e)}"}
