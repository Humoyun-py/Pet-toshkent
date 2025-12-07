from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import aiohttp
import sys
sys.path.append('..')
from config import MESSAGES, API_BASE_URL
from keyboards import main_menu, pet_types, pet_status, locations, skip_button, confirm_keyboard

router = Router()

class AddPetStates(StatesGroup):
    name = State()
    pet_type = State()
    breed = State()
    age = State()
    status = State()
    price = State()
    photo = State()
    location = State()
    confirm = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    # Register user via API
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{API_BASE_URL}/auth/register", json={
                "full_name": message.from_user.full_name,
                "email": f"tg_{message.from_user.id}@telegram.bot",
                "password": f"tg_{message.from_user.id}_secure",
                "telegram_id": message.from_user.id
            })
    except:
        pass
    
    await message.answer(
        MESSAGES['welcome'],
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@router.message(Command("help"))
@router.message(F.text == "❓ Yordam")
async def cmd_help(message: Message):
    await message.answer(MESSAGES['help'], parse_mode="Markdown")

@router.message(Command("add"))
@router.message(F.text == "➕ E'lon berish")
async def cmd_add_pet(message: Message, state: FSMContext):
    """Start add pet flow"""
    await state.set_state(AddPetStates.name)
    await message.answer(MESSAGES['add_name'])

@router.message(AddPetStates.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddPetStates.pet_type)
    await message.answer(MESSAGES['add_type'], reply_markup=pet_types())

@router.callback_query(AddPetStates.pet_type, F.data.startswith("type_"))
async def process_type(callback: CallbackQuery, state: FSMContext):
    pet_type = callback.data.replace("type_", "")
    await state.update_data(pet_type=pet_type)
    await state.set_state(AddPetStates.breed)
    await callback.message.edit_text(MESSAGES['add_breed'], reply_markup=skip_button())
    await callback.answer()

@router.message(AddPetStates.breed)
async def process_breed(message: Message, state: FSMContext):
    await state.update_data(breed=message.text)
    await state.set_state(AddPetStates.age)
    await message.answer(MESSAGES['add_age'], reply_markup=skip_button())

@router.callback_query(F.data == "skip")
async def skip_field(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddPetStates.breed:
        await state.update_data(breed="")
        await state.set_state(AddPetStates.age)
        await callback.message.edit_text(MESSAGES['add_age'])
    elif current_state == AddPetStates.age:
        await state.update_data(age="")
        await state.set_state(AddPetStates.status)
        await callback.message.edit_text(MESSAGES['add_status'], reply_markup=pet_status())
    await callback.answer()

@router.message(AddPetStates.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(AddPetStates.status)
    await message.answer(MESSAGES['add_status'], reply_markup=pet_status())

@router.callback_query(AddPetStates.status, F.data.startswith("status_"))
async def process_status(callback: CallbackQuery, state: FSMContext):
    status = callback.data.replace("status_", "")
    await state.update_data(status=status)
    
    if status == "selling":
        await state.set_state(AddPetStates.price)
        await callback.message.edit_text(MESSAGES['add_price'])
    else:
        await state.update_data(price=0)
        await state.set_state(AddPetStates.photo)
        await callback.message.edit_text(MESSAGES['add_photo'])
    await callback.answer()

@router.message(AddPetStates.price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
    except:
        price = 0
    await state.update_data(price=price)
    await state.set_state(AddPetStates.photo)
    await message.answer(MESSAGES['add_photo'])

@router.message(AddPetStates.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_id=photo.file_id)
    await state.set_state(AddPetStates.location)
    await message.answer(MESSAGES['add_location'], reply_markup=locations())

@router.message(AddPetStates.photo)
async def process_photo_skip(message: Message, state: FSMContext):
    await state.update_data(photo_id=None)
    await state.set_state(AddPetStates.location)
    await message.answer(MESSAGES['add_location'], reply_markup=locations())

@router.callback_query(AddPetStates.location, F.data.startswith("loc_"))
async def process_location(callback: CallbackQuery, state: FSMContext):
    location = callback.data.replace("loc_", "")
    await state.update_data(location=location)
    
    data = await state.get_data()
    
    # Show confirmation
    type_names = {'dog': '🐕 It', 'cat': '🐈 Mushuk', 'bird': '🦜 Qush', 'fish': '🐠 Baliq', 'other': '🐰 Boshqa'}
    status_names = {'selling': 'Sotish', 'free': 'Bepul', 'foster': 'Foster', 'adoption': 'Adoptsiya'}
    
    text = f"""📋 *E'lonni tasdiqlang:*

🏷 *Nomi:* {data.get('name')}
🐾 *Turi:* {type_names.get(data.get('pet_type'), data.get('pet_type'))}
📝 *Zoti:* {data.get('breed') or '-'}
📅 *Yoshi:* {data.get('age') or '-'}
📋 *Status:* {status_names.get(data.get('status'))}
💰 *Narxi:* {data.get('price', 0):,} so'm
📍 *Joylashuv:* {data.get('location')}"""
    
    await state.set_state(AddPetStates.confirm)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=confirm_keyboard())
    await callback.answer()

@router.callback_query(AddPetStates.confirm, F.data == "confirm")
async def confirm_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Send to API
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "name": data.get('name'),
                "pet_type": data.get('pet_type'),
                "breed": data.get('breed'),
                "age": data.get('age'),
                "status": data.get('status'),
                "price": data.get('price', 0),
                "location": data.get('location')
            }
            await session.post(f"{API_BASE_URL}/pets/add", json=payload)
    except:
        pass
    
    await state.clear()
    await callback.message.edit_text(MESSAGES['add_success'])
    await callback.answer("✅ E'lon qo'shildi!")

@router.callback_query(F.data == "cancel")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()
