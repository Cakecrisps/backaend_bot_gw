import sqlite3
import base64
import random
import time
import json
import ast
import requests
import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.environ['BOT_TOKEN']

db = sqlite3.connect("data.db")
cursor = db.cursor()
sql = cursor

#referrers - можно чем то заменить. Написал функцию referrers_get_count, которая делает этот параметр ненужным в бд

sql.execute("""CREATE TABLE IF NOT EXISTS users(
       user_id INT,
       username TEXT,
       tokens FLOAT,
       coins FLOAT,
       tickets INT,
       place TEXT,
       lang TEXT,
       room_id INT,
       collectibles TEXT,
       active_skin INT,
       daily_get INT,
       referrer_id INT,
       referrer_coins TEXT,
       referrer_all_coins FLOAT,
       days_online INT,
       active INT,
       last_time INT,
       last_active_mess_id INT,
       want_to_buy FLOAT,
       want_to_sell FLOAT,
       want_to_send FLOAT,
       daily_withdraws INT,
       last_time_download_pic INT,
       all_games INT,
       wins INT,
       loses INT,
       tokenwins FLOAT,
       tokenloses FLOAT,
       coinwins FLOAT,
       coinloses FLOAT,
       publicname TEXT,
       wallet_id TEXT,
       tosend_wallet_id TEXT,
       ban INT,
       pic_profile BLOB,
       pic_custom BLOB,
       pic_temp_avatar BLOB,
       pic_temp_settings BLOB,
       energy INT,
       energy_drinks INT,
       exp INT,
       active_emoji INT,
       leaderboard_count FLOAT);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS collectibles(
       item_id INT,
       item_type TEXT,
       item_pic BLOB,
       item_mask BLOB,
       item_pic_preview BLOB,
       item_mask_preview BLOB,
       item_price FLOAT,
       item_price_tokens FLOAT,
       item_count INT);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS emojies(
       pack_id INT,
       laughter BLOB,
       crying BLOB,
       hello BLOB,
       thumbs_up BLOB,
       cool BLOB,
       mockery BLOB,
       tongue BLOB,
       click BLOB,
       victory BLOB,
       surprise BLOB,
       contempt BLOB,
       angry BLOB,
       pack_name TEXT);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS daily_bonus(
       day INT,
       type TEXT,
       item_id INT,
       count INT);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS shop_available(
       item_id INT);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS ad_banners(
       banner_id INTEGER,
       pic_ru BLOB,
       pic_en BLOB,
       text_1_ru TEXT,
       text_1_en TEXT,
       text_2_ru TEXT,
       text_2_en TEXT,
       button_type TEXT,
       button_text_ru TEXT,
       button_text_en TEXT);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS lavka(
       nft_id INTEGER,
       item_id INTEGER,
       seller_id INTEGER,
       price INTEGER);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS nft(
       nft_id INTEGER,
       skin_id INTEGER,
       owner_id INTEGER,
       history TEXT);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS rooms_rps(
       creator_id INTEGER,
       in_room TEXT,
       bet REAL,
       players_count INTEGER,
       room_type INTEGER,
       free_places INTEGER,
       bet_type INTEGER,
       room_id INTEGER);
    """)

sql.execute("""CREATE TABLE IF NOT EXISTS whitelist(
       user_id INTEGER,
       username TEXT,
       date INTEGER,
       approved INTEGER);
    """)

#sql.execute("""INSERT INTO shop_available(item_id) VALUES (14), (15), (16), (17), (18), (19), (20);""")

db.commit()
db.close()

#dbn = "users"
dbn = "data"

async def message_to_telegram(user_id: int, mess: str):
    # Endpoint для отправки сообщений
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    # Формируем тело запроса
    payload = {
        'chat_id': str(user_id),
        'text': mess,
        'parse_mode': 'HTML'
    }

    # Делаем POST-запрос
    response = requests.post(url, json=payload)

    # Выводим ответ сервера
    print(response.text)

