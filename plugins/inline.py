import logging
from pyrogram import Client
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedAudio,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database.ia_filterdb import get_search_results
from database.users_chats_db import db
from info import IS_VERIFY, SUPPORT_GROUP # သင့် info.py ထဲမှ Channel Link များ သုံးနိုင်သည်

logger = logging.getLogger(__name__)


@Client.on_inline_query()
async def inline_search_handler(client: Client, query: InlineQuery):
    user_id = query.from_user.id
    string = query.query.strip()
    
    bot = await client.get_me()
    bot_username = bot.username
    
    # 🔗 သင့် Music Channel Link ကို ဒီနေရာမှာ ထည့်ပါ
    channel_link = "https://t.me/musicloverpublic"

    # User စာမရိုက်ရသေးပါက Guide စာသား ပြသပေးခြင်း
    if not string:
        await query.answer(
            results=[],
            switch_pm_text="🎵 သီချင်း/ဗီဒီယို အမည် ရိုက်ရှာပါ...",
            switch_pm_parameter="help",
        )
        return

    # 🔒 Verification / Premium Status စစ်ဆေးခြင်း
    if IS_VERIFY:
        is_premium = await db.has_premium_access(user_id)
        is_verified = await db.is_user_verified(user_id)

        if not (is_premium or is_verified):
            verify_link = f"https://t.me/{bot_username}?start=verify"

            return await query.answer(
                results=[
                    InlineQueryResultArticle(
                        title="🔒 Verification ပြုလုပ်ရန် လိုအပ်ပါသည်",
                        description="Inline Search မသုံးမီ Verification အရင် ကျော်ပေးပါ",
                        input_message_content=InputTextMessageContent(
                            "⚠️ **Inline Search အသုံးပြုရန် Verification ပြုလုပ်ရန် လိုအပ်ပါသည်!**\n\n"
                            "သီချင်း/ဗီဒီယိုများ ရှာဖွေနိုင်ရန် အောက်ပါ Link ကို နှိပ်ပြီး Verification ကျော်လွန်ပေးပါ။"
                        ),
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔓 Verify / Unlock Search", url=verify_link)]
                        ])
                    )
                ],
                cache_time=1,
                switch_pm_text="🔒 Verification ကျော်ရန် အောက်ပါ Link ကိုနှိပ်ပါ",
                switch_pm_parameter="verify"
            )

    # 🔍 Verification အဆင်ပြေပါက ရလဒ်များ ရှာဖွေပြသခြင်း
    try:
        files, next_offset, total = await get_search_results(
            chat_id=None, query=string, max_results=10
        )

        results = []
        for file in files:
            file_id = file.file_id
            file_name = file.file_name or "Media File"
            file_type = getattr(file, "file_type", None)

            # 🔘 ခလုတ် (၄) ခုပါသော Keyboard ပြင်ဆင်ခြင်း
            save_button = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "❤️ Save", 
                        callback_data=f"add_fav_{file_id}"
                    ),
                    InlineKeyboardButton(
                        "🎧 My Playlist", 
                        callback_data="my_playlist"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🤖 Bot သို့သွားရန်", 
                        url=f"https://t.me/{bot_username}?start=true"
                    ),
                    InlineKeyboardButton(
                        "🎵 Music Channel", 
                        url=channel_link
                    )
                ]
            ])

            caption_text = file.caption or file_name

            # 📹 Video
            if file_type == "video" or file_name.lower().endswith(('.mp4', '.mkv', '.webm', '.avi', '.mov')):
                results.append(
                    InlineQueryResultCachedVideo(
                        video_file_id=file_id,
                        title=file_name,
                        description=f"Size: {file.file_size}",
                        caption=caption_text,
                        reply_markup=save_button
                    )
                )

            # 🎵 Audio
            elif file_type == "audio" or file_name.lower().endswith(('.mp3', '.m4a', '.flac', '.wav', '.aac')):
                results.append(
                    InlineQueryResultCachedAudio(
                        audio_file_id=file_id,
                        caption=caption_text,
                        reply_markup=save_button
                    )
                )

            # 📁 Document
            else:
                results.append(
                    InlineQueryResultCachedDocument(
                        title=file_name,
                        document_file_id=file_id,
                        description=f"Size: {file.file_size}",
                        caption=caption_text,
                        reply_markup=save_button
                    )
                )

        await query.answer(
            results=results,
            cache_time=1,
            switch_pm_text=f"🔍 ရှာတွေ့သော ရလဒ် - {total} ခု",
            switch_pm_parameter="search",
        )

    except Exception as e:
        logger.error(f"Inline Search Error: {e}")
        await query.answer(
            results=[],
            switch_pm_text="❌ ရှာဖွေစဉ် အမှားအယွင်း ဖြစ်ပေါ်ခဲ့သည်",
            switch_pm_parameter="error",
        )
