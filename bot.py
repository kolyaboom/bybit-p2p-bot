import os
import asyncio
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Local Green Bank", callback_data="local_green")]
    ]
)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Выберите метод оплаты:", reply_markup=keyboard)

async def fetch_p2p_data():
    url = "https://api2.bybit.com/fiat/otc/item/online"
    payload = {
        "userId": "",
        "tokenId": "USDT",
        "currencyId": "RUB",
        "payment": ["Local Green Bank"],
        "side": "1",
        "size": "20",
        "page": "1"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            data = response.json()
            return data.get("result", {}).get("items", [])
        except Exception as e:
            print(f"❌ Ошибка при получении данных с Bybit: {e}")
            return []
        data = response.json()

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    if callback.data == "local_green":
        offers = await fetch_p2p_data()
        selected_offers = offers[5:11]
        if not selected_offers:
            await callback.message.answer("Не удалось получить предложения.")
            return
        prices = [float(offer["price"]) for offer in selected_offers]
        avg_price = sum(prices) / len(prices)
        await callback.message.answer(f"Средняя цена покупки USDT (6–11): {avg_price:.2f} RUB")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# -------------------------------
# 🟡 Фейковый веб-сервер для Render
# -------------------------------
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running.')

def run_http_server():
    server = HTTPServer(('0.0.0.0', 10000), PingHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()
