import random
from pyrogram import Client, filters
# ဒီနေရာမှာ get_bad_files နေရာတွင် get_search_results ဟု ပြောင်းလိုက်ပါ
from database.ia_filterdb import get_search_results 

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

    await query.answer("သီချင်း ရှာနေတယ်ဗျာ... ⏳", show_alert=False)
    random.shuffle(search_keywords)
    
    found_song = None
    
    # Keyword တစ်ခုချင်းစီကို Loop ပတ်ပြီး ရှာပါမယ်
    for keyword in search_keywords:
        print(f"DEBUG: အခု ' {keyword} ' နဲ့ ရှာနေပါတယ်...")
        # ဒီနေရာမှာ get_search_results ကို ခေါ်သုံးပါမယ်
        files, total = await get_search_results(keyword) 
        
        if files and len(files) > 0:
            print(f"DEBUG: ' {keyword} ' နဲ့ တွေ့ပါပြီ!")
            found_song = random.choice(files)
            break 
        else:
            print(f"DEBUG: ' {keyword} ' နဲ့ ရှာမတွေ့ပါဘူး။ နောက်တစ်ခု ထပ်ရှာမယ်။")
    
    if found_song:
        await client.send_cached_media(
            chat_id=query.message.chat.id,
            file_id=found_song.file_id,
            caption=f"🎵 သင့်အတွက် ရွေးချယ်ပေးထားသော သီချင်း:\n\n**{found_song.file_name}**"
        )
    else:
        await query.message.reply("ဒီအမျိုးအစားထဲမှာ သီချင်း ရှာမတွေ့သေးဘူးဗျာ။ နောက်မှ ပြန်စမ်းကြည့်ပေးပါ။")
