import os, requests
from dotenv import load_dotenv
load_dotenv()
TG = os.getenv('TELEGRAM_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID')
def send_message(text):
    if not TG or not CHAT:
        print('Telegram not configured.')
        return False
    url = f'https://api.telegram.org/bot{TG}/sendMessage'
    try:
        r = requests.post(url, json={'chat_id':CHAT,'text':text,'parse_mode':'HTML'}, timeout=10)
        return r.status_code==200
    except Exception as e:
        print('Telegram send failed:', e)
        return False
