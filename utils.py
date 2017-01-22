import datetime


def get_name_of_file():
    now = str(datetime.datetime.now())
    now = now.split(' ')
    now[1] = '__'.join(now[1].replace(':', '-').split('.'))
    return '#'.join(now)
