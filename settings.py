# coding:utf8
import os
from googleplaces import types as google_types

dir_path = os.path.dirname(os.path.realpath(__file__))
IMAGE_PATH = dir_path + '\media\image' + "\\"

BOT_KEY = '255777948:AAHC-Lg1qfkd6XKSRbrGGdqnQ52hFsBt1i0'
GOOGLE_API_KEY = 'AIzaSyAy9cd9ooP5L6bRn5IdkeDrQshGnNduBmE'
GOOGLE_PLACES_API_KEY = 'AIzaSyD43gPXhDr8aQxrSNULQJ9_95RuNc5VNDA'

WEB_HOOK_HOST = 'telegram-bot-search.herokuapp.com'
WEB_HOOK_URL_BASE = "https://%s/%s/" % (WEB_HOOK_HOST, BOT_KEY)


PLACES_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
TEXT_PLACES_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
GET_PHOTO_URL = 'https://maps.googleapis.com/maps/api/place/photo'

DEFAULT_PARAMS = {'language': 'uk', 'radius': 30000}

HTML_TAGS = ['b', 'strong', 'i', 'em', 'a', 'code', 'pre']

HTML_HELP = '''
            <strong>Привіт,</strong> <i>{} {}</i>
            <code>Я допоможу Вам знайти поблизу місця, де ви зможете провести свій час!</code>
            '''

HTML_INFO = '<strong>Інформація, по використанню!</strong>' \
            '<pre>Для коректного пошуку потрібно вводити повідомлення у форматі:</pre>'\
            '<pre>  Тип місця  "[Назва місця]" [У радіусі (радіус пошуку)] [Зображення] [Записи]</pre>' \
            '<em>Назва місця</em>' \
            '<pre>  Вказується в лапках назва конкретного шуканого закладу.</pre>'\
            '<em>Радіус пошуку</em>' \
            '<pre>  Число метрів або кілометрів (у радіусі 50 км(кіломентрів)).</pre>' \
            '<em>Зображення</em>' \
            '<pre>  Кількість фото кожного із знайдених місць для виводу. (із 5 фото, і виведи 5 зображень ).</pre>' \
            '<em>Записи</em>' \
            '<pre>  Кількість результатів для виводу. (Аналогічно до зображень).</pre>'


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
            'Аптеки': google_types.TYPE_PHARMACY, 'Лікарні': google_types.TYPE_HOSPITAL,
            'Кінотеатри': google_types.TYPE_MOVIE_THEATER, 'Парки': google_types.TYPE_PARK,
            'Аеропорти': google_types.TYPE_AIRPORT, 'Парки розваг': google_types.TYPE_AMUSEMENT_PARK,
            'Галереї мистецтв': google_types.TYPE_ART_GALLERY, 'Банкомати': google_types.TYPE_ATM,
            'Пекарні': google_types.TYPE_BAKERY, 'Банки': google_types.TYPE_BANK,
            'Бари': google_types.TYPE_BAR, 'Салони краси': google_types.TYPE_BEAUTY_SALON,
            'Книгарні': google_types.TYPE_BOOK_STORE, 'Автобусні зупинки': google_types.TYPE_BUS_STATION,
            'Спортзали': google_types.TYPE_GYM, 'Магазини побутової техніки': google_types.TYPE_HARDWARE_STORE,
            }

PHOTO_TEXT_HTML = '<code>Декілька зображень: {}</code>'
