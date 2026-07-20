import random
from pyrogram import Client, filters
from database.ia_filterdb import get_bad_files

@Client.on_callback_query(filters.regex(r"^rnd_"))
async def random_song_callback(client, query):
    # Button ကို နှိပ်လိုက်တဲ့အခါ rnd_ ဆိုတာပါတဲ့ data ကို ဖမ်းယူခြင်း
    cat = query.data.split("_")[1]
    
    # အမျိုးအစားအလိုက် ရှာဖွေရမည့် Keywords များ
    keywords = {
        "sad": ["အသဲကွဲ", "လွမ်း", "မျက်ရည်"],
        "love": ["အချစ်", "ချစ်သူ", "ရင်ခုန်"],
        "parent": ["မိဘ", "အမေ", "အဖေ"],
        "child": ["ကလေး", "သား", "သမီး"],
        "thingyan": ["သင်္ကြန်", "ရေကစား"],
        "modern": ["Rap", "Hip Hop", "Pop"]
    }
    
    # ရွေးလိုက်တဲ့ category ထဲက keywords တွေကို ခေါ်ယူခြင်း
    search_keywords = keywords.get(cat, [])
    
    if not search_keywords:
        await query.answer("ဒီ category မှာ keywords မသတ်မှတ်ရသေးပါဘူး။")
        return

    # User ကို စောင့်ခိုင်းတဲ့စာ ပြခြင်း
    await query.answer("သီချင်း Random ရှာနေတယ်ဗျာ... ⏳", show_alert=False)
    
    # keywords ထဲက တစ်ခုခုကို random ရွေးပြီး Database ထဲမှာ ရှာခိုင်းခြင်း
    search_query = random.choice(search_keywords)
    
    # get_bad_files function ကိုသုံးပြီး သီချင်းတွေ ရှာခြင်း
    files, total = await get_bad_files(search_query) 
    
    if files and len(files) > 0:
        # ရှာလို့ရလာတဲ့ သီချင်းတွေထဲက တစ်ပုဒ်ကို random ရွေးခြင်း
        chosen_song = random.choice(files)
        
        # သီချင်းကို User ဆီ ပို့ပေးခြင်း
        await client.send_cached_media(
            chat_id=query.message.chat.id,
            file_id=chosen_song.file_id,
            caption=f"🎵 သင့်အတွက် ရွေးချယ်ပေးထားသော သီချင်း:\n\n**{chosen_song.file_name}**"
        )
    else:
        # ရှာမတွေ့ရင် ပြမယ့်စာ
        await query.message.reply("ဒီအမျိုးအစားထဲမှာ သီချင်း ရှာမတွေ့သေးဘူးဗျာ။ နောက်မှ ပြန်စမ်းကြည့်ပေးပါ။")
