import logging
from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultCachedDocument
from database.ia_filterdb import get_search_results

logger = logging.getLogger(__name__)


@Client.on_inline_query()
async def inline_search_handler(client: Client, query: InlineQuery):
    string = query.query.strip()

    # User စာမရိုက်ရသေးပါက Guide စာသား ပြသပေးခြင်း
    if not string:
        await query.answer(
            results=[],
            switch_pm_text="🎵 သီချင်းအမည် ရိုက်ရှာပါ...",
            switch_pm_parameter="help",
        )
        return

    try:
        # ကျွန်ုပ်တို့ ပြင်ထားသည့် Atlas Fuzzy Search DB ကို ခေါ်ယူခြင်း
        files, next_offset, total = await get_search_results(
            chat_id=None, query=string, max_results=10
        )

        results = []
        for file in files:
            file_id = file.file_id
            file_name = file.file_name

            # Telegram ရလဒ် ပြသရန် ရွေးချယ်ခြင်း
            results.append(
                InlineQueryResultCachedDocument(
                    title=file_name,
                    document_file_id=file_id,
                    description=f"Size: {file.file_size}",
                    caption=file.caption or file_name,
                )
            )

        # ရှာတွေ့သည့် ရလဒ်များ Telegram ပေါ်သို့ တင်ပြခြင်း
        await query.answer(
            results=results,
            cache_time=1,
            switch_pm_text=f"🔍 ရှာတွေ့သော သီချင်းရလဒ် - {total} ခု",
            switch_pm_parameter="search",
        )

    except Exception as e:
        logger.error(f"Inline Search Error: {e}")
        await query.answer(
            results=[],
            switch_pm_text="❌ ရှာဖွေစဉ် အမှားအယွင်း ဖြစ်ပေါ်ခဲ့သည်",
            switch_pm_parameter="error",
        )
