# -*- coding: utf-8 -*-
import telebot
from sqlalchemy import *
from sqlalchemy.orm.exc import *
from sqlalchemy.orm import sessionmaker
from settings import *
from db_models import BotUser
import requests
from googleplaces import GooglePlaces, types, lang

bot = telebot.TeleBot(BOT_KEY)
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

google_places = GooglePlaces(GOOGLE_PLACES_API_KEY)


def create_buttons_group(*args, **kwargs):
    row_width = kwargs.get('row_width', 2)
    row_qty = kwargs.get('row_qty', 1)
    col_qty = kwargs.get('col_qty', 3)
    request_location = kwargs.get('request_location', True)
    one_time_keyboard = kwargs.get('one_time_keyboard', True)

    markup = telebot.types.ReplyKeyboardMarkup(row_width=row_width, one_time_keyboard=one_time_keyboard)
    start_slice = 0

    for row in range(row_qty):
        buttons_list = []

        for button in args[start_slice:col_qty]:
            buttons_list.append(telebot.types.KeyboardButton(button, request_location=request_location))

        markup.row(*buttons_list)
        start_slice += col_qty
        col_qty += col_qty

    return markup


def query_parser(message_text):
    query = DEFAULT_PARAMS.copy()
    message_text = message_text.upper()

    if 'РЕСТОР' in message_text:
        query['type'] = 'restaurant'

    # if u'РЕСТОР' in message_text:
    #     query['type'] = 'restaurant'

    # if set(message_text.split()) & {u'РАДІУС', u'РАДІУСІ'}:
    #     return message_text
    return query


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, HTML_HELP.format(message.chat.first_name, message.chat.last_name),
                     parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    markup.row(telebot.types.KeyboardButton('Надати доступ', request_location=True))
    bot.send_message(message.chat.id, HTML_START, parse_mode='HTML', reply_markup=markup)


@bot.message_handler(content_types=['location'])
def search_handler(message):
    # Add coordinate To DB
    session = Session()
    try:
        user = session.query(BotUser).filter(BotUser.chat_id == message.chat.id).one()
        user.longitude = message.location.longitude
        user.latitude = message.location.latitude
    except NoResultFound:
        session.add(BotUser(
            chat_id=message.chat.id, longitude=message.location.longitude, latitude=message.location.latitude,
            user_name=message.chat.first_name + ' ' + message.chat.last_name))

    session.commit()

    bot.send_message(message.chat.id, 'Виберіть що ви шукаєте', reply_markup=create_buttons_group(
        *UK_POPULAR_PLACES, row_width=3, row_qty=2, col_qty=3, request_location=False))


@bot.message_handler(content_types=['text'])
def text_handler(message):

    session = Session()

    try:
        user = session.query(BotUser).filter(
            BotUser.chat_id == int(message.chat.id),
            BotUser.user_name == message.chat.first_name + ' ' + message.chat.last_name
        ).one()

        query = query_parser(message.text)
        query['location'] = ','.join(map(str, [user.latitude, user.longitude]))
        response = requests.get(TEXT_PLACES_SEARCH_URL, query)

        if response.status_code != 200:
            bot.send_message(message.chat.id, u'Виникла помилка при доступі до Google Maps')
            return

        status = response.json().get('status')

        if status not in ['OK', 'ZERO_RESULTS']:
            bot.send_message(message.chat.id, u'Виникла помилка при доступі до Google Maps')
            return

        if status == 'ZERO_RESULTS':
            bot.send_message(message.chat.id, u'За вашим запитом нічого не знайдено')
            return
        # MESSAGE_FORM
        result = response.json().get('results')[1]
        location = result.get('geometry', {}).get('location', None)

        if location:
            bot.send_location(message.chat.id, location.get('lat'), location.get('lng'))

        bot.send_message(message.chat.id, MESSAGE_FORM.format(
            result.get('name', ''), result.get('formatted_address', ''),
            'Так' if result.get('opening_hours', {}).get('open_now', False) else 'Ні'),  parse_mode='HTML')

        bot.send_message(message.chat.id, str(query))

    except NoResultFound:
        bot.send_message(message.chat.id, u'Ви не дали доступ до свого місцезнаходження')

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
