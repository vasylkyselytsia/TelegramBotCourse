# coding:utf8
import os
from googleplaces import types as google_types

BOT_KEY = '255777948:AAHC-Lg1qfkd6XKSRbrGGdqnQ52hFsBt1i0'
GOOGLE_API_KEY = 'AIzaSyAy9cd9ooP5L6bRn5IdkeDrQshGnNduBmE'
GOOGLE_PLACES_API_KEY = 'AIzaSyD43gPXhDr8aQxrSNULQJ9_95RuNc5VNDA'

WEB_HOOK_HOST = 'telegram-bot-search.herokuapp.com'
WEB_HOOK_URL_BASE = "https://%s/%s/" % (WEB_HOOK_HOST, BOT_KEY)


PLACES_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
TEXT_PLACES_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
GET_PHOTO_URL = 'https://maps.googleapis.com/maps/api/place/photo'

DEFAULT_PARAMS = {'language': 'uk', 'radius': 30000}


UK_POPULAR_PLACES = ["Кав'ярні", 'Готелі', 'Кінотеатри',
                     'Нічні клуби', 'Парки', 'Ресторани']

HTML_TAGS = ['b', 'strong', 'i', 'em', 'a', 'code', 'pre']

HTML_HELP = '''
            <strong>Привіт,</strong> <i>{} {}</i>
            <code>Я допоможу Вам знайти поблизу місця, де ви зможете провести свій час!</code>
            '''

HTML_START = '''
             <pre>Для того, щоб почаит користуватись, надайте доступ, для визначення вашого місцезнаходження </pre>
             '''

DB_PATH = 'sqlite:///BotDB'

MESSAGE_FORM = '''
<strong>{},</strong>
<b>Адреса : </b><i>{},</i>
<em>Відкритий зараз: {}.</em>
'''


MY_TYPES = {'Ресторани': google_types.TYPE_RESTAURANT, "Кав'ярні": google_types.TYPE_CAFE,
            'Готелі': google_types.TYPE_ROOM, 'Нічні клуби': google_types.TYPE_NIGHT_CLUB,
            'Кінотеатри': google_types.TYPE_MOVIE_THEATER, 'Парки': google_types.TYPE_PARK,
            'Аптеки': google_types.TYPE_PHARMACY, 'Лікарні': google_types.TYPE_HOSPITAL}

dir_path = os.path.dirname(os.path.realpath(__file__))
IMAGE_PATH = dir_path + '\media\image' + "\\"

PHOTO_TEXT_HTML = '''
<code>Декілька зображень: {}</code>
'''