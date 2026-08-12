import logging
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

# db Object ကိုသာ Import ပြုလုပ်ခြင်း
from database.users_chats_db import db
from database.ia_filterdb import get_file_details

logger = logging.getLogger(__name__)


# ၁။ ❤️ Save Button နှိပ်သည့်အခါ
@Client.on_callback_query(filters.regex(r"^add_fav_(.+)"))
async def add_fav_handler(client: Client, query: CallbackQuery):
    try:
        file_id = query.data.split("_", 2)[2]
        user_id = query.from_user.id

        # db.add_to_playlist ဖြင့် ခေါ်သုံးခြင်း
        await db.add_to_playlist(user_id, file_id)
        await query.answer(
            "❤️ သီချင်းကို သင်၏ Playlist ထဲသို့ သိမ်းဆည်းလိုက်ပါပြီ!",
            show_alert=True,
        )
    except Exception as e:
        logger.error(f"Error in add_fav: {e}")
        await query.answer(
            "❌ သိမ်းဆည်းစဉ် အမှားအယွင်း ဖြစ်ပေါ်ခဲ့သည်!", show_alert=True
        )


# ၂။ 🗑️ Playlist မှ ပြန်ဖျက်သည့်အခါ
@Client.on_callback_query(filters.regex(r"^rem_fav_(.+)"))
async def rem_fav_handler(client: Client, query: CallbackQuery):
    try:
        file_id = query.data.split("_", 2)[2]
        user_id = query.from_user.id

        # db.remove_from_playlist ဖြင့် ခေါ်သုံးခြင်း
        await db.remove_from_playlist(user_id, file_id)
        await query.answer(
            "🗑️ သီချင်းကို Playlist ထဲမှ ဖျက်လိုက်ပါပြီ!", show_alert=True
        )
        await view_playlist(client, query)
    except Exception as e:
        logger.error(f"Error in rem_fav: {e}")
        await query.answer(
            "❌ ဖျက်ရာတွင် အမှားအယွင်း ဖြစ်ပေါ်ခဲ့သည်!", show_alert=True
        )


# ၃။ 🎧 My Playlist စာရင်း ပြသခြင်း
@Client.on_callback_query(filters.regex("^my_playlist$"))
async def view_playlist(client: Client, query: CallbackQuery):
    try:
        user_id = query.from_user.id

        # db.get_playlist ဖြင့် ခေါ်သုံးခြင်း
        fav_ids = await db.get_playlist(user_id)

        if not fav_ids:
            return await query.answer(
                "❌ သင့် Playlist ထဲတွင် သီချင်းများ မရှိသေးပါ။",
                show_alert=True,
            )

        buttons = []
        for f_id in fav_ids[:15]:
            files_res = await get_file_details(f_id)
            if files_res:
                file = files_res[0]
                file_name = getattr(file, "file_name", "Unknown Song")
                buttons.append(
                    [
                        InlineKeyboardButton(
                            f"🎵 {file_name}", callback_data=f"file_{f_id}"
                        ),
                        InlineKeyboardButton(
                            "🗑️", callback_data=f"rem_fav_{f_id}"
                        ),
                    ]
                )

        if not buttons:
            return await query.answer(
                "❌ Playlist ထဲရှိ သီချင်းများ ရှာမတွေ့တော့ပါ။",
                show_alert=True,
            )

        markup = InlineKeyboardMarkup(buttons)
        text = "🎧 **သင့်စိတ်ကြိုက် Playlist သီချင်းများ:**\n\n(သီချင်းနားထောင်ရန် နှိပ်ပါ သို့မဟုတ် 🗑️ ဖြင့် ပြန်ဖျက်ပါ)"

        try:
            await query.message.edit_text(text, reply_markup=markup)
        except Exception:
            await query.message.reply_text(text, reply_markup=markup)

    except Exception as e:
        logger.error(f"Error in view_playlist: {e}")
        await query.answer(
            "❌ အချက်အလက် ခေါ်ယူရာတွင် အမှားအယွင်း ဖြစ်ပေါ်ခဲ့သည်!",
            show_alert=True,
        )


# ၄။ 🎵 Playlist ထဲမှ သီချင်း/ဗီဒီယို နှိပ်သည့်အခါ ဖိုင်ပြန်ပို့ပေးခြင်း
@Client.on_callback_query(filters.regex(r"^file_(.+)"))
async def send_playlist_file(client: Client, query: CallbackQuery):
    try:
        file_id = query.data.split("_", 1)[1]
        files_res = await get_file_details(file_id)

        if not files_res:
            return await query.answer(
                "❌ ဖိုင် အချက်အလက် ရှာမတွေ့ပါ!", show_alert=True
            )

        file = files_res[0]
        caption = getattr(file, "caption", "") or getattr(file, "file_name", "")

        # send_cached_media ကို သုံးခြင်းဖြင့် Video / Audio / Document မူရင်းအတိုင်း ပို့ပေးမည် ဖြစ်သည်
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=caption,
        )
        await query.answer("▶️ ဖိုင် ပို့ပေးလိုက်ပါပြီ!")

    except Exception as e:
        logger.error(f"Error in send_playlist_file: {e}")
        await query.answer(
            "❌ ဖိုင် ပို့ပေးရာတွင် အမှားအယွင်း ဖြစ်ပေါ်ခဲ့သည်!",
            show_alert=True,
        )
