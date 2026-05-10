# 🇪🇹 Ethiopia Information Assistant (AI-Powered Bot)

**A Smart Hybrid Tourism Companion for Exploring Ethiopia.**

## 🎯 Project Overview

The **Ethiopia Information Assistant** is an advanced Telegram Bot designed to bridge the gap between structured tourism data and AI-driven assistance. It combines a **hardcoded database** of 50+ top destinations with **Real-Time APIs** (Weather, Wikipedia, Maps) and **Generative AI** (Google Gemini) to provide tourists with a complete, interactive travel guide.

### ❗ What Problem Does It Solve?
Travelers in Ethiopia often face fragmented information sources. This project solves that by:
*   **Centralizing Data:** Providing key tourism details (History, Prices, Hotels) in one accessible interface.
*   **Visual Discovery:** Dynamically fetching high-quality images of sites using Wikipedia APIs.
*   **Real-Time Context:** Offering live weather updates and instant driving directions.
*   **AI Assistance:** Solving the "unpredictable query" problem by using a Large Language Model (LLM) for general questions.

### 👤 Who Is It For?
*   Local and international **tourists**
*   **Travel planners** and tour guides
*   Students and researchers exploring Ethiopian heritage

---

## ⚙️ Key Features & Functionalities

### 1️⃣ 🤖 Dual-Mode Interaction
*   **🏛️ Original Guide:** A structured, menu-driven interface for reliable, fact-checked details (History, Hotels, Ticket Prices, Opening Hours).
*   **🧠 AI Chatbot:** A free-form conversational mode powered by **Google Gemini**. Users can ask complex questions like *"What is the best time to visit Omo Valley?"* or *"Tell me about Ethiopian coffee culture."*

### 2️⃣ 🖼️ Smart Visual Exploration
*   **Dynamic Image Search:** Fetches high-quality images from **Wikipedia** based on the site name.
*   **Smart Filtering:** Automatically filters out icons, maps, and system images to ensure only relevant scenery is shown.
*   **Gallery Mode:** Users can view images in batches and click "🔄 Refresh" to load more.

### 3️⃣ 🗺️ Mapping & Navigation
*   **Geocoding:** Converts site names into precise GPS coordinates using **OpenStreetMap (Nominatim)**.
*   **Driving Directions:** Generates a direct route link from the user's current live location to the tourist site via Google Maps.

### 4️⃣ ⛅ Real-Time Weather
*   Integrates with the **OpenWeatherMap API**.
*   Provides current temperature, humidity, "feels like" temperature, and specific safety advice based on the weather conditions.

### 5️⃣ 📝 Feedback System
*   **User Feedback:** Users can send suggestions or report bugs using `/feedback`.
*   **Admin Dashboard:** The bot forwards feedback to a private admin channel with **Inline Buttons** (✅ Accept / ❌ Reject) for team management.

---

## 📂 Project Architecture

The project uses a modular file structure for scalability and maintainability:

---

````md
# SE_python_project2025

## 📂 File Structure

SE_python_project2025/
├── main.py           # Entry point: initializes bot, handlers, states, and starts polling
├── data.py           # Static database of 50+ Ethiopian tourist sites
├── requirements.txt  # Python dependencies
├── .env              # Environment variables (API keys, tokens)
├── modules/          # Feature modules (business logic)
│   ├── ai_chatbot.py
│   ├── explore_images.py
│   ├── mapping.py
│   ├── weather.py
│   ├── tourism_info.py
│   ├── feedback.py
│   ├── help_system.py
│   └── images.py
└── utils/            # Shared utilities
    ├── __init__.py
    ├── config.py
    └── models.py
````

---

## 🚀 How to Run

Follow these steps to get the bot running on your local machine.

### 1️⃣ Prerequisites

* **Python 3.10** or higher installed
* **API Keys Required:**

  * 🤖 Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
  * 🧠 Google Gemini API Key (from [Google AI Studio](https://aistudio.google.com/))
  * ⛅ OpenWeatherMap API Key (from [OpenWeather](https://openweathermap.org/api))

### 2️⃣ Installation Steps

#### Step 1: Clone the Repository

```bash
git clone <your-repository-link>
cd SE_python_project2025
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Configure Environment

Create a `.env` file in the root folder:

```ini
TELEGRAM_BOT_TOKEN=your_telegram_token_here
WEATHER_API_KEY=your_weather_key_here
GEMINI_API_KEY=your_gemini_key_here
FEEDBACK_CHANNEL_ID=-100xxxxxxxxxx  # Optional: Admin feedback logs
```

#### Step 4: Run the Application

```bash
python main.py
```

---

### 3️⃣ Usage

* **Start:** Send `/start` to the bot to begin
* **Original Guide:** Browse Hotels, History, Maps
* **AI Chatbot:** Ask free-form questions about Ethiopia
* **Help:** Use `/help` for full command list

---

## 💡 Why We Chose This Idea

* 🌍 **Economic Impact:** Tourism is a vital sector for Ethiopia
* 👤 **User Need:** Travelers need simple, reliable, real-time information
* 💻 **Technical Challenge:** Integrates:

  * Databases & Data Structures
  * RESTful APIs (Weather, Wikipedia, Maps)
  * Generative AI Integration
  * Asynchronous Programming

---


