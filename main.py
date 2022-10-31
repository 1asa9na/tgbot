import logging
from aiogram import Bot, Dispatcher, executor, types

f = open("token.txt")
bot = Bot(token=f.read())
f.close()

dp = Dispatcher(bot)

# Configure logging
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def start_message_handle(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("START CHATTING", callback_data='start'))
    await message.answer("Hi dear!♥️", reply_markup=markup)


@dp.callback_query_handler(lambda callback: callback.data in ['start', 'back'])
async def main_menu_handler(callback: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💕SMALL DROPBOX", callback_data="small"))
    markup.add(types.InlineKeyboardButton("💕MEDIUM DROPBOX", callback_data="medium"))
    markup.add(types.InlineKeyboardButton("💕LARGE DROPBOX", callback_data="large"))
    await callback.message.answer("To familiarize yourself with the plans, "
                          "select the one you need by clicking on "
                          "the appropriate button", reply_markup=markup)


@dp.callback_query_handler(lambda callback: callback.data in ["small",
                                                              "medium",
                                                              "large"])
async def check_callback_data(callback):
    options = {
        "small": [35, "indefinitely", 55, 55],
        "medium": [55, "indefinitely", 110, 120],
        "large": [70, "indefinitely", 256, 125]
    }
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Pay", callback_data=callback.data))
    markup.add(types.InlineKeyboardButton("Back", callback_data="back"))
    data = str(callback.data)
    await callback.message.answer(f"Plan: 💕{data.upper()} DROPBOX\n"
                          f"Cost: {options[data][0]} USD\n"
                          f"Validity: {options[data][1]}\n\n"
                          f"You will get access to the following resources:\n"
                          f"-💕{data.upper()} DROPBOX (channel)\n\n"
                          f"💋 {options[data][2]} vids and"
                          f" {options[data][3]} pics 🔥", reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)