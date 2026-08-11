import asyncio
import random
from database.ia_filterdb import get_search_results
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    ForceReply,
    InputMediaVideo,
)  # ForceReply နှင့် InputMediaVideo အားလုံး ပါဝင်သည်


# Message အလိုအလျောက် ပျက်စေမည့် Helper Function
async def delete_msg_after_delay(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")


# =========================================================
# ၁။ Random ဗီဒီယို ၁၀ ဖိုင် ပို့ပေးသည့် Callback Handler
# =========================================================
@Client.on_callback_query(filters.regex(r"^rnd_"))
async def random_video_callback(client, query):
    cat = query.data.split("_")[1]

    keywords = {
        "sad": ["အသဲကွဲ", "လွမ်း", "မျက်ရည်"],
        "love": ["အချစ်", "ချစ်သူ", "ရင်ခုန်"],
        "parent": ["မိဘ", "အမေ", "အဖေ"],
        "child": ["child"],
        "thingyan": ["သင်္ကြန်", "ရေကစား"],
        "other": ["other"],
        "ahlu": ["ahlu"],
        "web": ["wedd"],
        "old": ["old"],
        "modern": ["Rap", "Hip Hop", "Pop"],
    }

    search_keywords = keywords.get(cat, [])

    if not search_keywords:
        await query.answer("ဒီ category မှာ keywords မသတ်မှတ်ရသေးပါဘူး။")
        return

    await query.answer(
        "ဗီဒီယို ၁၀ ဖိုင် random ရှာနေတယ်ဗျာ... ⏳", show_alert=False
    )
    random.shuffle(search_keywords)

    chat_id = query.message.chat.id
    all_found_videos = []
    seen_file_ids = set()

    for keyword in search_keywords:
        files, next_offset, total = await get_search_results(chat_id, keyword)

        if files:
            for file in files:
                if file.file_id not in seen_file_ids:
                    seen_file_ids.add(file.file_id)
                    all_found_videos.append(file)

    if all_found_videos:
        random.shuffle(all_found_videos)
        selected_videos = all_found_videos[:10]

        media_list = []
        for video in selected_videos:
            caption = (
                "🎬 သင့်အတွက် random ရွေးချယ်ပေးထားသော ဗီဒီယို ၁နာရီနေ auto ပျက်ပါမယ် "
                "Saved messages မှာ forward လုပ်သိမ်းထားနိုင်ပါတယ်:\n\n"
                f"**{video.file_name}**"
            )
            media_list.append(
                InputMediaVideo(media=video.file_id, caption=caption)
            )

        try:
            sent_msgs = await client.send_media_group(
                chat_id=chat_id, media=media_list
            )

            for msg in sent_msgs:
                asyncio.create_task(delete_msg_after_delay(msg, 1 * 3600))

        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"Error sending video media group: {e}")

    else:
        await query.message.reply(
            "ဒီအမျိုးအစားထဲမှာ ဗီဒီယို ရှာမတွေ့သေးဘူးဗျာ။ နောက်မှ ပြန်စမ်းကြည့်ပေးပါ။"
        )


# =========================================================
# ၂။ အဆိုတော် နာမည် ရိုက်ရှာရန် စာတောင်းသည့် Callback Handler
# =========================================================
@Client.on_callback_query(filters.regex("^search_artist$"))
async def search_artist_callback(client, query):
    await query.message.reply_text(
        "🎤 **သင်ရှာလိုသော အဆိုတော် နာမည်ကို ဒီစာကို Reply ပြန်၍ ရိုက်ထည့်ပေးပါခင်ဗျာ -**",
        reply_markup=ForceReply(True),
    )
    await query.answer()
