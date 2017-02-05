# -*- coding: utf-8 -*-
import telebot
from sqlalchemy import *
from sqlalchemy.orm.exc import *
from sqlalchemy.orm import sessionmaker
from settings import *
from db_models import BotUser
from googleplaces import GooglePlaces
import sys
import re
from log_settings import logger
import datetime

TOKEN = sys.argv[1] if len(sys.argv) > 1 else BOT_KEY

bot = telebot.TeleBot(TOKEN)
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

google_places = GooglePlaces(GOOGLE_PLACES_API_KEY)


def create_buttons_group(*args, **kwargs):

    def chunks(l, n):
        """Генератор який розбиває LIST на відповідну кількість частин"""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    row_width = kwargs.get('row_width', 2)
    col_qty = kwargs.get('col_qty', 3)
    request_location = kwargs.get('request_location', True)
    one_time_keyboard = kwargs.get('one_time_keyboard', True)

    markup = telebot.types.ReplyKeyboardMarkup(row_width=row_width, one_time_keyboard=one_time_keyboard)

    buttons = chunks(args, col_qty)

    for row in buttons:
        markup.row(*[telebot.types.KeyboardButton(button, request_location=request_location) for button in row])

    return markup


def query_parser(message_text):
    query = DEFAULT_PARAMS.copy()
    message_text = message_text.upper()
    query['types'] = []

    keys = MY_TYPES.keys()

    for key in keys:
        if key.upper()[:-2] in message_text:  # [:-2] Щоб відкинути закінчення
            query['types'].append(MY_TYPES[key])

    # digests = re.findall(r'([0-9]{1,4})', message_text)  # Пошук Цифер у Строці

    radius = list(set(re.findall(r'РАДІУСІ\b\s*((?:\d+){0,3})', message_text)) | set(
                      re.findall(r'РАДІУС\b\s*((?:\d+){0,3})', message_text)))

    query['radius'] = int(radius[0]) if radius else 30000  # Якщо в повідомленні є радіус то задаємо, інакше 1000 м

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
def get_new_location_handler(message):
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
        *MY_TYPES.keys(), row_width=3, col_qty=2, request_location=False))


@bot.message_handler(content_types=['text'])
def text_handler(message):

    session = Session()
    try:
        user = session.query(BotUser).filter(
            BotUser.chat_id == int(message.chat.id),
            BotUser.user_name == message.chat.first_name + ' ' + message.chat.last_name
        ).one()
    except NoResultFound:
        bot.send_message(message.chat.id, 'Ви не надали доступ до свого місцезнаходження')
        return

    query = query_parser(message.text)
    query['location'] = ','.join(map(str, [user.latitude, user.longitude]))

    places_result = google_places.nearby_search(**query)

    if not places_result.places:
        bot.send_message(message.chat.id, 'За вашим запитом нічого не знайдено')
        return

    for place in places_result.places[:2]:
        place.get_details()
        location = place.geo_location

        message_text = MESSAGE_FORM.format(
            place.name, place.formatted_address,
            'Так' if place.details.get('opening_hours', {}).get('open_now', False) else 'Ні')

        if place.website:
            message_text += '<a href="{}">Website  {}</a>'.format(place.website, place.name)

        bot.send_message(message.chat.id, message_text, parse_mode='HTML')

        if location:
            bot.send_location(message.chat.id, location.get('lat'), location.get('lng'))

        photos = [photo for photo in place.photos]  # In Python 3 Map objects to List

        if not photos:
            continue

        bot.send_message(message.chat.id, PHOTO_TEXT_HTML.format(place.name), parse_mode='HTML')

        for photo in photos[:2]:

            photo.get(maxheight=1000, maxwidth=1000)

            try:
                bot.send_chat_action(message.chat.id, 'upload_photo')
                bot.send_photo(message.chat.id, photo.url, caption=photo.filename)
            except Exception as error:
                print(error)
                continue


if __name__ == "__main__":
    try:
        run_bot_time = datetime.datetime.now()
        logger.info('-' * 100)
        logger.info((('*' * 28) + '| BOT START TIME|{}|' + ('*' * 28)).format(
            str(run_bot_time)))
        logger.info('-' * 100)
        # bot.remove_webhook()
        # bot.polling(none_stop=True)
        bot.set_webhook('https://telegram-bot-search.herokuapp.com/')
    except Exception as e:
        print(e)

