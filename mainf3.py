from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
import os
import base64
import openai

# === ПЕРВАЯ ТОЧКА ВХОДА: НАЖАТИЕ НА КНОПКУ 3 ===

async def start_your_item_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Загрузите изображение вашего изделия (например, фотографии свитера):")
    context.user_data["awaiting_user_item_photo"] = True

# === ВТОРАЯ ТОЧКА: ПОЛУЧЕНИЕ ИЗОБРАЖЕНИЯ ОТ ПОЛЬЗОВАТЕЛЯ ===

async def handle_user_item_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_user_item_photo"):
        return

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    photo_path = "user_item.jpg"
    await file.download_to_drive(photo_path)

    context.user_data["user_item_photo_path"] = photo_path
    context.user_data["awaiting_user_item_photo"] = False
    context.user_data["awaiting_color_choice"] = True

    await update.message.reply_photo(
        photo=open("palette.png", "rb"),
        caption="Выберите интересующий цвет:",
        reply_markup=build_palette_keyboard()
    )

# === ТРЕТЬЯ ТОЧКА: ВЫБОР ЦВЕТА ===

COLOR_CODES = [
    "D2077", "D2073B", "D2021", "M125",
    "D2074", "D2016", "D2090", "D2013",
    "D2125", "D2020", "D2014", "D2078"
]

COLOR_DESCRIPTIONS = {
    "D2077": "delicate lilac pink yarn",
    "D2073B": "deep marsala red yarn",
    "D2021": "warm terracotta orange yarn",
    "M125": "soft pastel mint yarn",
    "D2074": "dusty rose pink yarn",
    "D2016": "light beige sand-colored yarn",
    "D2090": "sky blue cotton yarn",
    "D2013": "classic light gray yarn",
    "D2125": "pale lavender violet yarn",
    "D2020": "rich matte black yarn",
    "D2014": "creamy off-white yarn",
    "D2078": "deep navy ocean blue yarn"
}



def build_palette_keyboard():
    keyboard = []
    row = []
    for i, code in enumerate(COLOR_CODES):
        row.append(InlineKeyboardButton(code, callback_data=f"your_color_{code}"))
        if (i + 1) % 4 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def handle_color_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("awaiting_color_choice"):
        return

    color_code = query.data.replace("your_color_", "")
    photo_path = context.user_data.get("user_item_photo_path")

    prompt = await describe_image(photo_path)
    color_text = COLOR_DESCRIPTIONS.get(color_code, color_code)

    full_prompt = (
    f"Generate an ultra-realistic studio photo of the same garment as in the photo, "
    f"but recolored into {color_text}. "
    f"Preserve the original garment’s shape, tailoring, texture, and style. "
    f"The background should be neutral and minimalistic."
)

    image_url = await generate_image(full_prompt, color_code=color_code, image_path=photo_path)

    if image_url:
        await query.message.reply_photo(
            photo=image_url,
            caption=f"Готово! Изделие в цвете {color_code}"
        )
    else:
        await query.message.reply_text("Ошибка генерации изображения 😔")

    keyboard = [[
        InlineKeyboardButton("🔁 Новый выбор", callback_data="your_item"),
        InlineKeyboardButton("🏠 В меню", callback_data="start_over")
    ]]
    await query.message.reply_text("Что дальше?", reply_markup=InlineKeyboardMarkup(keyboard))

    context.user_data.clear()

# === GPT-4o: ВИЗУАЛЬНОЕ ОПИСАНИЕ ===

async def describe_image(image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Describe in detail the clothing item in this photo. Emphasize style, texture, shape, type of garment."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]
    )
    return response.choices[0].message.content
    description = response.choices[0].message.content
print("GPT-4o description:", description)
return description
# === DALL·E: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ ===

import requests

async def generate_image(prompt, color_code=None, image_path=None):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        response = requests.post(
            "https://image-yarn-ai.onrender.com/generate_your_item",
            json={
                "prompt": prompt,  # 💥 ЭТО ГЛАВНОЕ: передаём prompt
                "color_code": color_code,
                "image_base64": img_base64
            },
            timeout=120
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("url")
        else:
            print("Ошибка от сервера Render:", response.text)
            return None
    except Exception as e:
        print("Ошибка запроса к Render:", e)
        return None

# === РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ===

def register_your_item_handlers(app):
    app.add_handler(MessageHandler(filters.PHOTO, handle_user_item_photo))
    app.add_handler(CallbackQueryHandler(handle_color_selection, pattern="^your_color_"))
