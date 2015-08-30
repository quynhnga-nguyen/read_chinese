__author__ = 'nga'

# calculate and insert median difficulty level of the articles in the database

import MySQLdb
import json


def main():
    with open('config.json') as config_file:
        config_data = json.load(config_file)
    host = config_data["db_host"]
    user_name = config_data["db_user_name"]
    password = config_data["db_password"]
    db_name = config_data["db_name"]

    db = MySQLdb.connect(host=host, user=user_name, passwd=password, db=db_name)
    db.set_character_set("utf8")
    cursor = db.cursor()


    QUERY = "SELECT id, text FROM paragraph WHERE median_percentile IS NULL LIMIT %s"
    BATCH_SIZE = 20

    while True:
        cursor.execute(QUERY, BATCH_SIZE)
        rows = cursor.fetchall()
        if not rows:
            break

        for row in rows:
            percentile_list = []
            para_id = row[0]
            text = row[1].decode('utf-8')

            for character in text:
                cursor.execute("SELECT percentile FROM frequency WHERE word = %s", character)
                char_row = cursor.fetchone()
                #print character, char_row
                if char_row:
                    percentile_list.append(char_row[0])

            # calculate median
            percentile_list.sort()
            size = len(percentile_list)
            if size > 0:
                median = (percentile_list[size / 2] + percentile_list[(size - 1) / 2]) / 2.0
            else:
                median = -1

            print median, para_id
            # update database
            cursor.execute("UPDATE paragraph SET median_percentile=%s WHERE id=%s", (median, para_id))
            db.commit()


main()