import asyncio
import random
from database.ia_filterdb import get_search_results
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaVideo  # Audio အစား Video ကို ပြောင်းလဲ Import လုပ်ထားသည်


# Message အလိုအလျောက် ပျက်စေမည့် Function
async def delete_msg_after_delay(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")


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

    # Keyword အားလုံးမှ ဗီဒီယိုများကို လိုက်ရှာပြီး List ထဲ စုစည်းပါမည်
    for keyword in search_keywords:
        files, next_offset, total = await get_search_results(chat_id, keyword)

        if files:
            for file in files:
                if file.file_id not in seen_file_ids:
                    seen_file_ids.add(file.file_id)
                    all_found_videos.append(file)

    if all_found_videos:
        # တွေ့ရှိသော ဗီဒီယိုများထဲမှ Random ၁၀ ဖိုင် ရွေးထုတ်ပါမည်
        random.shuffle(all_found_videos)
        selected_videos = all_found_videos[:10]

        # send_media_group အတွက် InputMediaVideo List ပြုလုပ်ခြင်း
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
            # ဗီဒီယို ၁၀ ဖိုင်လုံးကို Album (Video Group) အဖြစ် တစ်ခါတည်း ပို့ပေးမည်
            sent_msgs = await client.send_media_group(
                chat_id=chat_id, media=media_list
            )

            # ပို့လိုက်သော Message တစ်ခုချင်းစီကို ၁ နာရီ (3600 စက္ကန့်) ကြာလျှင် Auto ဖျက်ခိုင်းမည်
            for msg in sent_msgs:
                asyncio.create_task(delete_msg_after_delay(msg, 1 * 3600))

        except FloodWait as e:
            # Rate Limit မိပါက Telegram မှ စောင့်ခိုင်းသည့် စက္ကန့်အတိုင်း ခဏ ရပ်စောင့်မည်
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"Error sending video media group: {e}")

    else:
        await query.message.reply(
            "ဒီအမျိုးအစားထဲမှာ ဗီဒီယို ရှာမတွေ့သေးဘူးဗျာ။ နောက်မှ ပြန်စမ်းကြည့်ပေးပါ။"
        )
