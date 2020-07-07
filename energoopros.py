import config
import logging
import datetime as dt
import requests
import asyncio
from bs4 import BeautifulSoup
import re
from aiogram import Bot, Dispatcher, executor, types
from sqlighter import SQLighter


def find_home(string, home_number):
    # Если номер дома это просто число, дробь или число с буквой, то ищем совпадения тут
    mas = re.findall(r'\d+[/-]*[\d\w]*', string)
    if str(home_number) in mas:
        return True
    # Перебор всех найденных диапазонов номеров (типа ХХ-НН)
    try:
        home_number_int = int(home_number)  # Если искомый номер не число, то и в диапазонах его искать не будем
        mas = re.findall(r'\d+-\d+', string)
        for i in mas:
            first = (re.search(r'^\d+', i)).group(0)
            second = (re.search(r'\d+$', i)).group(0)
            if ((int(first) < home_number_int) and (int(second) > home_number_int)):
                return True
        return False
    except:
        pass
    return False


def send_request(req):
    resp = requests.request('GET', req)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'lxml')
        if soup.find("ul", class_="po_address"):
            # print(soup.findAll("div", class_="po_time"))
            # print(soup.findAll("ul", class_="po_address"))
            return (
            [list(tup) for tup in zip(soup.findAll("div", class_="po_time"), soup.findAll("ul", class_="po_address"))])
            # return str(soup.findAll("div", class_="po_time")) + str(soup.findAll("ul", class_="po_address"))
        return None


def calc_timedelta(delta_days):
    now = dt.datetime.now()
    start_day = '{:02}'.format(now.day)
    start_month = '{:02}'.format(now.month)
    start_year = now.year

    tomorrow = now + dt.timedelta(days=delta_days)
    end_day = '{:02}'.format(tomorrow.day)
    end_month = '{:02}'.format(tomorrow.month)
    end_year = tomorrow.year
    return (start_day, start_month, start_year, end_day, end_month, end_year)


def request_data(street, timedelta):
    start_day, start_month, start_year, end_day, end_month, end_year = calc_timedelta(timedelta)
    req = 'https://gorsetitomsk.ru/po-search?limit=0&street=' + street + '&enddate=' + str(end_year) + '-' + str(
        end_month) + '-' + str(end_day) + '&startdate=' + str(start_year) + '-' + str(start_month) + '-' + str(
        start_day) + '&view=search'
    resp = send_request(req)
    return resp


async def scheduled(wait_for):
    old_date = dt.datetime.now()
    old_date = old_date + dt.timedelta(days=-2)
    while True:
        await asyncio.sleep(wait_for)
        new_date = dt.datetime.now()
        if ((new_date.day != old_date.day) and (new_date.hour > 10)):
            old_date = new_date
            users_with_subscribe = db.users_with_subscribe()
            for current_user in users_with_subscribe:
                addr = db.list_address(current_user[0])
                for current_address in addr:
                    response = request_data(current_address[0], 1)
                    if (response):
                        for resp_elem in response:
                            print(resp_elem[0])
                            print(resp_elem[1])
                            if find_home(str(resp_elem[1]), current_user[1]):
                                time = re.sub(r'<.+>', '', str(resp_elem[0]))
                                await bot.send_message(
                                    f"Обнаружено уведомление об отключении электроэнергии по улице - {current_user[0]}, номер дома - {current_user[1]} \n Во время "
                                    f"{time}")
                            """print(resp_elem)
                            # and find_home(response, j[1])
                            #await message.reply(f"Обнаружено уведомление об отключении электроэнергии по улице - {i[0]}, номер дома - {i[1]}")
                            await bot.send_message(i[0], f"Обнаружено уведомление об отключении электроэнергии по улице - {j[0]}, номер дома - {j[1]}")"""


