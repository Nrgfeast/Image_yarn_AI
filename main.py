from fastapi import FastAPI, Request from fastapi.middleware.cors import CORSMiddleware import openai import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware( CORSMiddleware, allow_origins=[""], allow_credentials=True, allow_methods=[""], allow_headers=["*"], )

@app.get("/") def read_root(): return {"status": "OK"}

@app.post("/generate") async def generate_image(request: Request): data = await request.json() color_code = data.get("color_code", "D2020")  # Можно выбрать любой, если не передано

prompt = (
    f"A beautiful young woman with a Californian appearance wearing a knitted wool sweater "
    f"and a knitted hat, both in color {color_code}. She is outdoors in a natural setting, "
    f"like a forest or park, with soft daylight. The photo is high-resolution, natural style, "
    f"realistic fashion photography. The sweater and hat are clearly hand-knitted, with visible yarn texture."
)

try:
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="standard",
        response_format="url"
    )

    image_url = response.data[0].url
    return {"url": image_url}

except Exception as e:
    return {"error": f"Failed to generate image: {str(e)}"}

