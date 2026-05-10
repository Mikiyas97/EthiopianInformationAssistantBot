from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ContextTypes
from data import data
from utils.config import SELECT_SITE, ORIGINAL_MENU, TOURISM_INFO, TICKET_INFO, CHOOSING_MODE, EXPLORE_IMAGES

# Import Helper Modules
from modules.weather import get_weather_report
from modules.mapping import get_coordinates
# Import Wiki Logic
from modules.explore_images import search_wiki_page, fetch_images_from_page, send_image_batch
# Import the function used for the cover photo (to preserve that feature)
from modules.images import get_wikipedia_image 

# --- KEYBOARDS ---

def get_start_keyboard():
    return ReplyKeyboardMarkup([
        ["🏛️ Original Guide", "🤖 AI Chatbot"]
    ], resize_keyboard=True)

def get_original_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["🌍 Tourism Info", "⛅️ Weather Updates"],
        ["🏨 Nearby Hotels", "🎟️ Ticket Prices"],
        # Side by side: Map and Image Gallery
        ["📍 Location Map", "🖼️ Explore Site Images"], 
        ["🔙 Change Site", "🏠 Home"]
    ], resize_keyboard=True)

def get_tourism_keyboard():
    return ReplyKeyboardMarkup([["📜 Background History", "🏺 Cultural Note"], ["🔙 Back to Menu"]], resize_keyboard=True)

def get_ticket_keyboard():
    return ReplyKeyboardMarkup([["💰 Price", "⏰ Opening Hours"], ["🔙 Back to Menu"]], resize_keyboard=True)

# --- HANDLERS ---

async def handle_site_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    clean_input = user_input.lower().replace(" ", "")

    # Save destination for later use (Maps & Images)
    context.user_data['current_site'] = clean_input
    context.user_data['destination_name'] = user_input 

    # 1. Try to find in hardcoded data (for text details)
    site_data = data.get(clean_input, {})
    site_name = site_data.get('name', user_input.title())

    # --- PRESERVED FEATURE: FETCH COVER IMAGE DYNAMICALLY ---
    # This is the part you asked not to touch/break. 
    # It searches for ONE image immediately when the user types the name.
    
    await update.message.reply_text(f"🔍 Found: **{site_name}**", parse_mode="Markdown")
    
    # Try API first using your existing logic
    img_url, caption = get_wikipedia_image(site_name)
    
    # Fallback to hardcoded data if API fails
    if not img_url:
        img_url = site_data.get('image_url')
        caption = f"📍 **{site_name}**"

    # Send Image
    if img_url:
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=img_url,
                caption=caption,
                reply_markup=get_original_menu_keyboard(),
                parse_mode="Markdown"
            )
        except:
            # Fallback if URL is bad
            await update.message.reply_text(f"✅ Selected: {site_name}", reply_markup=get_original_menu_keyboard())
    else:
        await update.message.reply_text(f"✅ Selected: {site_name} (No image found)", reply_markup=get_original_menu_keyboard())

    return ORIGINAL_MENU

