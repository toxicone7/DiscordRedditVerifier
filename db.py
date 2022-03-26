import _sqlite3
import datetime


def insert(user_id, reddit_user, action, actionBy):
    flag = False
    try:
        conn = _sqlite3.connect('logs.db')
        c = conn.cursor()
    except Exception as e:
        print("Error while trying to connect to the database.")
        print(e)

    try:
        date = datetime.date.today()
        date = date.strftime("%Y-%m-%d")
        c.execute('INSERT INTO logs VALUES (?,?,?,?,?)',
                  (user_id, reddit_user, date, action, actionBy))
        conn.commit()

        print(
            "Successfully added Reddit user: '{}' with Discord ID: '{}' to the database.".format(reddit_user, user_id))
        flag = True
    except Exception as e:
        print("Error while inserting Reddit user: '{}' with Discord ID: '{}' to the database.".format(reddit_user,
                                                                                                      user_id))
        print(e)
    finally:
        c.close()
        conn.close()
        return flag


def insert_with_date(user_id, reddit_user, date, action, actionBy):
    flag = False
    try:
        conn = _sqlite3.connect('logs.db')
        c = conn.cursor()
    except Exception as e:
        print("Error while trying to connect to the database.")
        print(e)

    try:
        # DATE NEEDS TO BE IN FORMAT YEAR-MONTH-DAY
        c.execute('INSERT INTO logs VALUES (?,?,?,?,?)',
                  (user_id, reddit_user, date, action, actionBy))
        conn.commit()

        print(
            "Successfully added Reddit user: '{}' with Discord ID: '{}' to the database.".format(reddit_user, user_id))
        flag = True
    except Exception as e:
        print("Error while inserting Reddit user: '{}' with Discord ID: '{}' to the database.".format(reddit_user,
                                                                                                      user_id))
        print(e)
    finally:
        c.close()
        conn.close()
        return flag


def is_duplicate(redditUsername):
    flag = None
    try:
        conn = _sqlite3.connect('logs.db')
        c = conn.cursor()
    except Exception as e:
        print("Error while trying to connect to the database.")
        print(e)

    try:
        c.execute('SELECT id FROM logs WHERE redditUsername = (?)', (redditUsername,))
        id = c.fetchall()
        if id:
            print("Reddit user: '{}' is already in the server with a user id: '{}' ".format(redditUsername, id[0][0]))
            flag = True
            return flag
        else:
            print("Reddit user: '{}' doesn't exist. Inserting into to the database.".format(redditUsername))
            flag = False
            return flag
            #insert into db
    except Exception as e:
        print("ERROR")
        print(e)
    finally:
        c.close()
        conn.close()
        return flag


# insert('253119392789954561', 'fudaru', 'Verified', 'toxicone7')

#is_duplicate('toxicone7')
