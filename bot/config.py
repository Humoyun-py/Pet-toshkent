import os

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN') or 'YOUR_BOT_TOKEN_HERE'

# API configuration
API_BASE_URL = os.environ.get('API_BASE_URL') or 'http://localhost:5000/api'

# Admin IDs (Telegram user IDs who can use admin commands)
ADMIN_IDS = [123456789]  # Add your Telegram user ID here

# Messages
MESSAGES = {
    'welcome': """🐾 *Pet Tashkent* ga xush kelibsiz!

Shahar hayvonlari uchun yagona platforma.

Bu bot orqali siz:
• 🐕 Hayvon e'loni berishingiz
• 🔍 Hayvonlarni qidirishingiz
• 🏥 Yaqin veterinar klinikalarni topishingiz
• ❤️ Xayriya qilishingiz mumkin

Quyidagi tugmalardan birini tanlang:""",
    
    'help': """📚 *Yordam*

/start - Botni boshlash
/pets - Hayvonlarni ko'rish
/add - Yangi hayvon qo'shish
/clinics - Yaqin klinikalar
/donate - Xayriya qilish
/my - Mening e'lonlarim
/help - Yordam

Savollaringiz bo'lsa: @PetTashkentSupport
""",

    'add_name': "📝 Hayvon nomini kiriting:",
    'add_type': "🐾 Hayvon turini tanlang:",
    'add_breed': "🏷 Zotini kiriting (yoki 'o'tkazib yuborish'):",
    'add_age': "📅 Yoshini kiriting (masalan: 2 yil):",
    'add_status': "📋 E'lon turini tanlang:",
    'add_price': "💰 Narxini kiriting (so'm):",
    'add_photo': "📷 Hayvon rasmini yuboring:",
    'add_location': "📍 Joylashuvni tanlang:",
    'add_success': "✅ E'lon muvaffaqiyatli qo'shildi! Admin tasdiqlashidan so'ng e'lon qilinadi.",
    
    'no_pets': "😔 Hozircha hayvonlar yo'q.",
    'send_location': "📍 Joylashuvingizni yuboring:",
}
