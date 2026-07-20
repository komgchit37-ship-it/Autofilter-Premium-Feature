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
    
    search_keywords = keywords.get(cat, [])
    
    if not search_keywords:
        await query.answer("ဒီ category မှာ keywords မသတ်မှတ်ရသေးပါဘူး။")
        return

    await query.answer("သီချင်း ရှာနေတယ်ဗျာ... ⏳", show_alert=False)
    
    # Keyword တွေကို အရင် Random ရှuffling လုပ်လိုက်မယ် (အမြဲတမ်း ပထမဆုံး Keyword ပဲ မရှာအောင်လို့)
    random.shuffle(search_keywords)
    
    found_song = None
    
    # Keyword တစ်ခုချင်းစီကို Loop ပတ်ပြီး ရှာပါမယ်
    for keyword in search_keywords:
        files, total = await get_bad_files(keyword)
        
        # သီချင်းတွေ့ပြီဆိုရင် Loop ကို ရပ်လိုက်ပါမယ်
        if files and len(files) > 0:
            found_song = random.choice(files)
            break 
    
    if found_song:
        # သီချင်းကို User ဆီ ပို့ပေးခြင်း
        await client.send_cached_media(
            chat_id=query.message.chat.id,
            file_id=found_song.file_id,
            caption=f"🎵 သင့်အတွက် ရွေးချယ်ပေးထားသော သီချင်း:\n\n**{found_song.file_name}**"
        )
    else:
        # အကုန်လုံးရှာပြီးတာတောင် မတွေ့မှ ဒီစာကို ပြပါမယ်
        await query.message.reply("ဒီအမျိုးအစားထဲမှာ သီချင်း ရှာမတွေ့သေးဘူးဗျာ။ နောက်မှ ပြန်စမ်းကြည့်ပေးပါ။")
