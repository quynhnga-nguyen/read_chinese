__author__ = 'nga'

# fetch random Chinese articles from wikiapedia
# calculate difficulty level based on individual words in the article
# insert new words, the articles and their statistics into the database

import urllib2
from bs4 import BeautifulSoup
import MySQLdb
import re
import threading
import json


def main():
    threading.Timer(60.0, main).start()

    LOWER_LIMIT = 15

    # fetch a random article on wikipedia
    article_request = urllib2.urlopen("http://zh.wikipedia.org/zh-cn/Special:Random")
    soup = BeautifulSoup(article_request.read())
    content_text = soup.find(id="mw-content-text")

    # connect to the database
    with open('config.json') as config_file:
        config_data = json.load(config_file)
    host = config_data["db_host"]
    user_name = config_data["db_user_name"]
    password = config_data["db_password"]
    db_name = config_data["db_name"]

    db = MySQLdb.connect(host=host, user=user_name, passwd=password, db=db_name)
    db.set_character_set("utf8")
    cursor = db.cursor()

    for paragraph in content_text.find_all('p'):
        text = re.sub("\[\d+\]", '', paragraph.get_text())

        # check if the text already in database
        cursor.execute("SELECT * FROM paragraph WHERE text = %s", text)
        if not cursor.fetchone():
            word_cnt = 0
            percentile_sum = 0.0
            percentile_list = []

            # analyze character frequency
            for character in text:
                # if the character is punctuation or not Chinese, leave out
                # default percentile is 100 (most difficult)
                percentile = get_default_percentile(character)
                if not percentile:
                    continue

                cursor.execute("SELECT percentile FROM frequency WHERE word = %s", character)
                row = cursor.fetchone()
                if row:
                    percentile = row[0]
                else:  # the character not in database yet
                    #frequency = look_up_google(character)
                    hanviet_char = look_up_hanviet(character)

                    # insert the character and its attributes into database
                    cursor.execute(
                        "INSERT INTO frequency (word, hanviet, percentile) VALUES (%s, %s, %s)",
                        (character, hanviet_char, percentile))
                    db.commit()

                percentile_sum += percentile
                word_cnt += 1
                percentile_list.append(percentile)

            if word_cnt < LOWER_LIMIT:
                continue

            # find median of percentiles of characters
            percentile_list.sort()
            size = len(percentile_list)
            median = (percentile_list[size / 2] + percentile_list[(size - 1) / 2]) / 2.0

            # insert the paragraph info into database
            cursor.execute("INSERT INTO paragraph (text, source, wc, avg_percentile, median_percentile) VALUES (%s, %s, %s, %s, %s)",
                           (text, article_request.geturl(), word_cnt, percentile_sum / word_cnt, median))
            db.commit()


def look_up_google(character):
    PUNCTUATION_FREQUENCY = 100000000000

    google_request = urllib2.Request("http://www.google.com/search?hl=en&q=" + character.encode('utf-8'),
                                     headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
                                                            '(KHTML, like Gecko) Chrome/23.0.1271.64 ''Safari/537.11',
                                              'Accept': 'text/html,application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8'})
    google_search = urllib2.urlopen(google_request)
    google_result_stat = BeautifulSoup(google_search.read()).find(id="resultStats")
    if google_result_stat:
        google_stat_text = google_result_stat.get_text()
        frequency = int(re.match("About ([0-9,]*) results", google_stat_text).group(1).replace(',', ''))
    else:  # treat as punctuation
        frequency = PUNCTUATION_FREQUENCY

    return frequency


def look_up_hanviet(character):
    hanviet_search = urllib2.urlopen("http://hanviet.org/hv_timchu.php?unichar=" + character.encode('utf-8'))
    hanviet_html = BeautifulSoup(hanviet_search.read()).find_all("font", attrs={"size": "6", "color": "darkblue"})
    if hanviet_html:
        hanviet = hanviet_html[1].get_text().strip()
    else:
        hanviet = ""

    return hanviet


# returns 0 if the character is not Chinese, else returns 100 (most difficult)
def get_default_percentile(character):
    DEFAULT_LOW_PERCENTILE = 0
    DEFAULT_HIGH_PERCENTILE = 100

    if re.match(re.compile(ur"\p{P}+"), character) or not re.match(re.compile(ur"[\u4e00-\u9fff]"), character):
        defaul_percentile = DEFAULT_LOW_PERCENTILE  # not Chinese character or punctuation
    else:
        defaul_percentile = DEFAULT_HIGH_PERCENTILE

    return defaul_percentile


main()




















