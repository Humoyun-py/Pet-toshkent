from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    """Main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🐕 Hayvonlar"), KeyboardButton(text="➕ E'lon berish")],
            [KeyboardButton(text="🏥 Klinikalar"), KeyboardButton(text="❤️ Xayriya")],
            [KeyboardButton(text="📋 Mening e'lonlarim"), KeyboardButton(text="❓ Yordam")]
        ],
        resize_keyboard=True
    )
    return keyboard

def pet_types():
    """Pet type selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐕 It", callback_data="type_dog"),
         InlineKeyboardButton(text="🐈 Mushuk", callback_data="type_cat")],
        [InlineKeyboardButton(text="🦜 Qush", callback_data="type_bird"),
         InlineKeyboardButton(text="🐠 Baliq", callback_data="type_fish")],
        [InlineKeyboardButton(text="🐰 Boshqa", callback_data="type_other")]
    ])
    return keyboard

def pet_status():
    """Pet status selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Sotish", callback_data="status_selling"),
         InlineKeyboardButton(text="🎁 Bepul berish", callback_data="status_free")],
        [InlineKeyboardButton(text="🏠 Foster", callback_data="status_foster"),
         InlineKeyboardButton(text="❤️ Adoptsiya", callback_data="status_adoption")]
    ])
    return keyboard

def locations():
    """Location selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yunusobod", callback_data="loc_Yunusobod"),
         InlineKeyboardButton(text="Chilonzor", callback_data="loc_Chilonzor")],
        [InlineKeyboardButton(text="Sergeli", callback_data="loc_Sergeli"),
         InlineKeyboardButton(text="Mirobod", callback_data="loc_Mirobod")],
        [InlineKeyboardButton(text="Shayxontohur", callback_data="loc_Shayxontohur"),
         InlineKeyboardButton(text="Olmazor", callback_data="loc_Olmazor")]
    ])
    return keyboard

def pets_navigation(current_page, total_pages, pet_id=None):
    """Navigation for pets list"""
    buttons = []
    
    row = []
    if current_page > 1:
        row.append(InlineKeyboardButton(text="⬅️", callback_data=f"page_{current_page-1}"))
    row.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop"))
    if current_page < total_pages:
        row.append(InlineKeyboardButton(text="➡️", callback_data=f"page_{current_page+1}"))
    buttons.append(row)
    
    if pet_id:
        buttons.append([InlineKeyboardButton(text="📱 Bog'lanish", callback_data=f"contact_{pet_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def skip_button():
    """Skip button for optional fields"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data="skip")]
    ])

def confirm_keyboard():
    """Confirmation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def donation_amounts():
    """Donation amount selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50,000 so'm", callback_data="donate_50000"),
         InlineKeyboardButton(text="100,000 so'm", callback_data="donate_100000")],
        [InlineKeyboardButton(text="200,000 so'm", callback_data="donate_200000"),
         InlineKeyboardButton(text="500,000 so'm", callback_data="donate_500000")],
        [InlineKeyboardButton(text="💳 Boshqa miqdor", callback_data="donate_custom")]
    ])
    return keyboard

def admin_menu():
    """Admin menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="⏳ Kutilayotgan e'lonlar", callback_data="admin_pending")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")]
    ])
    return keyboard

def approve_reject(pet_id):
    """Approve/reject buttons for admin"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{pet_id}"),
         InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{pet_id}")]
    ])
