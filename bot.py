import os
import time
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

SYSTEM_PROMPT = """You are a helpful AI assistant running on a Telegram bot. 
Respond naturally, clearly, and concisely to user messages."""

def ask_gemini(prompt):
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }
    try:
        res = requests.post(GEMINI_URL, json=payload, timeout=15)
        print(f"Gemini HTTP Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            print(f"Gemini Error Body: {res.text}")
    except Exception as e:
        print(f"Gemini Exception: {e}")
    return "Sorry, I ran into an issue processing that request."

def send_telegram_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    res = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
    print(f"Telegram sendMessage Status: {res.status_code}")

def start_polling():
    offset = None
    print(">>> BOT IS LIVE AND POLLING TELEGRAM NOW <<<", flush=True)
    while True:
        try:
            url = f"{TELEGRAM_API_URL}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            
            res = requests.get(url, timeout=35).json()
            if res.get("ok"):
                for update in res.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    user_text = message.get("text")

                    if chat_id and user_text:
                        print(f"Received message from {chat_id}: {user_text}", flush=True)
                        reply = ask_gemini(user_text)
                        print(f"Sending reply: {reply}", flush=True)
                        send_telegram_message(chat_id, reply)
            else:
                print(f"Telegram getUpdates not OK: {res}", flush=True)
        except Exception as e:
            print(f"Polling Exception: {e}", flush=True)
            time.sleep(3)

if __name__ == "__main__":
    start_polling()
