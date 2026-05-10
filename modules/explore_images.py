import logging
import html
import httpx
import io
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from utils.config import CHOOSING_MODE, EXPLORE_IMAGES

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
IMAGES_PER_BATCH = 3
USER_AGENT = "EthiopiaInfoBot/1.0 (contact: admin@gmail.com)"

# Strict MIME types
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

# --- WIKIPEDIA API HELPERS ---

async def search_wiki_page(query: str):
    """Searches for the most relevant Wikipedia page title."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1
    }
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        try:
            response = await client.get(WIKI_API_URL, params=params, timeout=10.0)
            
            if response.status_code == 403:
                logger.error("❌ Wikipedia blocked the request (403 Forbidden).")
                return None
                
            if response.status_code != 200:
                logger.error(f"❌ Wikipedia Error: {response.status_code}")
                return None
                
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            if search_results:
                return search_results[0]["title"]
            return None
        except Exception as e:
            logger.error(f"Error searching Wiki: {e}")
            return None

async def fetch_images_from_page(page_title: str):
    """
    Fetches image URLs associated with a specific Wikipedia page title.
    """
    params = {
        "action": "query",
        "generator": "images",
        "titles": page_title,
        "gimlimit": 50,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "iiurlwidth": 800, 
        "format": "json",
    }
    
    valid_images = []
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        try:
            response = await client.get(WIKI_API_URL, params=params, timeout=10.0)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            for _, page_data in pages.items():
                info = page_data.get("imageinfo", [{}])[0]
                url = info.get("thumburl", info.get("url"))
                mime = info.get("mime")

                if not url or not mime: continue
                if url.startswith("//"): url = "https:" + url
                if mime not in ALLOWED_MIME_TYPES: continue

                # Junk Filter
                url_lower = url.lower()
                is_junk = any(x in url_lower for x in ["c-base", "ambox", "icon", "flag", "logo", "stub", "play", "symbol"])
                
                if not is_junk:
                    valid_images.append(url)
            
            return valid_images

        except Exception as e:
            logger.error(f"Error fetching images: {e}")
            return []

# --- IMAGE DOWNLOADER ---

async def download_image_data(client, url):
    """
    Downloads image bytes. Returns None if download fails.
    """
    try:
        response = await client.get(url, timeout=15.0)
        if response.status_code == 200:
            f = io.BytesIO(response.content)
            f.name = "image.jpg"
            return f
    except:
        pass
    return None

# --- HANDLERS ---

async def handle_explore_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.strip()
    
    if user_query.lower() == "back":
        from modules.tourism_info import get_start_keyboard
        await update.message.reply_text("🏠 Main Menu", reply_markup=get_start_keyboard())
        return CHOOSING_MODE

    await update.message.reply_chat_action(action="upload_photo")

    page_title = await search_wiki_page(user_query)
    if not page_title:
        page_title = await search_wiki_page(f"{user_query} Ethiopia")

    if not page_title:
        await update.message.reply_text(f"❌ Couldn't find images for '{html.escape(user_query)}'.")
        return EXPLORE_IMAGES

    images = await fetch_images_from_page(page_title)

    if not images:
        await update.message.reply_text(f"⚠️ Found article '{page_title}', but valid images were filtered out.")
        return EXPLORE_IMAGES

    context.user_data['search_query'] = page_title
    context.user_data['image_cache'] = images
    context.user_data['current_index'] = 0

    await send_image_batch(update, context)
    return EXPLORE_IMAGES

async def send_image_batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper to send the images safely by uploading them."""
    images = context.user_data.get('image_cache', [])
    current_index = context.user_data.get('current_index', 0)
    query = context.user_data.get('search_query', 'Unknown')

    end_index = current_index + IMAGES_PER_BATCH
    batch_urls = images[current_index:end_index]

    if not batch_urls:
        msg = "🏁 That's all the images I could find."
        if update.callback_query:
            await update.callback_query.answer(msg, show_alert=True)
            try:
                await update.callback_query.message.edit_reply_markup(reply_markup=None)
            except:
                pass
        else:
            await update.message.reply_text(msg)
        return

    context.user_data['current_index'] = end_index

    keyboard = [[InlineKeyboardButton("🔄 Refresh Images", callback_data="refresh_images")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if update.callback_query:
            chat_id = update.callback_query.message.chat_id
        else:
            chat_id = update.effective_chat.id

        caption_text = f"🖼️ Images for **{html.escape(query)}**"

        # DOWNLOAD IMAGES
        media_group = []
        
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
            tasks = [download_image_data(client, url) for url in batch_urls]
            results = await asyncio.gather(*tasks)

            for i, img_data in enumerate(results):
                if img_data:
                    if i == 0:
                        media_group.append(InputMediaPhoto(media=img_data, caption=caption_text, parse_mode="Markdown"))
                    else:
                        media_group.append(InputMediaPhoto(media=img_data))

        if not media_group:
            err_msg = "⚠️ Failed to download images. Try again later."
            if update.callback_query:
                await context.bot.send_message(chat_id=chat_id, text=err_msg)
            else:
                await update.message.reply_text(err_msg)
            return

        if len(media_group) == 1:
            await context.bot.send_photo(
                chat_id=chat_id, 
                photo=media_group[0].media, 
                caption=caption_text, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_media_group(chat_id=chat_id, media=media_group)
            
            # ✅ FIX: Added text here to prevent "Message text is empty" error
            await context.bot.send_message(
                chat_id=chat_id,
                text="👇 **Click below for more images:**", 
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

    except Exception as e:
        logger.error(f"Error sending batch: {e}")
        err_msg = "⚠️ Error displaying images. Please try again."
        if update.callback_query:
            await context.bot.send_message(chat_id=chat_id, text=err_msg)
        else:
            await update.message.reply_text(err_msg)

async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if 'image_cache' not in context.user_data:
        await query.message.reply_text("⚠️ Session expired. Please search again.")
        return

    await send_image_batch(update, context)