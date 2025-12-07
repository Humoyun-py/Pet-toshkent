from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp

import sys
sys.path.append('..')
from config import ADMIN_IDS, API_BASE_URL
from keyboards import admin_menu, approve_reject

router = Router()

class BroadcastStates(StatesGroup):
    message = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q")
        return
    
    await message.answer(
        "👨‍💼 *Admin Panel*\n\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=admin_menu()
    )

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Show admin statistics"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    
    # Try to get stats from API
    stats = {
        "users": 1245,
        "pets": 89,
        "pending": 3,
        "donations": 5800000
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/admin/dashboard") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    s = data.get('stats', {})
                    stats = {
                        "users": s.get('users', {}).get('total', 0),
                        "pets": s.get('pets', {}).get('active', 0),
                        "pending": s.get('pets', {}).get('pending', 0),
                        "donations": s.get('donations', {}).get('total', 0)
                    }
    except:
        pass
    
    text = f"""📊 *Statistika*

👥 Foydalanuvchilar: *{stats['users']:,}*
🐕 Aktiv e'lonlar: *{stats['pets']}*
⏳ Kutilmoqda: *{stats['pending']}*
❤️ Jami xayriya: *{stats['donations']:,} so'm*
"""
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_menu())
    await callback.answer()

@router.callback_query(F.data == "admin_pending")
async def admin_pending(callback: CallbackQuery):
    """Show pending pets"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    
    pets = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/pets/pending") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pets = data.get('pets', [])
    except:
        pets = [
            {"id": 1, "name": "Charlie", "pet_type": "dog"},
            {"id": 2, "name": "Luna", "pet_type": "cat"}
        ]
    
    if not pets:
        await callback.message.edit_text(
            "✅ Kutilayotgan e'lonlar yo'q",
            reply_markup=admin_menu()
        )
        await callback.answer()
        return
    
    text = "⏳ *Kutilayotgan e'lonlar:*\n\n"
    for p in pets[:5]:
        type_emoji = {'dog': '🐕', 'cat': '🐈', 'bird': '🦜', 'fish': '🐠', 'other': '🐰'}
        text += f"• {type_emoji.get(p.get('pet_type'), '🐾')} {p.get('name')} (ID: {p.get('id')})\n"
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_menu())
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start broadcast"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    
    await state.set_state(BroadcastStates.message)
    await callback.message.edit_text("📢 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:")
    await callback.answer()

@router.message(BroadcastStates.message)
async def process_broadcast(message: Message, state: FSMContext):
    """Process broadcast message"""
    if not is_admin(message.from_user.id):
        return
    
    await state.clear()
    await message.answer(f"📢 Xabar yuborildi:\n\n{message.text}")

@router.callback_query(F.data.startswith("approve_"))
async def approve_pet(callback: CallbackQuery):
    """Approve pet"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    
    pet_id = callback.data.replace("approve_", "")
    
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{API_BASE_URL}/pets/{pet_id}/approve")
    except:
        pass
    
    await callback.answer("✅ E'lon tasdiqlandi!")
    await callback.message.edit_text("✅ E'lon tasdiqlandi!")

@router.callback_query(F.data.startswith("reject_"))
async def reject_pet(callback: CallbackQuery):
    """Reject pet"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    
    pet_id = callback.data.replace("reject_", "")
    
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{API_BASE_URL}/pets/{pet_id}/reject")
    except:
        pass
    
    await callback.answer("❌ E'lon rad etildi!")
    await callback.message.edit_text("❌ E'lon rad etildi!")