async def handle_original_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    
    # Retrieve stored data
    site_key = context.user_data.get('current_site')
    site_data = data.get(site_key, {})
    
    # Get the original name the user typed (e.g. "Lalibela")
    destination_name = context.user_data.get('destination_name', 'Ethiopia')
    site_display_name = site_data.get('name', destination_name)

    if choice == "🌍 Tourism Info":
        await update.message.reply_text("🌍 Choose a category:", reply_markup=get_tourism_keyboard())
        return TOURISM_INFO
    
    elif choice == "🎟️ Ticket Prices":
        await update.message.reply_text("🎟️ Choose an option:", reply_markup=get_ticket_keyboard())
        return TICKET_INFO

    elif choice == "⛅️ Weather Updates":
        status_msg = await update.message.reply_text(f"🔍 Fetching weather for {site_display_name}...")
        report = get_weather_report(site_display_name, site_data.get('safety_guideline', 'N/A'))
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        await update.message.reply_text(report, reply_markup=get_original_menu_keyboard(), parse_mode="Markdown")
        return ORIGINAL_MENU

    elif choice == "🏨 Nearby Hotels":
        raw_hotels = site_data.get('nearby_hotels', [])
        msg = "🏨 **Nearby Hotels:**\n\n"
        hotel_list = list(raw_hotels.values()) if isinstance(raw_hotels, dict) else raw_hotels
        if not hotel_list: msg += "ℹ️ No info available."
        else:
            for item in hotel_list:
                if isinstance(item, (list, tuple)) and len(item) >= 2: msg += f"• **{item[0]}**\n   💰 {item[1]}\n"
        await update.message.reply_text(msg, reply_markup=get_original_menu_keyboard(), parse_mode="Markdown")
        return ORIGINAL_MENU

    # --- FEATURE: MAP & DIRECTIONS ---
    elif choice == "📍 Location Map":
        await update.message.reply_text("🛰️ Fetching coordinates...")
        lat, lon = get_coordinates(site_display_name)
        
        if not lat:
            coords = site_data.get('location', {})
            lat = coords.get('lat')
            lon = coords.get('lon')

        if lat and lon:
            context.user_data['dest_coords'] = {'lat': lat, 'lon': lon}
            await context.bot.send_location(chat_id=update.effective_chat.id, latitude=lat, longitude=lon)
            
            loc_btn = KeyboardButton("🚗 Get Directions (Share Location)", request_location=True)
            cancel_btn = KeyboardButton("🔙 Cancel Directions")
            kb = ReplyKeyboardMarkup([[loc_btn], [cancel_btn]], resize_keyboard=True, one_time_keyboard=True)
            
            await update.message.reply_text(
                "🗺️ To get driving directions, click the button below:", 
                reply_markup=kb
            )
        else:
            await update.message.reply_text("⚠️ Coordinates not found.", reply_markup=get_original_menu_keyboard())
        return ORIGINAL_MENU

    # --- FEATURE: EXPLORE SITE IMAGES (FIXED) ---
    elif choice == "🖼️ Explore Site Images":
        await update.message.reply_chat_action(action="upload_photo")
        
        # FIX: Append "Ethiopia" to the search to make sure we find the right page
        # e.g. "Simien" -> "Simien Mountains National Park"
        search_query = f"{destination_name} Ethiopia"
        
        # 1. Search Wiki
        page_title = await search_wiki_page(search_query)
        
        if not page_title:
            # Try without "Ethiopia" if strict search failed
            page_title = await search_wiki_page(destination_name)

        if not page_title:
            await update.message.reply_text(f"❌ No gallery found for '{destination_name}'.", reply_markup=get_original_menu_keyboard())
            return ORIGINAL_MENU

        # 2. Fetch Images
        images = await fetch_images_from_page(page_title)

        if not images:
            await update.message.reply_text(f"⚠️ Found article '{page_title}', but it has no images.", reply_markup=get_original_menu_keyboard())
            return ORIGINAL_MENU

        # 3. Store State for Pagination
        context.user_data['search_query'] = page_title
        context.user_data['image_cache'] = images
        context.user_data['current_index'] = 0

        # 4. Send Batch
        await send_image_batch(update, context)
        return ORIGINAL_MENU

    elif choice == "🔙 Change Site":
        await update.message.reply_text("Type the name of the new place:", reply_markup=ReplyKeyboardRemove())
        return SELECT_SITE

    elif choice == "🏠 Home":
        # Import here to avoid circular dependencies
        from modules.tourism_info import get_start_keyboard 
        await update.message.reply_text("🏠 Main Menu", reply_markup=get_start_keyboard())
        return CHOOSING_MODE
    
    return ORIGINAL_MENU

# Sub-menu handlers (History/Prices)
async def handle_tourism_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    site_key = context.user_data.get('current_site')
    site_data = data.get(site_key, {})
    if choice == "📜 Background History":
        await update.message.reply_text(f"📜 **History:**\n\n{site_data.get('background_history', 'N/A')}", parse_mode="Markdown")
    elif choice == "🏺 Cultural Note":
        await update.message.reply_text(f"🏺 **Culture:**\n\n{site_data.get('cultural_note', 'N/A')}", parse_mode="Markdown")
    elif choice == "🔙 Back to Menu":
        await update.message.reply_text("Menu:", reply_markup=get_original_menu_keyboard())
        return ORIGINAL_MENU
    return TOURISM_INFO

async def handle_ticket_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    site_key = context.user_data.get('current_site')
    site_data = data.get(site_key, {})
    if choice == "💰 Price":
        await update.message.reply_text(f"💰 **Price:** {site_data.get('ticket_price', 'N/A')}", parse_mode="Markdown")
    elif choice == "⏰ Opening Hours":
        await update.message.reply_text(f"⏰ **Hours:** {site_data.get('opening_hour', 'N/A')}", parse_mode="Markdown")
    elif choice == "🔙 Back to Menu":
        await update.message.reply_text("Menu:", reply_markup=get_original_menu_keyboard())
        return ORIGINAL_MENU
    return TICKET_INFO