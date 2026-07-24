import requests
import json
import time
import os

# === تنظیمات با استفاده از متغیرهای محیطی ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# اگر متغیرهای محیطی تعریف نشده باشند، خطا بده
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables!")

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is not set in environment variables!")

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
BALE_URL = f"https://api.bale.ai/v1/bots/{BOT_TOKEN}/"

def ask_deepseek(question):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "تو یک دستیار هوشمند و مفید هستی."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"خطا در ارتباط با DeepSeek: {response.status_code}"
    except Exception as e:
        return f"خطا در ارتباط با DeepSeek: {str(e)}"

def send_message(chat_id, text):
    try:
        url = BALE_URL + "sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.ok
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def get_updates(offset=None):
    try:
        url = BALE_URL + "getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return {"ok": False, "result": []}

def handle_message(message):
    try:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if not text:
            return
        
        if text.startswith("/start"):
            send_message(chat_id, "🤖 سلام! من ربات هوش مصنوعی DeepSeek هستم.\n\nسوالات خود را بپرسید.")
            return
        
        if text.startswith("/ask"):
            question = text.replace("/ask", "", 1).strip()
            if not question:
                send_message(chat_id, "❌ لطفاً یک سوال بپرسید.\nمثال: /ask چطور غذا بپزم؟")
                return
            send_message(chat_id, "⏳ در حال پردازش سوال شما...")
            answer = ask_deepseek(question)
            send_message(chat_id, f"🤖 پاسخ:\n\n{answer}")
            return
        
        # پیام عادی
        send_message(chat_id, "⏳ در حال پردازش...")
        answer = ask_deepseek(text)
        send_message(chat_id, f"🤖 {answer}")
        
    except Exception as e:
        print(f"Error handling message: {e}")

if __name__ == "__main__":
    print("🚀 ربات DeepSeek در حال اجراست...")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print(f"DeepSeek API Key: {DEEPSEEK_API_KEY[:10]}...")
    
    offset = None
    error_count = 0
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates.get("ok") and updates.get("result"):
                error_count = 0  # Reset error count on success
                for update in updates["result"]:
                    if "message" in update:
                        handle_message(update["message"])
                    offset = update["update_id"] + 1
            
            time.sleep(1)
            
        except Exception as e:
            error_count += 1
            print(f"Error in main loop: {e}")
            if error_count > 10:
                print("Too many errors, waiting 60 seconds...")
                time.sleep(60)
                error_count = 0
            else:
                time.sleep(5)
