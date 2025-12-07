from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sys
sys.path.append('..')
from keyboards import donation_amounts

router = Router()

class DonationStates(StatesGroup):
    amount = State()

@router.message(Command("donate"))
@router.message(F.text == "❤️ Xayriya")
async def cmd_donate(message: Message):
    """Show donation options"""
    text = """❤️ *Xayriya qilish*

Sizning xayriyangiz priyutlardagi hayvonlarga:
• 🍖 Oziq-ovqat
• 💊 Davolash
• 🏠 Boshpana

ta'minlashga yordam beradi.

Miqdorni tanlang:"""
    
    await message.answer(text, parse_mode="Markdown", reply_markup=donation_amounts())

@router.callback_query(F.data.startswith("donate_"))
async def process_donation(callback: CallbackQuery, state: FSMContext):
    """Handle donation amount selection"""
    amount_str = callback.data.replace("donate_", "")
    
    if amount_str == "custom":
        await state.set_state(DonationStates.amount)
        await callback.message.edit_text("💰 Xayriya miqdorini kiriting (so'm):")
        await callback.answer()
        return
    
    amount = int(amount_str)
    await show_payment_options(callback.message, amount)
    await callback.answer()

@router.message(DonationStates.amount)
async def process_custom_amount(message: Message, state: FSMContext):
    """Handle custom donation amount"""
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        if amount < 1000:
            await message.answer("❌ Minimal miqdor: 1,000 so'm")
            return
    except:
        await message.answer("❌ Iltimos, raqam kiriting")
        return
    
    await state.clear()
    await show_payment_options(message, amount)

async def show_payment_options(message: Message, amount: int):
    """Show payment links"""
    text = f"""💳 *To'lov*

Miqdor: *{amount:,} so'm*

To'lov usulini tanlang:

🔵 *Click:* [To'lov qilish](https://my.click.uz)
🟢 *Payme:* [To'lov qilish](https://payme.uz)

Yoki karta raqami orqali:
`8600 1234 5678 9012`

Xayriyangiz uchun rahmat! ❤️"""
    
    await message.answer(text, parse_mode="Markdown")
