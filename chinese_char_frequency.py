__author__ = 'nga'

# import chinese characters and their frequency percentile from
# http://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO
# to the database

import urllib2
from bs4 import BeautifulSoup
import MySQLdb
import json


def main():
    respond = urllib2.urlopen("http://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO")
    soup = BeautifulSoup(respond.read(), 'html5lib').find('pre').contents
    print soup[10000]

    with open('config.json') as config_file:
        config_data = json.load(config_file)
    host = config_data["db_host"]
    user_name = config_data["db_user_name"]
    password = config_data["db_password"]
    db_name = config_data["db_name"]

    db = MySQLdb.connect(host=host, user=user_name, passwd=password, db=db_name)
    db.set_character_set("utf8")
    cursor = db.cursor()

    for i in range(0, len(soup), 2):
        cols = soup[i].split("\t")
        character = cols[1]
        percentile = cols[3]
        print character, percentile

        cursor.execute("SELECT * FROM frequency WHERE word = %s", character)
        row = cursor.fetchone()
        if not row:  # the character is not in database
            hanviet = look_up_hanviet(character)
            cursor.execute("INSERT INTO frequency (word, hanviet, percentile) VALUES (%s, %s, %s)",
                           (character, hanviet, percentile))
        else:
            cursor.execute("UPDATE frequency SET percentile=%s WHERE word=%s", (percentile, character))
        db.commit()


def look_up_hanviet(character):
    hanviet_search = urllib2.urlopen("http://hanviet.org/hv_timchu.php?unichar=" + character.encode('utf-8'))
    hanviet_html = BeautifulSoup(hanviet_search.read()).find_all("font", attrs={"size": "6", "color": "darkblue"})

    if hanviet_html:
        hanviet_char = hanviet_html[1].get_text().strip()
    else:
        hanviet_char = ""

    print hanviet_html
    return hanviet_char


main()