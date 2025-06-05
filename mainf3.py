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
    full_prompt = (
    f"You are given a description of a clothing item from a real photo: {prompt}. "
    f"Generate the same garment, in {color_code} yarn color. "
    f"Keep the original type of garment (e.g. jacket, dress, coat), its shape, tailoring, and details. "
    f"The image should look like a studio photo, minimalistic background, ultra-realistic."
    )

    image_url = await generate_image(full_prompt)

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

async def generate_image(prompt):
    client = openai.OpenAI()
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        print("Ошибка генерации:", e)
        return None

# === РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ===

def register_your_item_handlers(app):
    app.add_handler(MessageHandler(filters.PHOTO, handle_user_item_photo))
    app.add_handler(CallbackQueryHandler(handle_color_selection, pattern="^your_color_"))
