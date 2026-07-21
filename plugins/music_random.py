import random
import asyncio # အသစ်ထည့်ရမည့် အပိုင်း
from pyrogram import Client, filters
from database.ia_filterdb import get_search_results 

# Message အလိုအလျောက် ပျက်စေမည့် Function
async def delete_msg_after_delay(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

@Client.on_callback_query(filters.regex(r"^rnd_"))
async def random_song_callback(client, query):
    cat = query.data.split("_")[1]
    
    keywords = {
        "sad": ["အသဲကွဲ", "လွမ်း", "မျက်ရည်"],
        "love": ["အချစ်", "ချစ်သူ", "ရင်ခုန်"],
        "parent": ["မိဘ", "အမေ", "အဖေ"],
        "child": ["ကလေး", "သား", "သမီး"],
        "thingyan": ["သင်္ကြန်", "ရေကစား"],
        "modern": ["Rap", "Hip Hop", "Pop"]
    }
    
    search_keywords = keywords.get(cat, [])
    
    if not search_keywords:
        await query.answer("ဒီ category မှာ keywords မသတ်မှတ်ရသေးပါဘူး။")
        return

    await query.answer("သီချင်း ၁ပုဒ် random ရှာနေတယ်ဗျာ... ⏳", show_alert=False)
    random.shuffle(search_keywords)
    
    found_song = None
    chat_id = query.message.chat.id
    
    for keyword in search_keywords:
        files, next_offset, total = await get_search_results(chat_id, keyword) 
        
        if files and len(files) > 0:
            found_song = random.choice(files)
            break 
    
    if found_song:
        # သီချင်းကို ပို့ပြီး ပို့လိုက်တဲ့ message ကို သိမ်းထားပါမယ်
        sent_msg = await client.send_cached_media(
            chat_id=chat_id,
            file_id=found_song.file_id,
            caption=f"🎵 သင့်အတွက် random ရွေးချယ်ပေးထားသော သီချင်း ၆၀မိနစ်နေ auto ပျက်ပါမယ် save message မှာ forward လုပ်သိမ်းထားနိုင်ပါတယ်:\n\n**{found_song.file_name}**"
        )
        
        # ၆ နာရီ = 6 * 3600 seconds
        # ၆ နာရီကြာရင် message ကို delete လုပ်ဖို့ task တစ်ခု ဖန်တီးလိုက်တာပါ
        asyncio.create_task(delete_msg_after_delay(sent_msg, 1 * 3600))
        
    else:
        await query.message.reply("ဒီအမျိုးအစားထဲမှာ သီချင်း ရှာမတွေ့သေးဘူးဗျာ။ နောက်မှ ပြန်စမ်းကြည့်ပေးပါ။")
