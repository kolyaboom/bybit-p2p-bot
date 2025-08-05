import asyncio
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart

# 🔐 Твой токен от BotFather
TOKEN = '8236071155:AAHOORv1Dfenoh5Q0KDn-EtScwhJGwaLggU'

# 🧠 Создаем экземпляры
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔘 Кнопка
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Local Green Bank", callback_data="local_green")]
    ]
)

# 🧪 Обработка команды /start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Выберите метод оплаты:", reply_markup=keyboard)

# 🌐 Функция запроса к Bybit P2P API
async def fetch_p2p_data():
    url = "https://api2.bybit.com/fiat/otc/item/online"
    payload = {
        "userId": "",
        "tokenId": "USDT",
        "currencyId": "RUB",
        "payment": ["Local Green Bank"],
        "side": "1",  # Покупка
        "size": "10",  # Получаем хотя бы 11 предложений
        "page": "1"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        data = response.json()
        return data.get("result", {}).get("items", [])

# 📲 Обработка нажатия кнопки
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    if callback.data == "local_green":
        offers = await fetch_p2p_data()
        selected_offers = offers[5:11]  # с 6 по 11
        if not selected_offers:
            await callback.message.answer("Не удалось получить предложения.")
            return
        prices = [float(offer["price"]) for offer in selected_offers]
        avg_price = sum(prices) / len(prices)
        await callback.message.answer(f"Средняя цена покупки USDT (6–11 строк): {avg_price:.2f} RUB")

# 🚀 Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
