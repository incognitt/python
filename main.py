import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

# Замените 'YOUR_BOT_TOKEN' на фактический токен вашего бота
bot = telebot.TeleBot('6643283580:AAEq4wtoANh1nv2RDFzxhezn6NvEnUCGp6o')

# Задайте идентификатор чата администратора
admin_chat_id = '455499371'  # Замените на актуальный идентификатор чата

user_data = {}
contact_data = {}

# Создаем клавиатуру с кнопкой "Назад"
def create_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton('Назад')
    markup.add(button_back)
    return markup


# Пример использования в вашей функции process_agreement
# Создаем кнопку "Начать" и добавляем ее в клавиатуру
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_button = types.KeyboardButton('Начать')
start_markup.add(start_button)

# Функция для обработки команды /start и первого сообщения
@bot.message_handler(func=lambda message: message.text == '/start' or message.text == 'Начать')
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Сделать заказ')
    button2 = types.KeyboardButton('Калькулятор стоимости')
    button3 = types.KeyboardButton('Связаться с администратором')
    markup.add(button1)
    markup.add(button2, button3)
    bot.send_message(message.chat.id, 'Добро пожаловать! Что вы хотите сделать?', reply_markup=markup)

def create_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton('Назад')
    markup.add(button_back)
    return markup

# Функция для обработки команды "Назад"
@bot.message_handler(func=lambda message: message.text == 'Назад')
def go_back(message):
    # Здесь вы можете определить логику возврата на предыдущий шаг
    bot.send_message(message.chat.id, 'Вы вернулись на предыдущий шаг.')

@bot.message_handler(func=lambda message: message.text == 'Сделать заказ')
def process_info(message):
    # Создаем список правил магазина
    rules_of_store = [
    "1. Все товары продаются по фиксированным ценам.",
    "2. Оплата товаров производится по полной предоплате.",
    "3. Доставка товаров осуществляется до 1 месяца.",
    "4. Возврата товара нет, так как вы сами полностью выбираете модель, цвет и размер .",
    "5. Для оформления заказа необходимо предоставить ссылку на товар и контактные данные.",
    "6. Если вы хотите заказать товар с POIZON , то процедура вся таже самая только расценки на товар и доставку будут другие"
    ]

    # Объединяем элементы списка в одну строку с помощью "\n" для переноса строки
    rules_text = "\n".join(rules_of_store)

    # Выводим правила магазина на экран
    bot.send_message(message.chat.id, f"Правила магазина:\n{rules_text}")

    # Создаем клавиатуру с кнопками "Согласен" и "Не согласен"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttonAgree = types.KeyboardButton('Согласен')
    buttonDesAgree = types.KeyboardButton('Не согласен')
    markup.add(buttonAgree, buttonDesAgree)

    # Выводим вопрос о согласии и кнопки "Согласен" и "Не согласен"
    bot.send_message(message.chat.id, 'Согласны ли вы с правилами магазина?', reply_markup=markup)
    bot.register_next_step_handler(message, process_agreement)

def process_agreement(message):
    agreement = message.text
    if agreement.lower() in ['да', 'согласен', 'согласен', 'yes']:
        bot.send_message(message.chat.id, 'Введите ссылку на заказ:')
        bot.register_next_step_handler(message, process_article_number)
    elif agreement.lower() in ['нет', 'не согласен']:
        bot.send_message(message.chat.id, 'Вы не согласны с правилами магазина.')
        bot.send_message(message.chat.id, 'Вы будете возвращены на начальную страницу.')
        start(message)

        # Здесь можно вызвать start() функцию, если она не принимает аргументов, чтобы вернуть пользователя на начальную страницу.
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите "Согласен" или "Не согласен" из предложенных вариантов.')


def process_article_number(message):
    article_number = message.text
    user_data[message.chat.id] = {'article_number': article_number}
    bot.send_message(message.chat.id, 'Введите размер ноги в миллиметрах и размер товара на карточке товара:')
    bot.register_next_step_handler(message, process_foot_size)

# Далее следующие шаги обработки заказа...
def process_foot_size(message):
    foot_size = message.text
    user_data[message.chat.id]['foot_size'] = foot_size
    bot.send_message(message.chat.id, 'Введите ФИО (Фамилия Имя Отчество) в одной строке:')
    bot.register_next_step_handler(message, process_full_name)

def process_full_name(message):
    full_name = message.text
    user_data[message.chat.id]['full_name'] = full_name
    bot.send_message(message.chat.id, 'Введите адрес удобного вам Сдэк:')
    bot.register_next_step_handler(message, process_address)

def process_address(message):
    address = message.text
    user_data[message.chat.id]['address'] = address
    bot.send_message(message.chat.id, 'Введите ссылку на ваш профиль в Telegram для связи:')
    bot.register_next_step_handler(message, process_telegram_profile)

