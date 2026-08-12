import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.users_chats_db import add_to_playlist, remove_from_playlist, get_playlist
from database.ia_filterdb import get_file_details

logger = logging.getLogger(__name__)


# ၁။ ❤️ Save Button နှိပ်သည့်အခါ အလုပ်လုပ်မည့် Handler
@Client.on_callback_query(filters.regex(r"^add_fav_(.+)"))
async def add_fav_handler(client: Client, query: CallbackQuery):
    file_id = query.data.split("_")[2]
    user_id = query.from_user.id
    
    await add_to_playlist(user_id, file_id)
    await query.answer("❤️ သီချင်းကို သင်၏ Playlist ထဲသို့ သိမ်းဆည်းလိုက်ပါပြီ!", show_alert=True)


# ၂။ 🗑️ Playlist မှ ပြန်ဖျက်သည့် Handler
@Client.on_callback_query(filters.regex(r"^rem_fav_(.+)"))
async def rem_fav_handler(client: Client, query: CallbackQuery):
    file_id = query.data.split("_")[2]
    user_id = query.from_user.id
    
    await remove_from_playlist(user_id, file_id)
    await query.answer("🗑️ သီချင်းကို Playlist ထဲမှ ဖျက်လိုက်ပါပြီ!", show_alert=True)
    # စာရင်းကို အလိုအလျောက် ပြန်လည် Refresh လုပ်ပေးခြင်း
    await view_playlist(client, query)


# ၃။ 🎧 My Playlist Button နှိပ်သည့်အခါ စာရင်းပြပေးမည့် Handler
@Client.on_callback_query(filters.regex("^my_playlist$"))
async def view_playlist(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    fav_ids = await get_playlist(user_id)
    
    if not fav_ids:
        return await query.answer("❌ သင့် Playlist ထဲတွင် သီချင်းများ မရှိသေးပါ။", show_alert=True)
    
    buttons = []
    # နောက်ဆုံး သိမ်းဆည်းထားသော သီချင်း ၁၅ ပုဒ် ပြသပေးမည်
    for f_id in fav_ids[:15]:
        files_res = await get_file_details(f_id)
        if files_res:
            file = files_res[0]
            file_name = getattr(file, "file_name", "Unknown Song")
            buttons.append([
                InlineKeyboardButton(f"🎵 {file_name}", callback_data=f"file_{f_id}"),
                InlineKeyboardButton("🗑️", callback_data=f"rem_fav_{f_id}")
            ])
            
    markup = InlineKeyboardMarkup(buttons)
    text = "🎧 **သင့်စိတ်ကြိုက် Playlist သီချင်းများ:**\n\n(သီချင်းနားထောင်ရန် နှိပ်ပါ သို့မဟုတ် 🗑️ ဖြင့် ပြန်ဖျက်ပါ)"
    
    try:
        await query.message.edit_text(text, reply_markup=markup)
    except Exception:
        await query.message.reply_text(text, reply_markup=markup)
