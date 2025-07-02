import requests
import pandas as pd
import numpy as np
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

def get_klines(symbol="BTCUSDT", interval="1m", limit=100):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url, timeout=10).json()
    df = pd.DataFrame(data, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df = df.dropna(subset=['close'])
    return df

def analyze(df):
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['signal'] = df['macd'].ewm(span=9).mean()

    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df.iloc[-1][['close', 'ema_12', 'ema_26', 'macd', 'signal', 'rsi']]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Gửi Telegram lỗi:", e)

def run_bot():
    while True:
        try:
            df = get_klines("BTCUSDT")
            result = analyze(df).round(2)
            direction = "📉 SHORT" if result['macd'] < result['signal'] else "📈 LONG"

            msg = (
                f"📊 *HNCoinsBot - BTCUSDT*\n"
                f"Giá: `{result['close']}`\n"
                f"EMA12: `{result['ema_12']}`\n"
                f"EMA26: `{result['ema_26']}`\n"
                f"MACD: `{result['macd']}` | Signal: `{result['signal']}`\n"
                f"RSI: `{result['rsi']}`\n"
                f"Xu hướng: *{direction}*"
            )

            send_telegram(msg)
            print("✅ Đã gửi báo cáo Telegram.")
        except Exception as e:
            print("❌ Lỗi:", e)

        time.sleep(300)

if __name__ == "__main__":
    run_bot()