async def load_user_data(user_id: int, server: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        if server == 0:
            query = f"SELECT * FROM users WHERE user_id=?"
            cursor.execute(query, (user_id,))
            user_db = cursor.fetchone()  # Предполагаем, что id пользователя уникальный
            return user_db
            # for i in cursor.execute(f"SELECT * FROM users WHERE user_id = '{user_id}'"):
            #     user_db = i
            #     return user_db
        elif server == 1:
            cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_db = cursor.fetchone()

            if user_db:
                user_tokens = float(user_db[2])
                if user_tokens % 1 == 0:
                    user_tokens = int(user_tokens)
                else:
                    user_tokens = round(user_tokens, 2)

                user_coins = float(user_db[3])
                if user_coins % 1 == 0:
                    user_coins = int(user_coins)
                else:
                    user_coins = round(user_coins, 2)

                user_collectibles = str(user_db[8])
                user_collectibles = ast.literal_eval(user_collectibles)
                user_collectibles_list = list(user_collectibles.keys())
                # Convert the tuple to a dictionary for JSON serialization
                user_dict = {
                    "username": user_db[1],
                    "tokens": user_tokens,
                    "coins": user_coins,
                    "tickets": user_db[4],
                    "lang": user_db[6],
                    "room_id": user_db[7],
                    "collectibles": user_collectibles_list,
                    "active_skin": user_db[9],
                    "referrer_id": user_db[11],
                    "referrer_coins": user_db[12],
                    "referrer_all_coins": user_db[13],
                    "days_online": user_db[14],
                    "all_games_played_count": user_db[23],
                    "wins": user_db[24],
                    "loses": user_db[25],
                    "tokenwins": user_db[26],
                    "tokenloses": user_db[27],
                    "coinwins": user_db[28],
                    "coinloses": user_db[29],
                    "publicname": user_db[30],
                    "if_ban": user_db[33],
                    "user_energy": user_db[38],
                    "user_energy_drinks": user_db[39],
                    "user_exp": user_db[40],
                    "user_active_emoji": user_db[41],
                    "user_leaderboard_count": user_db[42],
                }
                return user_dict
            else:
                return "User not found"
        elif server == 2:
            cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_db = cursor.fetchone()

            if user_db:
                try:
                    #pic_profile = encode_image_to_base64(user_db[34])
                    pic_profile = user_db[34]
                except:
                    pic_profile = None
                try:
                    #pic_custom = encode_image_to_base64(user_db[35])
                    pic_custom = user_db[35]
                except:
                    pic_custom = None
                if pic_custom == "" or pic_custom == None:
                    if pic_profile == None:
                        pic = None
                        pic_type = None
                    else:
                        pic = pic_profile
                        pic_type = "pic_profile"
                else:
                    pic = pic_custom
                    pic_type = "pic_custom"

                #return pic_type + "/" + pic
                return pic
            else:
                return "User not found"
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        db.close()  # Закрываем соединение в блоке finally

async def register_new_user(user_id: int, user_username: str, new_tokens: float, new_coins: float, new_tickets: int, new_place: str, new_lang: str, new_room_id: int, new_collectibles: str, user_active_skin: int, referrers: int, referrer_id: int, new_referrer_coins: str, new_referrer_all_coins: float, new_days_online: int, new_active: int, new_last_time: int, last_active_mess_id: int, new_want_to_buy: float, new_want_to_sell: float, want_to_send: float, user_daily_withdraws: int, user_last_time_download_pic: int, user_all_games_played_count: int, user_wins: int, user_loses: int, user_tokenwins: float, user_tokenloses: float, user_coinwins: float, user_coinloses: float, user_publicname: str, user_wallet_id: str, user_tosend_wallet_id: str, user_ban: str, pic_profile: bytes, pic_custom: bytes, pic_temp_avatar: bytes, pic_temp_settings: bytes, user_energy: int, user_energy_drinks: int, user_exp: int, user_active_emoji: int, leaderboard_count: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'")
        if cursor.fetchone() is None:
            cursor.execute(
                f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    user_id, user_username, new_tokens, new_coins, new_tickets, new_place, new_lang, new_room_id,
                    new_collectibles, user_active_skin, referrers, referrer_id, new_referrer_coins,
                    new_referrer_all_coins, new_days_online, new_active, new_last_time, last_active_mess_id,
                    new_want_to_buy, new_want_to_sell, want_to_send, user_daily_withdraws, user_last_time_download_pic,
                    user_all_games_played_count, user_wins, user_loses, user_tokenwins, user_tokenloses, user_coinwins,
                    user_coinloses, user_publicname, user_wallet_id, user_tosend_wallet_id, user_ban, pic_profile, pic_custom, pic_temp_avatar, pic_temp_settings,
                    user_energy, user_energy_drinks, user_exp, user_active_emoji, leaderboard_count))
            db.commit()

        else:
            pass
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        db.close()  # Закрываем соединение в блоке finally

async def nft_create(user_id: int, nft_id: str, skin_id: str, cost: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        if skin_id == "1":
            return "ok"

        cursor.execute(f"SELECT nft_id FROM nft WHERE nft_id = '{nft_id}'")
        if cursor.fetchone() is None:
            unix_time = int(time.time())

            new_history_dict = {}
            next_transaction_number = len(new_history_dict) + 1
            new_history_dict[next_transaction_number] = {
                'transaction_time': str(unix_time),
                'owner_id': str(user_id),
                'price': str(cost)
            }
            new_history = str(new_history_dict)
            #new_history = json.dumps(new_history_dict)
            cursor.execute(f"INSERT INTO nft VALUES (?, ?, ?, ?)", (nft_id, skin_id, user_id, new_history))
            db.commit()
            return "ok"
        else:
            return "error"
    except:
        return "error"

async def get_translate_key(key, lang):
    try:
        # Используйте context manager для управления соединением
        with sqlite3.connect(f"{dbn}.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT translation FROM langs WHERE key=? AND locale=?", (key, lang))
            translate = cursor.fetchone()
            # Извлекаем перевод из кортежа
            return translate[0] if translate else None
    except Exception as e:  # отлавливаем оставшиеся исключения
        print("langs error:", e)
        return "error"
    finally:
        if db:
            db.close()


async def get_translate_type(type, locale):
    # Соединение с базой данных
    db = sqlite3.connect(f"{dbn}.db")
    cursor = db.cursor()

    # Подготовка SQL запроса
    query = 'SELECT key, translation FROM langs WHERE type=? AND locale=?'

    # Выполнение запроса
    cursor.execute(query, (type, locale))

    # Создание словаря с переводами
    translations = {key: translation for key, translation in cursor.fetchall()}

    # Закрытие соединения с базой данных
    cursor.close()

    return translations

async def get_nft_info(nft_id):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM nft WHERE nft_id = '{nft_id}'")
        nft_info = cursor.fetchone()
        if nft_info:
            return nft_info
    except:
        return "error"

async def count_total_users():
    db = sqlite3.connect(f"{dbn}.db")
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM users;")
    all_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE active IN (1, 3);")
    active_users = cursor.fetchone()[0]
    return all_users, active_users

async def rassilka_progon():
    db = sqlite3.connect(f"{dbn}.db")
    cursor = db.cursor()

    progon = cursor.execute(f"SELECT user_id, lang, ban FROM users")

    return progon

async def get_user_id_from_username(user_name: str):
    db = sqlite3.connect(f"{dbn}.db")
    cursor = db.cursor()
    for i in cursor.execute(f"SELECT * FROM users WHERE lower(username) = ? ", (user_name.lower(),)):
        user_db_his = i
        user_id_his = user_db_his[0]
        return user_id_his

async def new_place(user_id: int, new_place: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET place = "{new_place}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_lang(user_id: int, new_lang: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET lang = "{new_lang}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_last_active_mess_id(user_id: int, new_mess_id: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET last_active_mess_id = "{new_mess_id}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_want_to_buy(user_id: int, new_want_to_buy: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET want_to_buy = "{new_want_to_buy}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_want_to_sell(user_id: int, new_want_to_sell: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET want_to_sell = "{new_want_to_sell}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_want_to_send(user_id: int, new_want_to_send: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET want_to_send = "{new_want_to_send}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_send_to_wallet_id(user_id: int, new_send_to_wallet_id: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET tosend_wallet_id = "{new_send_to_wallet_id}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_coins(user_id: int, new_coins: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET coins = "{new_coins}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_tokens(user_id: int, new_tokens: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET tokens = "{new_tokens}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_tickets(user_id: int, new_tickets: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET tickets = "{new_tickets}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def add_refs_coins_count(user_id: int, stavka: float):    #Сюда отправляется вся сумма ставки. Процент высчитывается сам. Возвращает ставку уже после вычета комиссии пригласившему
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))  # Используем placeholder
        result = cursor.fetchone()
        if result:
            user_referrer_id = int(result[0])
            if user_referrer_id == None or str(user_referrer_id) == "":
                return stavka
            else:
                if user_referrer_id:
                    add_refs_coins = round(stavka * 0.01, 3)
                    stavka -= add_refs_coins
                    try:
                        # Загрузка текущего значения friend_referrer_coins
                        cursor.execute("SELECT referrer_coins, referrer_all_coins FROM users WHERE user_id = ?", (user_referrer_id,))
                        result = cursor.fetchone()

                        if result:
                            friend_referrer_coins = json.loads(result[0]) if result and result[0] else {}
                            friend_referrer_all_coins = float(result[1])
                        else:
                            friend_referrer_coins = {}
                            friend_referrer_all_coins = float(0.0)

                        # Преобразование user_id в строку для использования в качестве ключа JSON
                        user_id_str = str(user_id)

                        # Проверка существования ключа, если да - инкрементирование, если нет - установка
                        if user_id_str in friend_referrer_coins:
                            friend_referrer_coins[user_id_str] += add_refs_coins
                        else:
                            friend_referrer_coins[user_id_str] = add_refs_coins

                        # print(friend_referrer_coins)  # Для отладки
                        friend_referrer_coins_json = json.dumps(friend_referrer_coins)

                        friend_referrer_all_coins += add_refs_coins

                        # Используем параметризованный запрос
                        cursor.execute("UPDATE users SET referrer_coins = ? WHERE user_id = ?", (friend_referrer_coins_json, user_referrer_id))
                        cursor.execute("UPDATE users SET referrer_all_coins = ? WHERE user_id = ?", (friend_referrer_all_coins, user_referrer_id))
                        db.commit()  # Не забываем подтвердить изменения в базе

                        return stavka
                    except Exception as e:
                        print(f"Ошибка: {e}")
                        return stavka
        else:
            return stavka
    except Exception as e:
        print(f"Ошибка: {e}")
        return stavka
    finally:
        db.close()

async def get_refs_info(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        with open('web_url.json', 'r', encoding='utf-8') as f:
            web_link = json.load(f)

        # Загрузка текущего значения friend_referrer_coins
        cursor.execute("SELECT referrer_coins FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        user_referrer_coins = json.loads(result[0]) if result and result[0] else {}

        ####### ПОДКЛЮЧЕНИЕ ВСЕХ ДРУЗЕЙ СЮДА В СПИСОК
        # Ваш SQL-запрос для получения друзей пользователей
        cursor.execute("SELECT user_id FROM users WHERE referrer_id = ?", (user_id,))
        friends = cursor.fetchall()  # Получаем всех друзей пользователя

        # Теперь обновляем user_referrer_coins
        for friend in friends:
            friend_id = friend[0]  # предполагаем, что friend имеет структуру (user_id,)
            if str(friend_id) not in user_referrer_coins:
                # Если друг не в словаре, добавляем его с 0.0 токенов
                user_referrer_coins[str(friend_id)] = 0.0
        ####### ПОДКЛЮЧЕНИЕ ВСЕХ ДРУЗЕЙ СЮДА В СПИСОК

        if user_referrer_coins == {}:
            refs_info = []
            result_data = {
                'refs_info': refs_info,
                'total_balance': 0
            }
            return result_data

        user_ids_str = ','.join(
            '?' for _ in user_referrer_coins.keys())  # Создаем строку с плейсхолдерами для IN оператора
        query = f"""
            SELECT user_id, publicname, active_skin
            FROM users
            WHERE user_id IN ({user_ids_str})
            """
        cursor.execute(query, tuple(user_referrer_coins.keys()))
        users_info = cursor.fetchall()

        refs_info = []
        for user_id, public_name, active_skin in users_info:
            photo_url = web_link["url"] + "/avatar/" + str(user_id)

            #skin_info = await load_item_data(active_skin, 0)

            item_pic = web_link["url"] + "/get_item_image/" + str(active_skin)
            item_mask = web_link["url"] + "/get_item_image_mask/" + str(active_skin)
            refs_info.append({
                'user_id': str(user_id),
                'coins': user_referrer_coins[str(user_id)],
                'public_name': public_name,
                'avatar': photo_url,
                'item_pic': item_pic,
                'item_mask': item_mask
            })

        refs_info.sort(key=lambda x: float(x['coins']) if float(x['coins']) != 0.0 else float('-inf'), reverse=True)

        # Инициализируем переменную для хранения общего баланса
        total_balance = sum(user_referrer_coins.values())
        total_balance = round(total_balance, 3)

        # Изменяем структуру result_data для соответствия формату вывода
        result_data = {
            'refs_info': refs_info,
            'total_balance': total_balance
        }
        return result_data

    except Exception as e:
        print(f"Ошибка: {e}")
        return {'error': "An error occurred"}
    finally:
        if db:
            db.close()

async def transfer_refs_to_balance(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        user_coins = float(result[3])
        user_referrer_coins = json.loads(result[12]) if result and result[0] else {}

        if user_referrer_coins == {}:
            total_balance = 0
            return user_coins, total_balance
        else:
            # Инициализируем переменную для хранения общего баланса
            total_balance = sum(user_referrer_coins.values())
            print(str(total_balance))
            if float(total_balance) < 0.1:
                return user_coins, "small"
            else:

                user_coins += float(total_balance)

                new_referrer_coins_dict = {}
                new_referrer_coins = json.dumps(new_referrer_coins_dict)

                # Используем параметризованный запрос
                cursor.execute("UPDATE users SET referrer_coins = ? WHERE user_id = ?",
                               (new_referrer_coins, user_id))
                cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?",
                               (user_coins, user_id))
                db.commit()  # Не забываем подтвердить изменения в базе

                return user_coins, total_balance

    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def add_leaderboard_count(user_id: int, add_leaderboard_count: float):    #   Добавление для подсчета лидера недели
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT leaderboard_count FROM users WHERE user_id = {user_id}")
        user_leaderboard_count = int(cursor.fetchone()[0])
        if user_leaderboard_count:
            try:
                user_leaderboard_count += add_leaderboard_count

                cursor.execute((f'UPDATE users SET leaderboard_count = "{user_leaderboard_count}" WHERE user_id = "{user_id}"'))
                db.commit()

                return "ok"
            except:
                return "error"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def get_leaderboard_top_users():   #Подсчет топ 100 игроков для Таблицы лидеров
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        with open('web_url.json', 'r', encoding='utf-8') as f:
            web_link = json.load(f)

        # Выполнение запроса на выборку топ-100 пользователей
        # cursor.execute("""
        # SELECT user_id, leaderboard_count FROM users
        # ORDER BY leaderboard_count DESC
        # LIMIT 100
        # """)

        # Выполнение запроса на выборку топ-100 пользователей с дополнительными полями
        cursor.execute("""
            SELECT user_id, leaderboard_count, active_skin, publicname FROM users
            WHERE leaderboard_count IS NOT NULL AND leaderboard_count > 0
            ORDER BY leaderboard_count DESC
            LIMIT 100
            """)

        # Получаем все результаты запроса
        top_users = cursor.fetchall()

        # Закрытие соединения с базой данных
        db.close()

        top_users_list = []

        # Преобразование результатов в список словарей
        for user in top_users:

            photo_url = web_link["url"] + "/avatar/" + str(user[0])
            item_pic = web_link["url"] + "/get_item_image/" + str(user[2])
            item_mask = web_link["url"] + "/get_item_image_mask/" + str(user[2])

            # Словарь с информацией о пользователе
            user_info = {
                "user_id": user[0],
                "coins": user[1],
                "public_name": user[3],
                "avatar": photo_url,
                "item_pic": item_pic,
                "item_mask": item_mask
            }

            top_users_list.append(user_info)  # Добавляем элемент в список
            # photo_url = web_link["url"] + "/avatar/" + str(user[0])
            #
            # item_pic = web_link["url"] + "/get_item_image/" + str(user[2])
            # item_mask = web_link["url"] + "/get_item_image_mask/" + str(user[2])
            #
            # top_users_list = [{"user_id": user[0], "coins": user[1], "public_name": user[3], "avatar": photo_url, "item_pic": item_pic, "item_mask": item_mask}]
            # #top_users_list = [{"user_id": user[0], "count": user[1]} for user in top_users]

        result_data = {
            'top_users_list': top_users_list
        }

        return top_users_list
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"

async def new_room_id(user_id: int, new_room_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET room_id = "{new_room_id}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_collectibles(user_id: int, new_collectibles: str, count: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_db = cursor.fetchone()
        if user_db:
            try:
                if new_collectibles == 21:    #Энергетик
                    user_energy_drinks = int(user_db[39])
                    user_energy_drinks += int(count)

                    cursor.execute((f'UPDATE users SET energy_drinks = "{user_energy_drinks}" WHERE user_id = "{user_id}"'))
                    db.commit()

                    return str(user_energy_drinks)
                elif new_collectibles == 22:    #Билеты
                    user_tickets = int(user_db[4])
                    user_tickets += int(count)

                    cursor.execute((f'UPDATE users SET tickets = "{user_tickets}" WHERE user_id = "{user_id}"'))
                    db.commit()

                    return str(user_tickets)
                elif new_collectibles == 23:  #Щитки
                    user_tokens = float(user_db[2])
                    user_tokens += float(count)

                    cursor.execute((f'UPDATE users SET tokens = "{user_tokens}" WHERE user_id = "{user_id}"'))
                    db.commit()

                    return str(user_tokens)
                elif new_collectibles == 24:  #Опыт
                    user_exp = int(user_db[40])
                    user_exp += int(count)

                    cursor.execute((f'UPDATE users SET exp = "{user_exp}" WHERE user_id = "{user_id}"'))
                    db.commit()

                    return str(user_exp)
                else:

                    user_collectibles = str(user_db[8])

                    user_collectibles = ast.literal_eval(user_collectibles)

                    # Ключ и значение для нового элемента
                    new_collectible_key = str(new_collectibles)
                    new_collectible_value = str(random.randint(111111, 99999999))  # Создаем nft_id

                    # Проверяем, есть ли этот ключ в словаре
                    if new_collectible_key in user_collectibles:
                        return "has"
                    else:
                        #nft_create(user_id, nft_id, skin_id):
                        nft = await nft_create(user_id, new_collectible_value, str(new_collectibles), "0")
                        if nft == "ok":
                            # Добавляем новую пару ключ-значение в словарь
                            user_collectibles[new_collectible_key] = new_collectible_value

                            # Преобразуем словарь обратно в строку для сохранения в базу данных
                            user_collectibles_str = str(user_collectibles)

                            cursor.execute(f'UPDATE users SET collectibles = ? WHERE user_id = ?', (user_collectibles_str, user_id))
                            db.commit()
                            return "ok"
                        else:
                            return "error"

            except Exception as e:
                rez = "error"
                print(f"Ошибка: {e}")
                return "error"
                # rez = "error"
        db.close()
    except:
        return "error"

async def new_active_skin(user_id: int, new_active_skin: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET active_skin = "{new_active_skin}" WHERE user_id = "{user_id}"'))
        new_pic_temp_settings = ""
        cursor.execute((f'UPDATE users SET pic_temp_settings = "{new_pic_temp_settings}" WHERE user_id = "{user_id}"'))
        cursor.execute((f'UPDATE users SET pic_temp_avatar = "{new_pic_temp_settings}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_active_emoji(user_id: int, new_active_emoji: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET active_emoji = "{new_active_emoji}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_days_online(user_id: int, new_days_online: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET days_online = "{new_days_online}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def new_all_games_played_count(user_id: int, new_all_games_played_count: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET all_games = "{new_all_games_played_count}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_wins(user_id: int, new_wins: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET wins = "{new_wins}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_loses(user_id: int, new_loses: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET loses = "{new_loses}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_tokenwins(user_id: int, new_tokenwins: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET tokenwins = "{new_tokenwins}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_tokenloses(user_id: int, new_tokenloses: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET tokenloses = "{new_tokenloses}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_coinwins(user_id: int, new_coinwins: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET coinwins = "{new_coinwins}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_coinloses(user_id: int, new_coinloses: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET coinloses = "{new_coinloses}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_ban(user_id: int, new_ban: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET ban = "{new_ban}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_active(user_id: int, new_active: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET active = "{new_active}" WHERE user_id = "{user_id}"'))
        db.commit()
        #db.close()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()


async def new_public_name(user_id: int, new_public_name: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        # Приводим new_public_name к нижнему регистру перед сравнением
        cursor.execute(('SELECT user_id, publicname FROM users WHERE LOWER(publicname) = LOWER(?)'), (new_public_name,))
        result = cursor.fetchone()

        good = 0

        if result:
            existing_user_id, existing_publicname = result
            if str(existing_user_id) != str(user_id):
                good = 0
            else:
                good = 1
        else:
            good = 1

        # Если имя свободно, обновляем информацию в базе данных
        if good == 1:
            cursor.execute(('UPDATE users SET publicname = ? WHERE user_id = ?'), (new_public_name, user_id))
            db.commit()
            return "ok"
        else:
            return "false"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "error"
    finally:
        db.close()

# async def new_public_name(user_id: int, new_public_name: int):
#     try:
#         db = sqlite3.connect(f"{dbn}.db")
#         cursor = db.cursor()
#
#         # cursor.execute((f'SELECT publicname FROM users WHERE publicname = "{new_public_name}"'))
#         # result = cursor.fetchone()
#         cursor.execute((f'SELECT user_id, publicname FROM users WHERE publicname = "{new_public_name}"'))
#         result = cursor.fetchone()
#
#         try:
#             existing_user_id, existing_publicname = result
#         except:
#             pass
#
#         good = 0
#
#         if result and str(existing_user_id) != str(user_id):
#             good = 0
#         else:
#             cursor.execute((f'UPDATE users SET publicname = "{new_public_name}" WHERE user_id = "{user_id}"'))
#             db.commit()
#             good = 1
#
#         if good == 1:
#             return "ok"
#         else:
#             return "false"
#     except:
#         return "error"
#     finally:
#         if db:
#             db.close()

async def add_daily_withdraws(user_id: int, daily_withdraws: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        daily_withdraws +=1

        cursor.execute((f'UPDATE users SET daily_withdraws = "{daily_withdraws}" WHERE user_id = "{user_id}"'))
        db.commit()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_last_time_download_skin(user_id: int, new_time: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET last_time_download_pic = "{new_time}" WHERE user_id = "{user_id}"'))
        db.commit()
        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def get_wallet_info(wallet_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute('SELECT user_id FROM users WHERE wallet_id = ?', (wallet_id,))
        user_id = cursor.fetchone()

        if user_id:
            return user_id[0]
        else:
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        if db:
            db.close()

async def referrers_get_count(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,))
        count = cursor.fetchone()[0]

        return count
    except:
        return "error"
    finally:
        if db:
            db.close()

async def new_referrer_set(user_id: int, referrer: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET referrer_id = "{referrer}" WHERE user_id = "{user_id}"'))
        db.commit()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def get_pic_custom(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute('SELECT pic_custom FROM users WHERE user_id = ?', (user_id,))
        pic_custom = cursor.fetchone()

        if pic_custom:
            return pic_custom[0]
        else:
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        if db:
            db.close()

async def set_pic_to_bd(user_id: int, pic: bytes or None, place: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        # Обновляем только если pic это данные изображения или явно None
        if pic is not None or pic is None:
            cursor.execute(f'UPDATE users SET {place} = ? WHERE user_id = ?', (pic, user_id))
        db.commit()

        return "ok"
    except Exception as e:
        # Лучше логгировать конкретное исключение
        print(f"Error: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def new_username(user_id: int, new_username: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE users SET username = "{new_username}" WHERE user_id = "{user_id}"'))
        db.commit()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def get_level_info(user_points):
    try:
        user_level = 1
        user_points_orig = user_points
        #финальные user_points (-44) приплюсовать к первоначальным (31) и получим 75 - сколько нужно для нового уровня

        final_levels = {}

        for i in range(2, 9999999999):
            new_points = i * 15
            user_points -= new_points
            if user_points <= 0:
                user_level = i
                user_level -=1
                break
            else:
                final_levels[i] = new_points

        need_exp_to_new_lvl = abs(user_points) + abs(user_points_orig)
        return user_level, need_exp_to_new_lvl

    except:
        return "error"

async def new_exp(user_id: int, new_exp: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_db = cursor.fetchone()
        if user_db:
            try:
                user_exp = int(user_db[40])

                user_exp += new_exp
                cursor.execute((f'UPDATE users SET exp = "{user_exp}" WHERE user_id = "{user_id}"'))
                db.commit()

                return "ok"
            except:
                return "error"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def energy_drink_use(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        rez = "error"

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_db = cursor.fetchone()
        if user_db:
            try:
                user_energy = int(user_db[38])
                user_energy_drinks = int(user_db[39])
            except:
                rez = "error"
        if user_energy_drinks >=1:
            if user_energy == 20:
                rez = "UserHaveMaxEnergyYet"
            else:
                user_energy_drinks -=1
                user_energy += 8
                if user_energy > 20:
                    user_energy = 20

                cursor.execute((f'UPDATE users SET energy_drinks = "{user_energy_drinks}" WHERE user_id = "{user_id}"'))
                cursor.execute((f'UPDATE users SET energy = "{user_energy}" WHERE user_id = "{user_id}"'))
                db.commit()
                rez = "ok"
        else:
            rez = "DontHaveEnergyDrinks"

        return rez
    except:
        return "error"
    finally:
        if db:
            db.close()

#################   SHOP

async def coll_test_buy(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        purchased_items = []

        # Добавляем ID товаров в список
        purchased_items.append('5')  # теперь список будет ['5']
        purchased_items.append('12')  # станет ['5', '12']
        purchased_items.append('21')  # и теперь ['5', '12', '21']

        # Выводим текущий список
        print(purchased_items)  # Выведет ['5', '12', '21']

        cursor.execute((f'UPDATE users SET collectibles = "{purchased_items}" WHERE user_id = "{user_id}"'))
        db.commit()

        return "ok"
    except:
        return "error"
    finally:
        if db:
            db.close()

# Покупка
async def shop_buy_item(user_id: int, item_id: int, buy_count: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        rez = "error"

        if buy_count == 0:
            buy_count = 1

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_db = cursor.fetchone()
        if user_db:
            try:
                user_tokens = float(user_db[2])
                user_coins = float(user_db[3])
                user_tickets = int(user_db[4])
                user_collectibles = str(user_db[8])
                user_energy_drinks = int(user_db[39])

                user_collectibles = ast.literal_eval(user_collectibles)

            except Exception as e:
                rez = "error"
                print(f"Ошибка: {e}")
                return "error"
        db.close()

        # Проверяем, есть ли этот ID в списке
        if str(item_id) in user_collectibles:
            rez = "has"
        else:
            db = sqlite3.connect(f"{dbn}.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM collectibles WHERE item_id = ?", (item_id,))
            item_db = cursor.fetchone()
            if item_db:
                try:
                    item_type = item_db[1]
                    item_price_coins = float(item_db[6])
                    item_price_tokens = float(item_db[7])
                    item_count = int(item_db[8])
                except:
                    rez = "error"

            db.close()

            buying = 0

            if item_count >=buy_count or item_count == -1:  #Если нужное кол-во товара есть в наличии или если он бесконечный
                if item_price_coins !=0:  #Если товар продается за коины
                    if user_coins >= item_price_coins:  #Если средств хватает
                        user_coins -= item_price_coins
                        balance = await new_coins(user_id, user_coins)
                        buying = 1
                    else:
                        buying = 0
                        rez = "money"
                elif item_price_tokens !=0:  #Если товар продается за токены
                    if user_tokens >= item_price_tokens:  # Если средств хватает
                        user_tokens -= item_price_tokens
                        balance = await new_tokens(user_id, user_tokens)
                        buying = 1
                    else:
                        buying = 0
                        rez = "money"
                else:   #Если товар бесплатный
                    buying = 1

                if buying == 1: #Начисляем товар пользователю

                    if item_type == "energy_drink":

                        user_energy_drinks += buy_count

                        db = sqlite3.connect(f"{dbn}.db")
                        cursor = db.cursor()
                        cursor.execute((f'UPDATE users SET energy_drinks = "{user_energy_drinks}" WHERE user_id = "{user_id}"'))
                        db.commit()
                        db.close()

                        rez = "ok"
                    elif item_type == "ticket":
                        user_tickets += buy_count

                        db = sqlite3.connect(f"{dbn}.db")
                        cursor = db.cursor()
                        cursor.execute((f'UPDATE users SET tickets = "{user_tickets}" WHERE user_id = "{user_id}"'))
                        db.commit()
                        db.close()

                        rez = "ok"
                    else:
                        new_collectible_value = str(random.randint(111111, 99999999))  # Создаем nft_id

                        # item_price_coins = float(item_db[6])
                        # item_price_tokens = float(item_db[7])
                        if item_price_coins != 0:
                            nft_history_cost = item_price_coins
                        else:
                            if item_price_tokens != 0:
                                nft_history_cost = item_price_tokens
                            else:
                                nft_history_cost = 0
                        nft = await nft_create(user_id, new_collectible_value, str(item_id), nft_history_cost)
                        if nft == "ok":
                            # Добавляем новую пару ключ-значение в словарь
                            user_collectibles[str(item_id)] = new_collectible_value

                            # Преобразуем словарь обратно в строку для сохранения в базу данных
                            user_collectibles_str = str(user_collectibles)

                            db = sqlite3.connect(f"{dbn}.db")
                            cursor = db.cursor()

                            # Если товар имет кол-во - уменьшаем его
                            if item_count != -1 and item_count >= 1:
                                item_count -= 1
                                if item_count <=0:
                                    item_count = 0
                                cursor.execute((f'UPDATE collectibles SET item_count = "{item_count}" WHERE item_id = "{item_id}"'))
                                if item_type == "skin_png" or item_type == "skin_anim":
                                    cursor.execute((f'UPDATE users SET active_skin = "{item_id}" WHERE user_id = "{user_id}"'))
                                elif item_type == "emoji":
                                    cursor.execute((f'UPDATE users SET active_emoji = "{item_id}" WHERE user_id = "{user_id}"'))

                            cursor.execute(f'UPDATE users SET collectibles = ? WHERE user_id = ?', (user_collectibles_str, user_id))
                            db.commit()
                            db.close()

                            rez = "ok"
                        else:
                            rez = "error"
            else:
                rez = "out"
        return rez

    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def lavka_buy_item(user_id: int, nft_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        # Логика:
        # Проверяем продается ли такой nft_id, если да, то парсим цену. Смотрим хватает ли денег у юзера. Если да, удаляем из таблицы Лавка
        # Добавляем в коллектеблс юзера, присваеваем активным скином, удаляем у прошлого владельца!!! После вычитаем бабки и начисляем прошлому владельцу - пишем у вас купили item
        # ДОП ПРОВЕРКА - есть ли такой скин с item_id у юзера? Если да, то отбой - у вас уже есть такой скин

        # Не забыть обновить owner_id в таблице нфт, а также добавить транзакцию в историю

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_db = cursor.fetchone()
        if user_db:
            try:
                user_coins = float(user_db[3])
                user_collectibles = str(user_db[8])
                user_collectibles = ast.literal_eval(user_collectibles)
                user_publicname = user_db[30]

                cursor.execute(f"SELECT * FROM lavka WHERE nft_id = ?", (nft_id,))
                item_db = cursor.fetchone()
                if item_db:
                    try:
                        item_id = item_db[1]
                        seller_id = int(item_db[2])
                        price = float(item_db[3])

                        cursor.execute(f"SELECT item_type FROM collectibles WHERE item_id = ?", (item_id,))
                        item_type = str(cursor.fetchone()[0])

                        if str(item_id) in user_collectibles:
                            return "has"
                        else:
                            if user_coins >= price:

                                cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (seller_id,))
                                seller_db = cursor.fetchone()
                                if user_db:
                                    seller_coins = float(seller_db[3])
                                    seller_lang = seller_db[6]
                                    seller_collectibles = str(seller_db[8])
                                    seller_collectibles = ast.literal_eval(seller_collectibles)
                                    seller_active_emoji = int(seller_db[41])

                                    seller_collectibles.pop(str(item_id), None)
                                    seller_collectibles_str = str(seller_collectibles)
                                    cursor.execute(f'UPDATE users SET collectibles = ? WHERE user_id = ?', (seller_collectibles_str, seller_id))
                                    #####

                                    cursor.execute(f"DELETE FROM lavka WHERE nft_id = ?", (nft_id,))

                                    user_collectibles[str(item_id)] = str(nft_id)

                                    # Преобразуем словарь обратно в строку для сохранения в базу данных
                                    user_collectibles_str = str(user_collectibles)
                                    cursor.execute(f'UPDATE users SET collectibles = ? WHERE user_id = ?', (user_collectibles_str, user_id))

                                    cursor.execute(f'UPDATE nft SET owner_id = ? WHERE nft_id = ?', (user_id, nft_id))
                                    #db.commit()

                                    user_coins -= price
                                    seller_coins += price

                                    cursor.execute(f'UPDATE users SET coins = ? WHERE user_id = ?', (user_coins, user_id))
                                    cursor.execute(f'UPDATE users SET coins = ? WHERE user_id = ?', (seller_coins, seller_id))

                                    if item_type == "skin" or item_type == "skin_anim":
                                        cursor.execute((f'UPDATE users SET active_skin = "{item_id}" WHERE user_id = "{user_id}"'))
                                        new_pic_temp_settings = ""
                                        cursor.execute((f'UPDATE users SET pic_temp_settings = "{new_pic_temp_settings}" WHERE user_id = "{user_id}"'))
                                    elif item_type == "emoji":
                                        cursor.execute((f'UPDATE users SET active_emoji = "{item_id}" WHERE user_id = "{user_id}"'))
                                        if seller_active_emoji == item_id:
                                            cursor.execute((f'UPDATE users SET active_emoji = "" WHERE user_id = "{seller_id}"'))

                                    # Добавляем транзакцию в историю nft
                                    cursor.execute(f"SELECT * FROM nft WHERE nft_id = ?", (nft_id,))
                                    user_db = cursor.fetchone()
                                    if user_db:
                                        unix_time = int(time.time())

                                        nft_history = str(user_db[3])
                                        nft_history = ast.literal_eval(nft_history)
                                        next_transaction_number = len(nft_history) + 1
                                        nft_history[next_transaction_number] = {
                                            'transaction_time': str(unix_time),
                                            'owner_id': str(seller_id),
                                            'price': str(price)
                                        }
                                        nft_history_str = str(nft_history)
                                        cursor.execute(f'UPDATE nft SET history = ? WHERE nft_id = ?', (nft_history_str, nft_id))
                                        db.commit()

                                        #####
                                        if price % 1 == 0:
                                            price = int(price)
                                        else:
                                            price = round(price, 2)

                                        if seller_lang == "ru":
                                            mess = "📬 <b>" + user_publicname + "</b> приобрел в Лавке ваш предмет!\n\nВы получили 💵" + str(price)
                                        elif seller_lang == "en":
                                            mess = "📬 User <b>" + user_publicname + "</b> has purchased your item on the Market!\n\nYou have received 💵" + str(price)
                                        elif seller_lang == "zh-TW":
                                            mess = "📬 用戶<b>" + user_publicname + "</b>在市場上購買了您的商品！\n\n您已收到 💵" + str(price)
                                        elif seller_lang == "es":
                                            mess = "📬 Usuario <b>" + user_publicname + "</b> ha comprado tu artículo en el Mercado!\n\nHas recibido 💵" + str(price)
                                        elif seller_lang == "ja":
                                            mess = "📬 ユーザー<b>" + user_publicname + "</b>がマーケットであなたの商品を購入しました！\n\n💵" + str(price) + "を受け取りました"
                                        elif seller_lang == "ar":
                                            mess = "📬 المستخدم <b>" + user_publicname + "</b> قد اشترى سلعتك في السوق!\n\nلقد استلمت 💵" + str(price)
                                        elif seller_lang == "de":
                                            mess = "📬 Benutzer <b>" + user_publicname + "</b> hat Ihren Artikel auf dem Markt gekauft!\n\nSie haben 💵" + str(price) + " erhalten"
                                        elif seller_lang == "hi":
                                            mess = "📬 उपयोगकर्ता <b>" + user_publicname + "</b> ने बाजार में आपके आइटम को खरीदा है!\n\nआपको 💵" + str(price) + " प्राप्त हुए हैं"
                                        elif seller_lang == "bn":
                                            mess = "📬 ব্যবহারকারী <b>" + user_publicname + "</b> বাজারে আপনার আইটেমটি কিনেছেন!\n\nআপনি 💵" + str(price) + " পেয়েছেন"
                                        elif seller_lang == "fr":
                                            mess = "📬 L'utilisateur <b>" + user_publicname + "</b> a acheté votre article sur le Marché !\n\nVous avez reçu 💵" + str(price)

                                        send = await message_to_telegram(seller_id, mess)

                                        return "ok"
                            else:
                                return "money"

                    except Exception as e:
                        print(f"Ошибка: {e}")
                        return "error"
                else:   # Не продается
                    return "sold"

            except Exception as e:
                print(f"Ошибка: {e}")
                return "error"

    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def set_daily_zero(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        user_days_online = 0

        cursor.execute((f'UPDATE users SET daily_get = "{user_days_online}" WHERE user_id = "{user_id}"'))
        cursor.execute((f'UPDATE users SET days_online = "{user_days_online}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

async def get_daily_check(user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        rez = "error"

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_db = cursor.fetchone()
        if user_db:
            try:
                user_collectibles = str(user_db[8])
                user_daily_get = int(user_db[10])
                user_days_online = int(user_db[14])

                user_collectibles = ast.literal_eval(user_collectibles)
                user_collectibles = list(user_collectibles.keys())

                unix_time = int(time.time())
                print(str(unix_time))
                #unix_time = user_daily_get + 73000
                if user_days_online >=30:
                    user_days_online = 1

                time_check = unix_time - user_daily_get
                print(str(time_check))
                if time_check >= 72000: # 72000 сек = 20 часов
                #if time_check >= 30:  # 600 сек = 10 мин
                    if time_check >= 158400:  # 158400 сек = 44 часа
                    #if time_check >= 1200:  # 1200 сек = 20 мин
                        # Переключаем день
                        user_days_online = 1
                        cursor.execute((f'UPDATE users SET days_online = "{user_days_online}" WHERE user_id = "{user_id}"'))
                        db.commit()
                    else:
                        #Переключаем день
                        user_days_online +=1
                        #user_days_online = 1
                        cursor.execute((f'UPDATE users SET days_online = "{user_days_online}" WHERE user_id = "{user_id}"'))
                        db.commit()
                    rez = "yes"
                    print("daily:yes")


                    ########## Скрипт получения дейлика
                    cursor.execute(f"SELECT * FROM daily_bonus WHERE day = ?", (user_days_online,))
                    daily_db = cursor.fetchone()
                    if daily_db:
                        try:
                            bonus_day = int(daily_db[0])
                            bonus_type = daily_db[1]
                            bonus_item_id = int(daily_db[2])
                            bonus_count = int(daily_db[3])

                            with open('web_url.json', 'r', encoding='utf-8') as f:
                                web_link = json.load(f)
                            bonus_image = web_link["url"] + "/get_item_image/" + str(bonus_item_id)
                            print("bonus_image: " + str(bonus_image))

                            if bonus_type == "skin_png" or bonus_type == "skin_anim":   # Если у юзера уже есть этот скин - скипаем и показываем фронту, что даем щитки
                                if str(bonus_item_id) in user_collectibles:
                                    bonus_num = random.randint(1, 3)
                                    if bonus_num == 1:
                                        bonus_image = web_link["url"] + "/get_item_image/23"
                                        tokens_num = random.randint(5, 100)
                                        user_dict = {
                                            "day": bonus_day,
                                            "bonus_type": "tokens",
                                            "bonus_item_id": "23",
                                            "bonus_count": str(tokens_num),
                                            "bonus_image": bonus_image,
                                        }
                                    elif bonus_num == 2:
                                        bonus_image = web_link["url"] + "/get_item_image/21"
                                        energy_drink_num = random.randint(1, 4)
                                        user_dict = {
                                            "day": bonus_day,
                                            "bonus_type": "energy_drink",
                                            "bonus_item_id": "21",
                                            "bonus_count": str(energy_drink_num),
                                            "bonus_image": bonus_image,
                                        }
                                    elif bonus_num == 3:
                                        bonus_image = web_link["url"] + "/get_item_image/24"
                                        exp_num = random.randint(5, 30)
                                        user_dict = {
                                            "day": bonus_day,
                                            "bonus_type": "exp",
                                            "bonus_item_id": "24",
                                            "bonus_count": str(exp_num),
                                            "bonus_image": bonus_image,
                                        }
                                    rez = user_dict
                                else:  # Если у юзера нет этого скина - показываем фронту, что выдаем скин
                                    user_dict = {
                                        "day": bonus_day,
                                        "bonus_type": bonus_type,
                                        "bonus_item_id": bonus_item_id,
                                        "bonus_count": bonus_count,
                                        "bonus_image": bonus_image,
                                    }
                                    rez = user_dict
                            else:  # Если бонус - не скин
                                user_dict = {
                                    "day": bonus_day,
                                    "bonus_type": bonus_type,
                                    "bonus_item_id": bonus_item_id,
                                    "bonus_count": bonus_count,
                                    "bonus_image": bonus_image,
                                }
                                rez = user_dict
                            # Обновляем время, когда брал дейлик
                            #unix_time = int(time.time())
                            cursor.execute((f'UPDATE users SET daily_get = "{unix_time}" WHERE user_id = "{user_id}"'))
                            db.commit()
                        except:
                            rez = "error 2"
                    ########## Скрипт получения дейлика

                else:
                    rez = "no"
                    print("daily:no")
            except:
                rez = "error"
        return rez
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        if db:
            db.close()

######Получить эмодзи

async def get_emoji_db(pack_id: int, emotion: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM emojies WHERE pack_id = {pack_id}")
        user_db = cursor.fetchone()
        if user_db:
            try:
                # Убедимся здесь, что возвращаемое значение - это байты.
                # Например, это может быть просто при чтении из столбца BLOB.
                image_data = user_db[emotion]
                return image_data
            except Exception as e:
                print(f"Ошибка: {e}")
                return "error"
        else:
            return "error"
    except Exception as e:
        print(f"Ошиbка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def get_user_emoji(user_id: int):
    result = {
        "name": None,
        "user_emoji_pack": []
    }
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        with open('web_url.json', 'r', encoding='utf-8') as f:
            web_link = json.load(f)
        link = web_link["url"] + "/emoji/"

        cursor.execute("SELECT active_emoji FROM users WHERE user_id = ?", (user_id,))
        active_emoji = cursor.fetchone()

        if active_emoji:
            cursor.execute("SELECT pack_name FROM emojies WHERE pack_id = ?", (active_emoji[0],))
            emoji_pack = cursor.fetchone()

            if emoji_pack:
                result["name"] = emoji_pack[0]  # Pack name assigned separately

                for i in range(1, 13):
                    emoji_url = f"{link}{active_emoji[0]}/{i}"
                    #print(emoji_url)
                    result["user_emoji_pack"].append(emoji_url)

                return result

            else:
                print("Emoji pack not found.")
                return result
        else:
            print("Active emoji not found for user.")
            return result

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if db:
            db.close()

async def get_item_image_db(item_id: int, type: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM collectibles WHERE item_id = {item_id}")
        user_db = cursor.fetchone()
        if user_db:
            try:
                # Убедимся здесь, что возвращаемое значение - это байты.
                # Например, это может быть просто при чтении из столбца BLOB.
                if type == "mask":
                    image_data = user_db[3]
                else:
                    image_data = user_db[2]
                return image_data
            except Exception as e:
                print(f"Ошибка: {e}")
                return "error"
        else:
            return "error"
    except Exception as e:
        print(f"Ошиbка: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def get_banners_info():
    banners_info = []
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute("SELECT * FROM ad_banners")
        banners = cursor.fetchall()
        print(banners)
        # item_ids = [item[0] for item in items]  # Превращаем в список значений
        # for item_id in item_ids:
        #     item_info = await load_item_data(item_id, 1)
        #     if item_info:
        #         items_with_info.append(item_info)
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        if db:
            db.close()

    return banners_info

#################### Лавка

async def add_sell_lavka(user_id: int, item_id: int, price: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        if str(item_id) == "28" or price < 0.1:
            return "error"
        else:
            cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_db = cursor.fetchone()
            if user_db:
                try:
                    # Чтобы не было абуза - сначала проверяем, что есть в коллектеблс, после (удаляем из коллектеблс - больше не удаляем, чтобы остался в инвентаре), после выкладываем на продажу. А иначе 2 раза клацнул и выложил 2 раза 1 скин

                    user_collectibles = str(user_db[8])
                    user_collectibles = ast.literal_eval(user_collectibles)

                    if str(item_id) in user_collectibles:   #товар у юзера в наличии

                        nft_id = user_collectibles.get(str(item_id), "Key not found")
                        if nft_id == "Key not found":
                            return "error"
                        else:

                            cursor.execute(f"SELECT nft_id FROM lavka WHERE nft_id = '{nft_id}'")
                            if cursor.fetchone() is None:
                                # Удаляем из коллектеблс - решил не удалять, чтобы в инвентаре остался
                                #user_collectibles.pop(str(item_id), None)

                                cursor.execute("INSERT INTO lavka VALUES (?, ?, ?, ?)", (nft_id, item_id, user_id, price))
                                db.commit()

                                return "ok"
                            else:
                                return "already"
                except Exception as e:
                    print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def lavka_sell_cancel(user_id: int, item_id: int): #Отменить продажу в Лавке
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_db = cursor.fetchone()
        if user_db:
            try:
                # Чтобы не было абуза - сначала проверяем, что есть в коллектеблс, после (удаляем из коллектеблс - больше не удаляем, чтобы остался в инвентаре), после выкладываем на продажу. А иначе 2 раза клацнул и выложил 2 раза 1 скин

                user_collectibles = str(user_db[8])
                user_collectibles = ast.literal_eval(user_collectibles)

                if str(item_id) in user_collectibles:  # товар у юзера в наличии

                    nft_id = user_collectibles.get(str(item_id), "Key not found")
                    if nft_id == "Key not found":
                        return "error"
                    else:

                        cursor.execute(f"DELETE FROM lavka WHERE nft_id = ?", (nft_id,))

                        db.commit()

                        return "ok"
                else:
                    return "error"
            except:
                return "error"
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


######################  WHITELIST
async def get_whitelist_user(user_id: int):
    try:
        with sqlite3.connect(f"{dbn}.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM whitelist WHERE user_id=?", (user_id,))
            user_data = cursor.fetchone()
            if user_data is None:
                return "error"
            else:
                return user_data
    except Exception as e:
        print(f"An error occurred: {e}")  # Желательно логировать конкретную ошибку для отладки
        return "error"
    finally:
        if db:
            db.close()

async def put_whitelist_user(user_id: int, username: str, date: int, approved: int):    #   Добавление в вайтлист
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT user_id FROM whitelist WHERE user_id = '{user_id}'")
        if cursor.fetchone() is None:
            cursor.execute(
                f"INSERT INTO whitelist VALUES (?, ?, ?, ?)", (user_id, username, date, approved))
            db.commit()
            return "ok"
        else:
            return "already"
    except:
        return "error"
    finally:
        if db:
            db.close()

async def update_whitelist_user(user_id: int, approved: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute((f'UPDATE whitelist SET approved = "{approved}" WHERE user_id = "{user_id}"'))
        db.commit()
        db.close()

        return "ok"
    except:
        return "error"

# # Ежедневный бонус добавление
# def add_daily_bonus(day: int, day_type: str, day_item_id: int, day_count: int):
#     try:
#         db = sqlite3.connect(f"{dbn}.db")
#         cursor = db.cursor()
#
#         cursor.execute(f"SELECT day FROM daily_bonus WHERE day = '{day}'")
#         if cursor.fetchone() is None:
#             cursor.execute(f"INSERT INTO daily_bonus VALUES (?, ?, ?, ?)", (day, day_type, day_item_id, day_count))
#             db.commit()
#
#         else:
#             pass
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         return "error"
#     finally:
#         db.close()  # Закрываем соединение в блоке finally
#
# add_daily_bonus(1, "tokens", 23, 20)
# add_daily_bonus(2, "skin_png", 1, 1)
# add_daily_bonus(3, "tokens", 23, 15)
# add_daily_bonus(4, "exp", 24, 30)
# add_daily_bonus(5, "tokens", 23, 25)
# add_daily_bonus(6, "skin_png", 2, 1)
# add_daily_bonus(7, "energy_drink", 21, 2)
# add_daily_bonus(8, "exp", 24, 40)
# add_daily_bonus(9, "energy_drink", 21, 2)
# add_daily_bonus(10, "skin_anim", 3, 1)
# add_daily_bonus(11, "tokens", 23, 15)
# add_daily_bonus(12, "energy_drink", 21, 5)
# add_daily_bonus(13, "exp", 24, 50)
# add_daily_bonus(14, "tokens", 23, 5)
# add_daily_bonus(15, "skin_png", 4, 1)
# add_daily_bonus(16, "exp", 24, 20)
# add_daily_bonus(17, "energy_drink", 21, 4)
# add_daily_bonus(18, "tokens", 23, 80)
# add_daily_bonus(19, "exp", 24, 20)
# add_daily_bonus(20, "emoji", 25, 1)
# add_daily_bonus(21, "tokens", 23, 25)
# add_daily_bonus(22, "tokens", 23, 35)
# add_daily_bonus(23, "exp", 24, 50)
# add_daily_bonus(24, "energy_drink", 21, 2)
# add_daily_bonus(25, "skin_anim", 5, 1)
# add_daily_bonus(26, "energy_drink", 21, 4)
# add_daily_bonus(27, "tokens", 23, 10)
# add_daily_bonus(28, "exp", 24, 35)
# add_daily_bonus(29, "exp", 24, 55)
# add_daily_bonus(30, "skin_png", 6, 1)
# add_daily_bonus(31, "tokens", 23, 90)
