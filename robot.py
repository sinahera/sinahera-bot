import requests
import json
from balebot import Bot

# === تنظیمات ===
BOT_TOKEN = "1295567526:bcBC6Mk8FMksGs0l6dwZsZbdnkDJ2JX-bso"
DEEPSEEK_API_KEY = "sk-2414f35c6e84456bbe88f9cb7360ed5b"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# === راه‌اندازی ربات ===
bot = Bot(token=BOT_TOKEN)

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

# === دستورات ربات ===
@bot.command("/start")
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "🤖 سلام! من ربات هوش مصنوعی DeepSeek هستم.\n\n"
        "سوالات خود را به صورت مستقیم برای من بفرستید."
    )

@bot.command("/ask")
def ask_handler(message):
    user_question = message.text.replace("/ask", "", 1).strip()
    
    if not user_question:
        bot.send_message(message.chat.id, "❌ لطفاً یک سوال بپرسید.\nمثال: /ask چطور غذا بپزم؟")
        return
    
    bot.send_message(message.chat.id, "⏳ در حال پردازش سوال شما...")
    
    answer = ask_deepseek(user_question)
    bot.send_message(message.chat.id, f"🤖 پاسخ:\n\n{answer}")

@bot.event
def on_message(message):
    if message.text and not message.text.startswith("/"):
        bot.send_message(message.chat.id, "⏳ در حال پردازش...")
        answer = ask_deepseek(message.text)
        bot.send_message(message.chat.id, f"🤖 {answer}")

# === اجرا ===
if __name__ == "__main__":
    print("🚀 ربات DeepSeek در حال اجراست...")
    bot.run()
