from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import aiohttp

import sys
sys.path.append('..')
from config import API_BASE_URL, MESSAGES

router = Router()

@router.message(Command("clinics"))
@router.message(F.text == "🏥 Klinikalar")
async def cmd_clinics(message: Message):
    """Show clinics list"""
    # Request location
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvimni yuborish", request_location=True)],
            [KeyboardButton(text="🏠 Bosh menyu")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "🏥 *Yaqin atrofdagi veterinar klinikalar*\n\n"
        "Yaqin klinikalarni topish uchun joylashuvingizni yuboring yoki barcha klinikalarni ko'ring:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    # Also show all clinics
    clinics = await get_clinics()
    if clinics:
        text = "📋 *Barcha klinikalar:*\n\n"
        for i, c in enumerate(clinics[:5], 1):
            text += f"{i}. 🏥 *{c.get('name')}*\n"
            text += f"   📍 {c.get('address')}\n"
            text += f"   📞 {c.get('phone', '-')}\n"
            text += f"   🕐 {c.get('working_hours', '-')}\n\n"
        
        await message.answer(text, parse_mode="Markdown")

@router.message(F.location)
async def handle_location(message: Message):
    """Handle user location and find nearby clinics"""
    lat = message.location.latitude
    lng = message.location.longitude
    
    await message.answer("🔍 Yaqin klinikalar qidirilmoqda...")
    
    # Find nearby clinics
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/clinics/near",
                json={"lat": lat, "lng": lng, "radius": 5}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    clinics = data.get('clinics', [])
                    
                    if clinics:
                        text = "📍 *Sizga yaqin klinikalar:*\n\n"
                        for i, c in enumerate(clinics[:5], 1):
                            text += f"{i}. 🏥 *{c.get('name')}*\n"
                            text += f"   📍 {c.get('address')}\n"
                            text += f"   📞 {c.get('phone', '-')}\n"
                            if c.get('distance'):
                                text += f"   🚶 {c.get('distance')} km\n"
                            text += "\n"
                        
                        await message.answer(text, parse_mode="Markdown")
                    else:
                        await message.answer("😔 Yaqin atrofda klinikalar topilmadi.")
                    return
    except:
        pass
    
    # Fallback to demo
    clinics = await get_clinics()
    text = "📍 *Yaqin klinikalar:*\n\n"
    for i, c in enumerate(clinics[:3], 1):
        text += f"{i}. 🏥 *{c.get('name')}*\n"
        text += f"   📍 {c.get('address')}\n"
        text += f"   📞 {c.get('phone', '-')}\n\n"
    
    await message.answer(text, parse_mode="Markdown")

async def get_clinics():
    """Fetch clinics from API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/clinics/list") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('clinics', [])
    except:
        pass
    
    # Demo data
    return [
        {"id": 1, "name": "Tashkent Veterinary Clinic", "address": "Amir Temur ko'chasi, 100", "phone": "+998712345678", "working_hours": "09:00-18:00"},
        {"id": 2, "name": "Pet Care Center", "address": "Navoiy ko'chasi, 55", "phone": "+998712345679", "working_hours": "24/7"},
        {"id": 3, "name": "Zoo Veterinar", "address": "Chilonzor, 12-mavze", "phone": "+998712345680", "working_hours": "08:00-20:00"},
    ]