if __name__ == "__main__":
    # задаем уровень логов
    logging.basicConfig(level=logging.INFO)

    # инициализируем бота
    bot = Bot(token=config.API_TOKEN)
    dp = Dispatcher(bot)

    # инициализируем соединение с БД
    db = SQLighter('db.db')


    @dp.callback_query_handler(lambda call: True)
    async def query_handler(call):
        if call.data == "delete_all":
            db.clear_all_address(call.from_user.id)
            await call.answer('Все адреса для пользователя удалены')
        else:
            if (db.delete_addr(call.from_user.id, [call.data.split(sep='\n')[0], call.data.split(sep='\n')[1]])):
                await call.answer('Удален один адрес')


    # Команды приветствия и помощи
    @dp.message_handler(commands=['start'])
    async def process_start_command(message: types.Message):
        await message.reply("Привет!\nЭто бот предупреждающий о плановых отключениях электроэнергии в г. Томске")


    @dp.message_handler(commands=['help'])
    async def process_help_command(message: types.Message):
        await message.reply("""Данный бот раз в сутки проверяет списки адресов на отключение электричества, 
                            Для пополнения списка адресов просто введите необходимый адрес в формате Улица НомерДома
                            Бот понмает такие команды:
                            /allclear - очистить весь список адресов
                            /test - послать тестовый запрос по всему списку для данного пользователя
                            /listaddress - вывести список всех адресов для данного пользователя
                            /subscribe - включить рассылку уведомлений
                            /unsubscribe - отключить рассылку уведомлений""")


    @dp.message_handler(commands=['allclear'])
    async def all_clear(message: types.Message):
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="Нажми для удаления всех адресов", callback_data="delete_all")
        keyboard.add(callback_button)
        await bot.send_message(message.chat.id, "Действительно хотите удалить все отслеживаемые адреса?",
                               reply_markup=keyboard)


    # Тестовый запрос по списку для отключения на текущего пользователя
    @dp.message_handler(commands=['test'])
    async def process_test_request(message: types.Message):
        if (not db.subscriber_exists(message.from_user.id)):
            await message.reply("Данный пользователь еще не зарегистрирован в сиситеме")
        else:
            if (db.get_subscription(message.from_user.id)[0] == (0,)):
                await message.reply("У пользователя отключены уведомления")
            else:
                addr = db.list_address(message.from_user.id)
                for current_address in addr:
                    response = request_data(current_address[0], 1)
                    if (response):
                        for resp_elem in response:
                            if find_home(str(resp_elem[1]), current_address[1]):
                                time = re.sub(r'<.+>', '', str(resp_elem[0]))
                                await message.reply(
                                    f"Обнаружено уведомление об отключении электроэнергии по улице - {current_address[0]}, номер дома - {current_address[1]} \n Во время "
                                    f"{time}")


    # Выдает все имеющиеся в базе адреса для данного пользователя
    @dp.message_handler(commands=['listaddress'])
    async def list_address(message: types.Message):
        out = db.list_address(message.from_user.id)
        for i in out:
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text='Удалить адрес', callback_data=str(i[0] + '\n' + i[1]))
            keyboard.add(callback_button)
            await bot.send_message(message.chat.id, str(i[0] + ' ' + i[1]), reply_markup=keyboard)


    # Команда активации подписки
    @dp.message_handler(commands=['subscribe'])
    async def subscribe(message: types.Message):
        if (not db.subscriber_exists(message.from_user.id)):
            # если юзера нет в базе, добавляем его
            db.add_subscriber(message.from_user.id)
        else:
            # если он уже есть, то просто обновляем ему статус подписки
            db.update_subscription(message.from_user.id, True)
        await message.answer(
            "Вы успешно подписались на рассылку!\nКак только появятся данные по добавленным вами адресам, Вы получите уведомление")


    # Команда отписки
    @dp.message_handler(commands=['unsubscribe'])
    async def unsubscribe(message: types.Message):
        if (not db.subscriber_exists(message.from_user.id)):
            # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
            db.add_subscriber(message.from_user.id, False)
            await message.answer("Вы и так не подписаны.")
        else:
            # если он уже есть, то просто обновляем ему статус подписки
            db.update_subscription(message.from_user.id, False)
            await message.answer("Вы успешно отписаны от рассылки.")


    # Добавляет новый адрес
    @dp.message_handler()
    async def add_address(message: types.Message):
        house = message.text.split(' ')[-1]
        street = ' '.join(message.text.split(' ')[0: -1])
        if request_data(street,
                        - 365):  # Проверка что такая улица есть у электриков (чтобы проверка сработала, надо чтобы хоть раз в год на улице запланированно выключали свет)
            db.add_address(message.from_user.id, street, house)
            await message.answer('Адрес - ' + message.text + ' - успешно добавлен в базу данных')
        else:
            await message.answer(
                'Или улицы - ' + street + ' - в городе Томске нет, или на ней не выключают свет. Не стоит добавлять такой уникальный объект в нашу базу')


    dp.loop.create_task(scheduled(5))  # пока что оставим 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)
