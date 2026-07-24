import requests
import json
import time

# === تنظیمات ===
BOT_TOKEN = "1295567526:bcBC6Mk8FMksGs0l6dwZsZbdnkDJ2JX-bso"
DEEPSEEK_API_KEY = "sk-2414f35c6e84456bbe88f9cb7360ed5b"
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
    
    response = requests.post(DEEPSEEK_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"خطا در ارتباط با DeepSeek: {response.status_code}"

def send_message(chat_id, text):
    url = BALE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_updates(offset=None):
    url = BALE_URL + "getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()

def handle_message(message):
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

if __name__ == "__main__":
    print("🚀 ربات DeepSeek در حال اجراست...")
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    if "message" in update:
                        handle_message(update["message"])
                    offset = update["update_id"] + 1
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
