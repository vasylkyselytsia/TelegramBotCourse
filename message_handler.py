# -*- coding: utf-8 -*-
import telebot
from sqlalchemy import *
from sqlalchemy.orm.exc import *
from sqlalchemy.orm import sessionmaker
from settings import *
from db_models import BotUser
from googleplaces import GooglePlaces
import time
from urllib.request import urlretrieve
from utils import get_name_of_file


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
    query['types'] = []

    keys = MY_TYPES.keys()

    for key in keys:
        if key.upper() in message_text:
            query['types'].append(MY_TYPES[key])

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
        *MY_TYPES.keys(), row_width=3, row_qty=2, col_qty=3, request_location=False))


@bot.message_handler(content_types=['text'])
def text_handler(message):

    session = Session()
    # bot.get_user_profile_photos()
    try:
        user = session.query(BotUser).filter(
            BotUser.chat_id == int(message.chat.id),
            BotUser.user_name == message.chat.first_name + ' ' + message.chat.last_name
        ).one()

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
                    file_path = IMAGE_PATH + '{}.jpg'.format(get_name_of_file())
                    urlretrieve(photo.url, file_path)
                    new_photo = open(file_path, 'rb')
                    bot.send_photo(message.chat.id, new_photo, caption=photo.filename)
                    new_photo.close()
                except Exception as e:
                    print(e)
                    continue

    except NoResultFound:
        bot.send_message(message.chat.id, 'Ви не надали доступ до свого місцезнаходження')


def main():
    try:
        bot.polling(none_stop=True, interval=0)
        time.sleep(0)
    except Exception as e:
        print(e)
        main()

if __name__ == "__main__":
    main()