def process_telegram_profile(message):
    telegram_profile = message.text
    user_data[message.chat.id]['telegram_profile'] = telegram_profile
    send_order_form(message)

def send_order_form(message):
    if 'article_number' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию о номере заказа.')
        return

    if 'foot_size' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию о размере ноги.')
        return


    if 'full_name' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию о ФИО.')
        return

    if 'address' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию об адресе.')
        return

    if 'telegram_profile' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию о профиле Telegram.')
        return

    order_details = f"Ссылка: {user_data[message.chat.id]['article_number']}\n" \
                    f"Размер : {user_data[message.chat.id]['foot_size']}\n" \
                    f"ФИО: {user_data[message.chat.id]['full_name']}\n" \
                    f"Адрес: {user_data[message.chat.id]['address']}\n" \
                    f"Ссылка на Telegram профиль: {user_data[message.chat.id]['telegram_profile']}\n"

    bot.send_message(message.chat.id, 'Спасибо! Вот ваша анкета заказа:')
    bot.send_message(message.chat.id, order_details)

    bot.send_message(admin_chat_id, 'Новая анкета заказа:')
    bot.send_message(admin_chat_id, order_details)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_main_menu = types.KeyboardButton('Вернуться в главное меню')
    #button_order_status = types.KeyboardButton('Калькулятор стоимости')
    markup.add(button_main_menu)
    bot.send_message(message.chat.id, 'Что вы хотите сделать дальше?', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Калькулятор стоимости')
def selectValue(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttonValueDollar = types.KeyboardButton('💵')
    buttonValueEuro = types.KeyboardButton('💶')
    buttonValueYuan = types.KeyboardButton('💴')
    markup.add(buttonValueDollar, buttonValueEuro, buttonValueYuan)
    bot.send_message(message.chat.id, 'Выберите валюту из магазина:', reply_markup=markup)
    bot.register_next_step_handler(message, process_selected_value)

def process_selected_value(message):
    selected_currency = message.text.lower()  # Преобразуем введенный текст в нижний регистр

    if selected_currency in ['💵', '💶', '💴']:
        user_data[message.chat.id] = {'selected_currency': selected_currency}
        bot.send_message(message.chat.id, f'Введите стоимость товара в {selected_currency}:')
        bot.register_next_step_handler(message, process_price_status)
    else:
        bot.send_message(message.chat.id, 'Выбрана некорректная валюта. Пожалуйста, выберите валюту из списка.')
        selectValue(message)

def process_price_status(message):
    try:
        product_price = float(message.text)
        selected_currency = user_data[message.chat.id]['selected_currency']

        if selected_currency == '💵':
            currencyDollar(message, product_price)
        elif selected_currency == '💶':
            currencyEuro(message, product_price)
        elif selected_currency == '💴':
            currencyYuan(message, product_price)

    except ValueError:
        bot.send_message(message.chat.id, 'Некорректное значение. Введите стоимость числом.')
    bot.send_message(message.chat.id, 'В стоимость не входит доставка.')
   # bot.send_message(message.chat.id,    'Доставка зависит от массы коробки ,приблизительно коробка весит 1.5кг => доставка идет как за 2кг и будет в районе 3к. Но точную стоимость уточнаяйте у продавца')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_main_menu = types.KeyboardButton('Вернуться в главное меню')
    button_recalculate = types.KeyboardButton('Рассчитать заново')
    button_order = types.KeyboardButton('Сделать заказ')
    markup.add(button_recalculate, button_order)
    markup.add(button_main_menu)
    bot.send_message(message.chat.id, 'Что вы хотите сделать дальше?', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Рассчитать заново')
def recalculate_price(message):
    selectValue(message)

@bot.message_handler(func=lambda message: message.text == 'Вернуться в главное меню')
def return_to_main_menu(message):
    start(message)




@bot.message_handler(func=lambda message: message.text == 'Связаться с администратором')
def process_call_reason(message):
    bot.send_message(message.chat.id, 'По какому вопросу вы хотите связаться с администратором?')
    bot.register_next_step_handler(message, process_call_reason_details)

def process_call_reason_details(message):
    call_reason = message.text
    contact_data[message.chat.id] = {'call_reason': call_reason}
    bot.send_message(message.chat.id, 'Введите ФИО (Фамилия Имя Отчество) в одной строке:')
    bot.register_next_step_handler(message, process_full_name_and_profile)

def process_full_name_and_profile(message):
    full_name = message.text
    contact_data[message.chat.id]['full_name'] = full_name
    bot.send_message(message.chat.id, 'Введите ссылку на ваш профиль в Telegram для связи:')
    bot.register_next_step_handler(message, process_telegram_profile_contact)

def process_telegram_profile_contact(message):
    telegram_profile = message.text
    contact_data[message.chat.id]['telegram_profile'] = telegram_profile
    send_contact_request(message)

def send_contact_request(message):
    if 'call_reason' not in contact_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию о причине обращения.')
        return

    if 'full_name' not in contact_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию о ФИО.')
        return

    if 'telegram_profile' not in contact_data[message.chat.id]:
        bot.send_message(message.chat.id, 'Не удалось получить информацию о профиле Telegram.')
        return

    contact_details = f"Причина обращения: {contact_data[message.chat.id]['call_reason']}\n" \
                      f"ФИО: {contact_data[message.chat.id]['full_name']}\n" \
                      f"Ссылка на Telegram профиль: {contact_data[message.chat.id]['telegram_profile']}\n"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_main_menu = types.KeyboardButton('Вернуться в главное меню')
    markup.add(button_main_menu)

    bot.send_message(message.chat.id, 'Спасибо за ваше обращение! С вами скоро свяжутся.', reply_markup=markup)
    bot.send_message(admin_chat_id, 'С вами хотят связаться:')
    bot.send_message(admin_chat_id, contact_details)



@bot.message_handler(func=lambda message: message.text == 'Вернуться в главное меню')
def return_to_main_menu(message):
    start(message)


def currencyDollar(message, product_price):
    # Получение курса доллара
    Dollar_rub_url = 'https://www.google.com/search?q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(Dollar_rub_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        convert = soup.find("span", {"class": "DFlfde SwHCTb", "data-precision": "2"})
        kurs = float(convert.text.replace(",", "."))

        rub_price = (product_price * (kurs + 7)) * 1.32  # Рассчитываем цену в рублях на основе курса

        # Собираем информацию в нужном формате
        info = f'💳 Стоимость товара: {rub_price:.2f} ₽;\n\n'
        info += '🚚 Срок доставки: 25 - 30 дней, в зависимости от вашего города;\n\n'
        #info += '\n'
        info += '❗️ Обратите внимание, что стоимость указана без учета доставки!\n\n'
        info += 'Для окончательного расчета с учетом доставки обратитесь к нашему менеджеру: @arsushkin!'

        # Отправляем информацию в сообщении
        bot.send_message(message.chat.id, info)

    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка при получении курса доллара.')


def currencyEuro(message, product_price):
    # Получение курса евро
    Euro_rub_url = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80%D0%BE-%D1%80%D1%83%D0%B1%D0%BB%D1%8C'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(Euro_rub_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        convert = soup.find("span", {"class": "DFlfde SwHCTb", "data-precision": "2"})
        kurs = float(convert.text.replace(",", "."))
        #bot.send_message(message.chat.id, f'Курс евро: {kurs:.2f} ₽')

        rub_price = (product_price * (kurs + 7)) * 1.32  # Рассчитываем цену в рублях на основе курса
        # Собираем информацию в нужном формате
        info = f'💳 Стоимость товара: {rub_price:.2f} ₽;\n\n'
        info += '🚚 Срок доставки: 25 - 30 дней, в зависимости от вашего города;\n\n'
        # info += '\n'
        info += '❗️ Обратите внимание, что стоимость указана без учета доставки!\n\n'
        info += 'Для окончательного расчета с учетом доставки обратитесь к нашему менеджеру: @arsushkin!'

        # Отправляем информацию в сообщении
        bot.send_message(message.chat.id, info)


    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка при получении курса евро.')



def currencyYuan(message, product_price):
    # Получение курса евро
    Yuan_rub_url = 'https://www.google.com/search?q=%D1%8E%D0%B0%D0%BD%D1%8C+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&hl=en&sxsrf=AM9HkKl519yGZrTTfMpWYuOuPTQh7q67JQ%3A1696695894496&iflsig=AO6bgOgAAAAAZSGUZoQzmORXStor9tQnIMOpjGpA8zrT'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(Yuan_rub_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        convert = soup.find("span", {"class": "DFlfde SwHCTb", "data-precision": "2"})
        kurs = float(convert.text.replace(",", "."))
        #bot.send_message(message.chat.id, f'Курс юаня: {kurs:.2f} ₽')
        rub_price = (product_price * (kurs + 3)) +700
        #rub_price = (product_price * (kurs + 1)) * 1.2  # Рассчитываем цену в рублях на основе курса
        # Собираем информацию в нужном формате
        info = f'💳 Стоимость товара: {rub_price:.2f} ₽;\n\n'
        info += '🚚 Срок доставки: 25 - 30 дней, в зависимости от вашего города;\n\n'
        # info += '\n'
        info += '❗️ Обратите внимание, что стоимость указана без учета доставки!\n\n'
        info += 'Для окончательного расчета с учетом доставки обратитесь к нашему менеджеру: @arsushkin!'

        # Отправляем информацию в сообщении
        bot.send_message(message.chat.id, info)


    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка при получении курса евро.')

if __name__ == "__main__":
    bot.polling(none_stop=True, timeout=60)