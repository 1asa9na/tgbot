import requests
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle import Keyboard, KeyboardButtonColor, OpenLink, Text, CtxStorage, API


bot = Bot(token="vk1.a.0AqGLnQcjzjxYkngNr9LQBgHmoqdGU-ai8Fvc-BDBPaeazYUGP5MJftnx2rI3eYJIbLxVJ-KkPVGYo6dns3VvMNwfi8VDvmrfNyjYn0ffXTcbTJESb5L9BBaf29Dvl_1U8ABTr84qL8c4v6QdEI9YIGWZjCSlkRDMfbb84Q4CYmj4tIYgTkhncooNqvn_tQa")
api = API(token="vk1.a.0AqGLnQcjzjxYkngNr9LQBgHmoqdGU-ai8Fvc-BDBPaeazYUGP5MJftnx2rI3eYJIbLxVJ-KkPVGYo6dns3VvMNwfi8VDvmrfNyjYn0ffXTcbTJESb5L9BBaf29Dvl_1U8ABTr84qL8c4v6QdEI9YIGWZjCSlkRDMfbb84Q4CYmj4tIYgTkhncooNqvn_tQa")
ctx_storage = CtxStorage()


class IfStart(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        try:
            return eval(event.payload)["command"] == 'start'
        except TypeError:
            return False


class IfChat(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        return event.payload is None


class IfAction(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        try:
            return eval(event.payload)["command"] == "action"
        except TypeError:
            return False


@bot.on.message(IfStart())
async def start_message_handler(message: Message):
    keyboard = Keyboard(one_time=True)
    keyboard.add(Text("Курсы валют", payload={"command": "action", "data": "learn"}))
    keyboard.add(Text("Курсы бирж", payload={"command": "action", "data": "exchange"}))
    await message.answer("Выберите действие:", keyboard=keyboard)


@bot.on.message(IfChat())
async def chat_message_handler(message: Message):
    if ctx_storage.contains(message.from_id):
        keyboard = Keyboard()
        keyboard.add(Text("Вернуться", payload={"command": "start"}), KeyboardButtonColor.NEGATIVE)
        if ctx_storage.get(message.from_id)["stage"].split('_')[0] == "learn":
            if ctx_storage.get(message.from_id)["stage"].split('_')[1] == "1":
                results = await search_coins(message.text.lower())
                if len(results) == 0:
                    await message.answer("Валюты не найдены!\nВведите ещё раз.", keyboard=keyboard)
                else:
                    lst = '\n'.join([f'{i+1}. {results[i]}' for i in range(len(results))])
                    ctx_storage.set(message.from_id, {"stage": "learn_2", "local_data": results, "global_data": ctx_storage.get(message.from_id)["global_data"]})
                    await message.answer(f"Найдено {len(results)} валют. Введите номера нужных через пробел.\nДля выделения диапазона используйте \"-\"\n{lst}", keyboard=keyboard)
            elif ctx_storage.get(message.from_id)["stage"].split('_')[1] == "2":
                results = []
                try:
                    if ' ' in message.text:
                        for i in message.text.split():
                            if '-' in i:
                                for j in range(int(i.split('-')[0])-1, int(i.split('-')[1])):
                                    if ctx_storage.get(message.from_id)["local_data"][j] not in results:
                                        results.append(ctx_storage.get(message.from_id)["local_data"][j])
                            else:
                                if ctx_storage.get(message.from_id)["local_data"][int(i)-1] not in results:
                                    results.append(ctx_storage.get(message.from_id)["local_data"][int(i)-1])
                    else:
                        if '-' in message.text:
                            for j in range(int(message.text.split('-')[0]) - 1, int(message.text.split('-')[1])):
                                if ctx_storage.get(message.from_id)["local_data"][j] not in results:
                                    results.append(ctx_storage.get(message.from_id)["local_data"][j])
                        else:
                            if ctx_storage.get(message.from_id)["local_data"][int(message.text) - 1] not in results:
                                results.append(ctx_storage.get(message.from_id)["local_data"][int(message.text) - 1])
                    lst = '\n'.join(f'{i+1}. {results[i]}' for i in range(len(results)))
                    keyboard = Keyboard()
                    keyboard.add(Text("Добавить", payload={"command": "action", "data": "learn_add"}), KeyboardButtonColor.PRIMARY)
                    keyboard.add(Text("Ввести ещё...", payload={"command": "action", "data": "learn"}))
                    keyboard.add(Text("Вернуться", payload={"command": "start"}), KeyboardButtonColor.NEGATIVE)
                    await message.answer(f"Вами выбраны следующие валюты:\n{lst}", keyboard=keyboard)
                    ctx_storage.set(message.from_id, {"stage": "learn_2", "local_data": results, "global_data": ctx_storage.get(message.from_id)["global_data"]})
                except IndexError:
                    await message.answer("Неверный номер списка.")
                except ValueError:
                    await message.answer("Неверные параметры.")
    else:
        keyboard = Keyboard()
        keyboard.add(Text("Начать", payload={"command": "start"}))
        await message.answer("Здравствуйте\nPowered by CoinGecko", keyboard=keyboard)


@bot.on.message(IfAction())
async def action_message_handler(message: Message):
    payload = eval(message.payload)
    if payload["data"] == "learn":
        await learn(message)
    elif payload["data"] == "learn_add":
        await learn_add(message)
    elif payload["data"] == "learn_show":
        await learn_show(message)
    elif payload["data"] == "excange":
        await exchange(message)


async def learn(message: Message):
    await message.answer("Введите часть названия криптовалюты для поиска...")
    if ctx_storage.contains(message.from_id):
        if ctx_storage.get(message.from_id)["stage"].split('_')[0] != "learn":
            ctx_storage.set(message.from_id, {"stage": "learn_1", "local_data": None, "global_data": []})
        else:
            ctx_storage.set(message.from_id, {"stage": "learn_1",
                                              "local_data": None,
                                              "global_data": ctx_storage.get(message.from_id)["global_data"]})
    else:
        ctx_storage.set(message.from_id, {"stage": "learn_1", "local_data": None, "global_data": []})


async def learn_add(message: Message):
    picked = ctx_storage.get(message.from_id)["global_data"]
    for i in ctx_storage.get(message.from_id)["local_data"]:
        if i not in picked:
            picked.append(i)
    ctx_storage.set(message.from_id, {"stage": "learn_2", "local_data": None, "global_data": picked})
    keyboard = Keyboard()
    keyboard.add(Text("Показать", payload={"command": "action", "data": "learn_show"}), KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("Добавить валюту...", payload={"command": "action", "data": "learn"}))
    keyboard.add(Text("Вернуться", payload={"command": "start"}), KeyboardButtonColor.NEGATIVE)
    await message.answer("Показать курсы?", keyboard=keyboard)


async def learn_show(message: Message):
    crncs = "%2C%20".join(ctx_storage.get(message.from_id)["global_data"])
    response = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={crncs}&order=market_cap_desc&per_page=100&page=1&sparkline=false").json()
    await message.answer("\n\n".join([f"{i['symbol'].upper()} - {i['name']}\nЦена: {i['current_price']} USD\nМакс. цена за 24 часа: {i['high_24h']} USD\nМин. цена за 24 часа: {i['low_24h']} USD" for i in response]))


async def search_coins(text):
    response = requests.get("https://api.coingecko.com/api/v3/coins/list")
    results = [i for i in map(lambda x: x['id'], response.json()) if i.find(text) > 0]
    return results


async def exchange(message: Message):
    response = requests.get("https://api.coingecko.com/api/v3/")


bot.run_forever()