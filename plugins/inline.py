import logging
from pyrogram import Client
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedAudio,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database.ia_filterdb import get_search_results

logger = logging.getLogger(__name__)


@Client.on_inline_query()
async def inline_search_handler(client: Client, query: InlineQuery):
    string = query.query.strip()

    # User စာမရိုက်ရသေးပါက Guide စာသား ပြသပေးခြင်း
    if not string:
        await query.answer(
            results=[],
            switch_pm_text="🎵 သီချင်း/ဗီဒီယို အမည် ရိုက်ရှာပါ...",
            switch_pm_parameter="help",
        )
        return

    try:
        # Atlas Fuzzy Search DB မှ ခေါ်ယူခြင်း
        files, next_offset, total = await get_search_results(
            chat_id=None, query=string, max_results=10
        )

        results = []
        for file in files:
            file_id = file.file_id
            file_name = file.file_name or "Media File"
            file_type = getattr(file, "file_type", None)

            # ❤️ Save to Playlist နှင့် My Playlist Button များ
            save_button = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "❤️ Save", 
                        callback_data=f"add_fav_{file_id}"
                    ),
                    InlineKeyboardButton(
                        "🎧 My Playlist", 
                        callback_data="my_playlist" # သင့် bot တွင် သတ်မှတ်ထားသော callback_data ကို သုံးပါ
                    )
                ]
            ])

            caption_text = file.caption or file_name

            # 📹 Video ဖိုင်များအတွက်
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

            # 🎵 Audio/Music ဖိုင်များအတွက်
            elif file_type == "audio" or file_name.lower().endswith(('.mp3', '.m4a', '.flac', '.wav', '.aac')):
                results.append(
                    InlineQueryResultCachedAudio(
                        audio_file_id=file_id,
                        caption=caption_text,
                        reply_markup=save_button
                    )
                )

            # 📁 အခြား Document/Zip/PDF ဖိုင်များအတွက်
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

        # ရှာတွေ့သည့် ရလဒ်များ Telegram ပေါ်သို့ တင်ပြခြင်း
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
