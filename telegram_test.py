import requests

BOT_TOKEN = "7689174821:AAFhAvZf2VzDG0DIMigozNG4w8qugGJ2ofM"
GROUP_ID = "-2774425255"
msg = "👋 Test từ telegram_test.py"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
response = requests.post(url, json={"chat_id": GROUP_ID, "text": msg})

print("Status:", response.status_code)
print("Body:", response.text)

