from settings import IMAGE_PATH
import datetime
from os import listdir, remove
from os.path import isfile, join


def deleter():
    only_files = [f for f in listdir(IMAGE_PATH) if isfile(join(IMAGE_PATH, f))]
    now = datetime.datetime.now()
    start = str(now.date()) + '#' + str(now.hour - 1)

    delete_counter = 0
    all_files_counter = len(only_files)

    for file in only_files:
        if file.startswith(start):
            remove(IMAGE_PATH + file)
            delete_counter += 1

    print('\nFILES BEFORE DELETING : {}\nFILE DELETED: {}\nNOW FILES QUANTITY: {}'.format(
        all_files_counter, delete_counter, all_files_counter - delete_counter
    ))


if __name__ == "__main__":
    deleter()
