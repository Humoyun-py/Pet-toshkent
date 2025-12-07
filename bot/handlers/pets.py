from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import aiohttp

import sys
sys.path.append('..')
from config import API_BASE_URL, MESSAGES
from keyboards import pets_navigation

router = Router()

@router.message(Command("pets"))
@router.message(F.text == "🐕 Hayvonlar")
async def cmd_pets(message: Message):
    """Show pets list"""
    pets = await get_pets()
    
    if not pets:
        await message.answer(MESSAGES['no_pets'])
        return
    
    await show_pet(message, pets, 0)

async def get_pets():
    """Fetch pets from API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/pets/list") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('pets', [])
    except:
        pass
    
    # Demo data
    return [
        {"id": 1, "name": "Charlie", "pet_type": "dog", "breed": "Golden Retriever", "age": "2 yil", "status": "selling", "price": 3500000, "location": "Yunusobod"},
        {"id": 2, "name": "Luna", "pet_type": "cat", "breed": "British Shorthair", "age": "1 yil", "status": "free", "price": 0, "location": "Chilonzor"},
        {"id": 3, "name": "Max", "pet_type": "dog", "breed": "Labrador", "age": "3 yil", "status": "foster", "price": 0, "location": "Sergeli"},
    ]

async def show_pet(message: Message, pets: list, index: int):
    """Display single pet with navigation"""
    if not pets or index >= len(pets):
        return
    
    pet = pets[index]
    type_emoji = {'dog': '🐕', 'cat': '🐈', 'bird': '🦜', 'fish': '🐠', 'other': '🐰'}
    status_names = {'selling': '💰 Sotiladi', 'free': '🎁 Bepul', 'foster': '🏠 Foster', 'adoption': '❤️ Adoptsiya'}
    
    text = f"""{type_emoji.get(pet.get('pet_type'), '🐾')} *{pet.get('name')}*

🏷 *Zoti:* {pet.get('breed', '-')}
📅 *Yoshi:* {pet.get('age', '-')}
📋 *Status:* {status_names.get(pet.get('status'), pet.get('status'))}
💰 *Narxi:* {pet.get('price', 0):,} so'm
📍 *Joylashuv:* {pet.get('location', 'Toshkent')}
"""
    
    keyboard = pets_navigation(index + 1, len(pets), pet.get('id'))
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data.startswith("page_"))
async def change_page(callback: CallbackQuery):
    """Handle pagination"""
    page = int(callback.data.replace("page_", ""))
    pets = await get_pets()
    
    if pets and 0 < page <= len(pets):
        pet = pets[page - 1]
        type_emoji = {'dog': '🐕', 'cat': '🐈', 'bird': '🦜', 'fish': '🐠', 'other': '🐰'}
        status_names = {'selling': '💰 Sotiladi', 'free': '🎁 Bepul', 'foster': '🏠 Foster', 'adoption': '❤️ Adoptsiya'}
        
        text = f"""{type_emoji.get(pet.get('pet_type'), '🐾')} *{pet.get('name')}*

🏷 *Zoti:* {pet.get('breed', '-')}
📅 *Yoshi:* {pet.get('age', '-')}
📋 *Status:* {status_names.get(pet.get('status'), pet.get('status'))}
💰 *Narxi:* {pet.get('price', 0):,} so'm
📍 *Joylashuv:* {pet.get('location', 'Toshkent')}
"""
        keyboard = pets_navigation(page, len(pets), pet.get('id'))
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    await callback.answer()

@router.callback_query(F.data.startswith("contact_"))
async def contact_owner(callback: CallbackQuery):
    """Show owner contact info"""
    pet_id = callback.data.replace("contact_", "")
    await callback.answer("📱 Egasi bilan bog'lanish uchun saytga tashrif buyuring: pettashkent.uz", show_alert=True)

@router.message(Command("my"))
@router.message(F.text == "📋 Mening e'lonlarim")
async def my_pets(message: Message):
    """Show user's pets"""
    await message.answer("📋 Sizning e'lonlaringizni ko'rish uchun saytda ro'yxatdan o'ting: pettashkent.uz")
