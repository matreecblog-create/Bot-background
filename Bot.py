import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# ---------------- بيانات البوت ----------------
# التوكن الخاص بك
API_TOKEN = '8082451147:AAH5TjZgxLoVYrDNVmJvXoDZgynwy6dM--w'

# رابط الـ CPA (الخاص بك)
CPA_LINK = "https://trianglerockers.com/1868973"

# إعدادات Wallhaven API
WALLHAVEN_SEARCH_URL = "https://wallhaven.cc/api/v1/search"
WALLHAVEN_IMAGE_URL = "https://wallhaven.cc/api/v1/w/{}"

# إعدادات السجلات (Logging)
logging.basicConfig(level=logging.INFO)

# تهيئة البوت
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ---------------- الأزرار (Keyboards) ----------------

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📱 AMOLED / Dark", callback_data="cat_amoled")],
        [InlineKeyboardButton(text="🤖 AI Art", callback_data="cat_ai_art")],
        [InlineKeyboardButton(text="🎮 Gaming", callback_data="cat_gaming")],
        [InlineKeyboardButton(text="🌌 Nature & Minimal", callback_data="cat_nature")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def download_keyboard(image_id):
    keyboard = [
        [InlineKeyboardButton(text="🔒 فتح وتحميل (Original 4K)", callback_data=f"lock_{image_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def cpa_link_keyboard(image_id):
    keyboard = [
        [InlineKeyboardButton(text="🔓 اضغط هنا لفك القفل", url=CPA_LINK)],
        [InlineKeyboardButton(text="✅ تم، ابدأ التحميل", callback_data=f"verify_{image_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ---------------- الوظائف (Logic) ----------------

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = (
        f"مرحباً {message.from_user.first_name} 👋\n\n"
        "أهلاً بك في **VisionWalls** 🌌\n"
        "أفضل بوت لتحميل خلفيات 4K الحقيقية.\n\n"
        "👇 **اختر القسم المفضل لديك:**"
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())

# --- دالة البحث (تم الإصلاح هنا) ---
async def fetch_wallpapers(query):
    params = {
        'q': query,
        'sorting': 'random',
        'purity': '100', 
        'limit': 3
    }
    # إضافة الهوية لتجاوز الحظر
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(WALLHAVEN_SEARCH_URL, params=params, headers=headers)
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            return data['data']
        return []
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

async def get_full_image_url(image_id):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get(WALLHAVEN_IMAGE_URL.format(image_id), headers=headers)
        data = response.json()
        return data['data']['path']
    except:
        return None

# --- معالجة الأزرار ---

@dp.callback_query(lambda c: c.data.startswith('cat_'))
async def process_category(callback_query: types.CallbackQuery):
    cat_map = {'cat_amoled': 'amoled', 'cat_ai_art': 'ai art', 'cat_gaming': 'gaming', 'cat_nature': 'nature'}
    query = cat_map.get(callback_query.data, 'general')
    
    await bot.answer_callback_query(callback_query.id, "جاري البحث... ⏳")
    
    images = await fetch_wallpapers(query)
    
    if not images:
        await bot.send_message(callback_query.from_user.id, "⚠️ لم يتم العثور على صور، حاول مرة أخرى لاحقاً.")
        return

    for img in images:
        thumb = img['thumbs']['large']
        res = img['resolution']
        img_id = img['id']
        caption = f"💎 الدقة: {res}\n🆔 #{img_id}"
        
        await bot.send_photo(
            chat_id=callback_query.from_user.id,
            photo=thumb,
            caption=caption,
            reply_markup=download_keyboard(img_id)
        )

@dp.callback_query(lambda c: c.data.startswith('lock_'))
async def process_lock(callback_query: types.CallbackQuery):
    image_id = callback_query.data.split("_")[1]
    msg_text = "⚠️ **محتوى محمي**\n\nاضغط على الرابط أدناه لفك القفل، ثم اضغط 'تم' للتحميل."
    await bot.send_message(callback_query.from_user.id, msg_text, reply_markup=cpa_link_keyboard(image_id))
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query(lambda c: c.data.startswith('verify_'))
async def process_verify(callback_query: types.CallbackQuery):
    image_id = callback_query.data.split("_")[1]
    await bot.answer_callback_query(callback_query.id, "جاري التحقق وإرسال الملف... 🔄")
    
    full_url = await get_full_image_url(image_id)
    if full_url:
        await bot.send_document(chat_id=callback_query.from_user.id, document=full_url, caption="✅ تم التحميل بنجاح!")
    else:
        await bot.send_message(callback_query.from_user.id, "خطأ في جلب الملف، حاول مجدداً.")

# تشغيل البوت
async def main():
    print("✅ Bot is RUNNING successfully...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
