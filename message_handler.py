# -*- coding: utf-8 -*-
import telebot
from googleplaces import GooglePlaces
import speech_recognition as sr
from pydub import AudioSegment
from sqlalchemy import *
from sqlalchemy.orm.exc import *
from sqlalchemy.orm import sessionmaker

import flask
from urllib.request import urlretrieve

import sys
import re
import datetime
import traceback

from log_settings import log
from settings import *
from db_models import BotUser
from telebot.apihelper import FILE_URL

TOKEN = sys.argv[1] if len(sys.argv) > 1 else BOT_KEY

bot = telebot.TeleBot(TOKEN)

google_places = GooglePlaces(GOOGLE_PLACES_API_KEY)

application = app = flask.Flask(__name__)

engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


@app.route('/{}/'.format(TOKEN), methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


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

    radius = list(re.findall(r'РАДІУСІ?\b\s*((?:\d+){0,3})\s?(.*)\s?', message_text))

    radius = radius[0] if radius else radius

    radius_query = 30000

    if radius and len(radius) == 1:
        radius_query = int(radius[0]) if int(radius[0]) <= 50000 else radius_query
    elif len(radius) > 1:
        if radius[1].startswith('КМ') or 'КМ' in radius[1][:5]:
            distance = int(radius[0]) * 1000
            radius_query = distance if distance <= 50000 else radius_query
        else:
            radius_query = int(radius[0]) if int(radius[0]) <= 50000 else radius_query

    photos = list(re.findall(r'І(З|\b\s*ВИВЕДИ)?\b\s*((?:\d+){0,3})\b\s*(ФОТО|ЗОБР)(.*)', message_text))

    photos = photos[0] if photos else photos

    photos_qty = 2 if not photos else int(photos[1])

    query['radius'] = radius_query

    by_name = re.findall(r'"((\w\s?)*)"', message_text)

    error = 0

    if len(by_name) == 1:
        query['name'] = by_name.pop()[0]
        query.pop('types', None)

    elif len(by_name) > 1:
        error = 2

    result = {'query': query, 'photos_qty': photos_qty}
    result.update({'error': error} if error else {})

    return result


def validate_error(error_code):
    message = '' or error_code
    return message


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, HTML_HELP.format(message.chat.first_name, message.chat.last_name),
                     parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    markup.row(telebot.types.KeyboardButton('Надати доступ', request_location=True))
    bot.send_message(message.chat.id, HTML_START, parse_mode='HTML', reply_markup=markup)


@bot.message_handler(commands=['info'])
def info_handler(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    markup.row(telebot.types.KeyboardButton('Надати доступ', request_location=True))
    bot.send_message(message.chat.id, HTML_START, parse_mode='HTML', reply_markup=markup)


@bot.message_handler(content_types=['voice'])
def voices_handler(message):
    file_path = bot.get_file(message.voice.file_id).file_path

    save_path = os.path.join(dir_path, file_path.replace('/', '\\').replace('.oga', 'ogg'))
    new_file = save_path.replace('.ogg', '.wav')

    urlretrieve(FILE_URL.format(TOKEN, file_path), save_path)

    AudioSegment.from_ogg(save_path).export(new_file, format='wav')

    r = sr.Recognizer()

    with sr.AudioFile(new_file) as source:
        audio = r.record(source)
    try:
        msg = r.recognize_google(audio, language='uk-UK')
        message.text = msg
        text_handler(message)
    except sr.UnknownValueError as e:
        bot.send_message(message.chat.id, 'Спробуй повторити ше раз!')
        log(e, status='warning')
    except sr.RequestError as e:
        bot.send_message(message.chat.id, 'Сервіс розпізнавання голосу тимчасоо непрацює!')
        log(e, status='warning')
    except Exception as e:
        log(traceback.format_exc(), status='error')
        log(e, status='error')
    os.remove(save_path)
    return


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
    session.close()

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
        session.close()
    except NoResultFound:
        bot.send_message(message.chat.id, 'Ви не надали доступ до свого місцезнаходження')
        return

    parser = query_parser(message.text)
    if parser.get('error', None) is not None:
        error_message = validate_error(parser['error'])

    query = parser.get('query')
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

        for photo in photos[:parser['photos_qty']]:

            photo.get(maxheight=1000, maxwidth=1000)

            try:
                bot.send_chat_action(message.chat.id, 'upload_photo')
                bot.send_photo(message.chat.id, photo.url, caption=photo.filename)
            except Exception as error:
                print(error)
                continue


if __name__ == "__main__":
    run_bot_time = datetime.datetime.now()
    log((('*' * 18) + '| BOT START TIME|{}|' + ('*' * 18)).format(str(run_bot_time)))
    bot.remove_webhook()
    bot.polling(interval=0, none_stop=True)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', '5000')), debug=True)


