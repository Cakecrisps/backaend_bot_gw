import sqlite3
import json
import asyncio
#from bd import load_user_data
from bd import *
# db = sqlite3.connect('rooms.db')
# curs = db.cursor()


async def get_rooms_count():
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        return len(cursor.execute("SELECT * FROM rooms_rps").fetchall())
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def create_room(creatorid: int, bet: float, room_type: int, bet_type: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        # c = await load_user_data(creatorid,1)
        # money = c['coins']
        # tokens = c['tokens']
        # tickets = c['tickets']
        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (creatorid,))
        user_db = cursor.fetchone()
        tokens = float(user_db[2])
        money = float(user_db[3])
        tickets = int(user_db[4])
        emoji = "none"

        if bet_type == 1:
            pass
        elif bet_type == 2:
            money = tickets
        elif bet_type == 3:
            money = tokens

        if money > bet:
            print(str({creatorid:{"choice":"none","money":money}}))
            r_c = await get_rooms_count()

            if room_type == 1:
                free_places = 1
                value = '-'
            else:
                free_places = 7
                value = f"{random.randint(1, 100)}"

            data = {
                "players": [
                    {
                        "userid": creatorid,
                        "choice": "none",
                        "money": money,
                        "emoji": emoji,
                        "tokens": tokens,
                        "prev_choice": "rock"
                    },
                ],
                "win": {
                    "winner_id": "none",
                    "f_anim": "none",
                    "s_anim": "none",
                    "users": "none",
                    "winner_value": "none"
                }
            }

            # data = {
            #     "players": [
            #         {
            #             "userid": creatorid,
            #             "choice": "none",
            #             "money": money,
            #             "emoji": emoji,
            #             "tokens": tokens,
            #             "prev_choice": "rock"
            #         },
            #     ],
            #     "win": [  # Добавляем новую секцию "win"
            #         {
            #             "winner_id": "none",
            #             "f_anim": "none",
            #             "s_anim": "none",
            #             "users": "none",
            #             "winner_value": "none"
            #         }
            #     ]
            # }
            cursor.execute(
                f"INSERT INTO rooms_rps VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    creatorid,
                    json.dumps(data),  # Конвертируем словарь в JSON строку
                    float(bet),
                    1,
                    room_type,
                    free_places,
                    bet_type,
                    value,
                    r_c + 1,
                    '{' + f'"{creatorid}":{json.dumps(data)}' + '}'
                )
            )
            #cursor.execute(f"INSERT INTO rooms_rps VALUES (?,?,?,?,?,?,?,?,?,?)",(creatorid,json.dumps({"players":[{"userid":creatorid,"choice":"none","money":money,"emoji":emoji,"tokens":tokens,"prev_choice":"rock"},]}),float(bet),1,room_type,free_places,bet_type,value,r_c + 1, ""))
            #old=#cursor.execute(f"INSERT INTO rooms_rps VALUES (?,?,?,?,?,?,?,?)",(creatorid,json.dumps({"players":[{"userid":creatorid,"choice":None,"money":money,"tickets":tickets,"tokens":tokens},]}),float(bet),1,room_type,free_places,bet_type,r_c + 1))
            db.commit()

            return {"message":"success","creator":creatorid,"room_id":r_c+1}
        else:
            return {"message":"not_enough_coins","creator":creatorid}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def edit_last_info(room_id,user_id,new_state):
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    r = await get_room(room_id,0)
    if r is None:
        return 0
    states = json.loads(r[9])
    if str(user_id) not in states:
        return 0
    states[str(user_id)] = new_state
    cursor.execute("UPDATE rooms_rps SET in_room_2 = (?) WHERE room_id = (?)",(json.dumps(states),int(room_id)))
    db.commit()
    db.close()
    return 1
async def get_last_info(room_id,user_id):
    r = await get_room(room_id,0)
    if r is None:
        return 0
    states = json.loads(r[9])
    if str(user_id) not in states:
        return 0
    return states[str(user_id)]
async def get_room(room_id : int, server: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        if server == 0:
            cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)',(room_id,))
            r = cursor.fetchone()
            print(r)
            return r
        elif server == 1:
            with open('web_url.json', 'r', encoding='utf-8') as f:
                web_link = json.load(f)


            cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)', (room_id,))
            row = cursor.fetchone()
            if row:
                columns = ['creator_id', 'in_room', 'bet', 'players_count', 'room_type',
                           'free_places', 'bet_type', 'misc_value', 'room_id']
                data = {columns[i]: str(row[i]) if isinstance(row[i], (int, float)) else row[i]
                        for i in range(len(columns))}

                in_room_data = json.loads(data.pop('in_room'))

                # original_emojis = []
                # Вот тут мы добавим информацию о каждом игроке
                for player in in_room_data['players']:
                    #print(player['userid'])
                    # if player['emoji'] != "none":
                    #     # Сохраняем исходный emoji
                    #     original_emojis.append({"userid": player["userid"], "emoji": player["emoji"]})
                    #     # Устанавливаем значение emoji на "none"
                    #     player['emoji'] = "none"


                        ####################

                        #####################
                    cursor.execute('SELECT publicname, active_skin FROM users WHERE user_id = (?)', (player['userid'],))
                    player_info = cursor.fetchone()
                    if player_info:
                        photo_url = web_link["url"] + "/avatar/" + str(player['userid'])
                        item_pic = web_link["url"] + "/get_item_image/" + str(player_info[1])
                        item_mask = web_link["url"] + "/get_item_image_mask/" + str(player_info[1])

                        player['publicname'] = player_info[0]
                        player['active_skin'] = player_info[1]
                        player['avatar'] = photo_url
                        player['item_pic'] = item_pic
                        player['item_mask'] = item_mask

                # if original_emojis == []:
                #     pass
                # else:
                #     # Обновляем данные в базе данных
                #     updated_in_room = json.dumps(in_room_data)
                #     cursor.execute('UPDATE rooms_rps SET in_room = ? WHERE room_id = ?',
                #                    (updated_in_room, room_id))
                #     db.commit()
                #
                #     for player in in_room_data['players']:  # предполагаем, что player_list - это список словарей с информацией о игроках
                #         for emoji_info in original_emojis:
                #             if player['userid'] == emoji_info['userid']:
                #                 player['emoji'] = emoji_info['emoji']

                return {**in_room_data, **data}
            print("ROOMS NONE")
            print(room_id)
            return None
        elif server == 2:
            cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)', (room_id,))
            row = cursor.fetchone()
            if row:
                columns = ['creator_id', 'in_room', 'bet', 'players_count', 'room_type',
                           'free_places', 'bet_type', 'misc_value', 'room_id']
                data = {columns[i]: str(row[i]) if isinstance(row[i], (int, float)) else row[i]
                        for i in range(len(columns))}

                in_room_data = json.loads(data.pop('in_room'))

                # original_emojis = []
                # for player in in_room_data['players']:
                #     if player['emoji'] != "none":
                #         # Сохраняем исходный emoji
                #         original_emojis.append({"userid": player["userid"], "emoji": player["emoji"]})
                #         print("Запомнили эмодзи")
                #         # Устанавливаем значение emoji на "none"
                #         player['emoji'] = "none"
                #         print("Удалили эмодзи")
                # if original_emojis == []:
                #     pass
                # else:
                #     print("rewrite эмодзи")
                #     # Обновляем данные в базе данных
                #     updated_in_room = json.dumps(in_room_data)
                #     cursor.execute('UPDATE rooms_rps SET in_room = ? WHERE room_id = ?',
                #                    (updated_in_room, room_id))
                #     db.commit()
                #     print("Удалили эмодзи 2")
                #
                #     for player in in_room_data['players']:  # предполагаем, что player_list - это список словарей с информацией о игроках
                #         for emoji_info in original_emojis:
                #             if player['userid'] == emoji_info['userid']:
                #                 player['emoji'] = emoji_info['emoji']
                #                 print("Отправил эмодзи на сервер")

                #return {**in_room_data, **data, "original_emojis": original_emojis}
                return {**in_room_data, **data}

            return None

            # Orig_2_server
            # cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)', (room_id,))
            # row = cursor.fetchone()
            # if row:
            #     columns = ['creator_id', 'in_room', 'bet', 'players_count', 'room_type',
            #                'free_places', 'bet_type', 'misc_value', 'room_id']
            #     data = {columns[i]: str(row[i]) if isinstance(row[i], (int, float)) else row[i]
            #             for i in range(len(columns))}
            #
            #     in_room_data = json.loads(data.pop('in_room'))
            #
            #     return {**in_room_data, **data}
            # return None
            # Orig_2_server
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def get_room_long_poling_check_from_bd(room_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()
        cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)', (room_id,))
        row = cursor.fetchone()
        print(row)
        if row:
            check = str(row[9])
            print(check)
            return check
        else:
            return "error"

    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def set_room_long_polling_in_room_2(room_id: int, new_data: str):
    try:
        with sqlite3.connect(f"{dbn}.db") as db:
            cursor = db.cursor()
            new_data_str = str(new_data)
            update_query = '''UPDATE rooms_rps SET in_room_2 = ? WHERE room_id = ?'''
            cursor.execute(update_query, (new_data_str, room_id))
            db.commit()
        return "success"

    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def wait_for_room_change(room_id, server, last_known_state,player_id):
    while True:
        #print('while')
        current_state = await get_room(room_id, server)
        if current_state is None:
            print("Вышел из цикла")
            break  # Выход из цикла, если комната была удалена.
        if str(current_state) != str(last_known_state):
            print("update")
            print(last_known_state)
            print(current_state)
            set_new_data_in_room_2 = await edit_last_info(room_id,player_id,current_state)
            return current_state
        #print("nothing...")
        await asyncio.sleep(2) # небольшая задержка перед следующим опросом
        #await asyncio.sleep(0.5)  # небольшая задержка перед следующим опросом

# async def wait_for_room_change(room_id, server, last_known_state):
#     last_known_state_str = json.dumps(last_known_state, sort_keys=True)
#     while True:
#         current_state = await get_room(room_id, server)
#         if current_state is None:
#             break
#         current_state_str = json.dumps(current_state, sort_keys=True)
#         if current_state_str != last_known_state_str:
#             print("update")
#             print(json.dumps(last_known_state, indent=2))
#             print(json.dumps(current_state, indent=2))
#             set_new_data_in_room_2 = await set_room_long_polling_in_room_2(room_id, current_state)
#             return current_state
#         print("nothing...")
#         await asyncio.sleep(1)

async def get_room_long_poling(room_id,player_id,server):
    last_known_state = await get_last_info(room_id,player_id)
    new_state = await wait_for_room_change(room_id, server, last_known_state,player_id)
    #rooms_state[room_id] = new_state # обновляем состояние
    return new_state

async def who_is_win_rps(room_id: int, user_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)',(room_id,))
        r = cursor.fetchone()

        db.close()  ##################################################################################################################################################################

        if r:
            print(r)
            us = json.loads(r[1])
            players = us['players']
            if len(players) != 1 and r[4] == 1:
                fc = players[0]['choice']
                sc = players[1]['choice']
                print(fc,sc)
                if fc == "ready" or sc == "ready" or fc == "none" or sc == "none":
                    return {"message":"player_not_ready","room_id":room_id}
                else:
                    print("add_prev_choice_1" + str(fc))
                    print("add_prev_choice_2" + str(sc))

                    print(str(user_id))
                    print(str(players[0]["userid"]))

                    if str(players[0]["userid"]) == str(user_id):
                        print("ИГРОК 1")
                        write_choice = fc
                        print(write_choice)
                        await set_prev_choice(room_id, user_id, write_choice)

                        write_choice = sc
                        await set_prev_choice(room_id, players[1]["userid"], write_choice)

                        print("УСТАНОВИЛ ПРЕВ ЧОЙЗ")
                    elif str(players[1]["userid"]) == str(user_id):
                        print("ИГРОК 2")
                        write_choice = sc
                        print(write_choice)
                        await set_prev_choice(room_id, user_id, write_choice)

                        write_choice = fc
                        await set_prev_choice(room_id, players[0]["userid"], write_choice)

                        print("УСТАНОВИЛ ПРЕВ ЧОЙЗ")

                    # add_prev_choice_1 = await set_prev_choice(room_id, players[0], fc)
                    # add_prev_choice_2 = await set_prev_choice(room_id, players[1], sc)

                    with open('web_url.json', 'r', encoding='utf-8') as f:
                        web_link = json.load(f)

                    prev_fc = players[0]['prev_choice']
                    prev_sc = players[1]['prev_choice']
                    f_anim = web_link["url"] + "/cyefa_anim/l-" + prev_fc[0] + fc[0]
                    s_anim = web_link["url"] + "/cyefa_anim/r-" + prev_sc[0] + sc[0]

                    # users = {}
                    # for player in us["players"]:
                    #     userid = str(player['userid'])
                    #     users[userid] = {'coins': 0.0}
                    #
                    # users_results = await game_results(users, players[0], float(r[2]), int(r[6]))

                    if fc == sc:
                        #print("СБРОСИЛ ЧОЙЗ")
                        #reset_game_1 = await set_choice(room_id, players[0], "none")
                        return {"message":"success","winner":"draw","room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif fc == "scissors" and sc == "paper":
                        return {"message":"success","winner":str(players[0]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif fc == "scissors" and sc == "rock":
                        return {"message":"success","winner":str(players[1]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif fc == "paper" and sc == "rock":
                        return {"message":"success","winner":str(players[0]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif fc == "paper" and sc == "scissors":
                        return {"message":"success","winner":str(players[1]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif fc == "rock" and sc == "paper":
                        return {"message":"success","winner":str(players[1]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif fc == "rock" and sc == "scissors":
                        return {"message":"success","winner":str(players[0]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}

                    elif sc == "scissors" and fc == "paper":
                        return {"message":"success","winner":str(players[1]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif sc == "scissors" and fc == "rock":
                        return {"message":"success","winner":str(players[0]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif sc == "paper" and fc == "rock":
                        return {"message":"success","winner":str(players[1]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif sc == "paper" and fc == "scissors":
                        return {"message":"success","winner":str(players[0]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif sc == "rock" and fc == "paper":
                        return {"message":"success","winner":str(players[0]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
                    elif sc == "rock" and fc == "scissors":
                        return {"message":"success","winner":str(players[1]["userid"]),"room_id":room_id,"f_anim":f_anim,"s_anim":s_anim}
            else:
                return {"message":"not_enough_player","room_id":room_id}
        else:
            return {"message":"room_is_not_valid","room_id":room_id}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def add_player(room_id,player_id):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        kick = await kick_player(player_id)

        r = await get_room(room_id, 0)
        if r == None:
             return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}

        players = json.loads(r[1])
        # c = await load_user_data(player_id,1)
        # money = c['coins']
        # tickets = c['tickets']
        # tokens = c['tokens']

        # Проверяем наличие пользователя в комнате
        if any(player['userid'] == player_id for player in players['players']):
            # Пользователь уже в комнате, игнорируем добавление
            return {"message": "player_already_in_room", "player_id": player_id, "room_id": room_id}

        # 🚫 Если нет свободных мест, не добавляем пользователя
        if r[5] == 0:
            return {"message": "no_free_places", "player_id": player_id, "room_id": room_id}

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (player_id,))
        user_db = cursor.fetchone()
        tokens = float(user_db[2])
        money = float(user_db[3])
        #tickets = int(user_db[4])

        emoji = "none"

        if r[6] == 2:
            r[6] = 3

        if r[6] == 1 and money < r[2]:
            return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
        # elif r[6] == 2 and tickets < r[2]:
        #     return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
        elif r[6] == 3 and tokens < r[2]:
            return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
        if r[5] != 0:
            if r[5] == 1:   #Если цу-е-фа
                players['players'].append({"userid":player_id,"choice":"none","money":money,"emoji":emoji,"tokens":tokens,"prev_choice":"rock"})
            else:
                players['players'].append({"userid": player_id, "choice": "none", "money": money, "emoji": emoji, "tokens": tokens})
            players = json.dumps(players)
            cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}",(players,))
            cursor.execute(f"UPDATE rooms_rps SET players_count = (?) WHERE room_id = {room_id}",(r[3]+1,))
            cursor.execute(f"UPDATE rooms_rps SET free_places = (?) WHERE room_id = {room_id}",(r[5] - 1,))
            db.commit()
            return {"message":"success","player_id":player_id,"room_id":room_id}
        return {"message":"no_free_places","player_id":player_id,"room_id":room_id}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


# async def kick_player(room_id, player_id):
#     try:
#         db = sqlite3.connect(f"{dbn}.db")
#         cursor = db.cursor()
#
#         # Получаем информацию о комнате
#         r = await get_room(room_id, 0)
#         if r is None:
#             return {"message": "room_is_not_valid", "player_id": player_id, "room_id": room_id}
#
#         players = json.loads(r[1])
#
#         for i in range(len(players['players'])):
#             if players['players'][i]['userid'] == player_id:
#                 players['players'].pop(i)
#
#                 # Если после удаления игрока список становится пустым
#                 if not players['players']:
#                     # Удаляем комнату из базы данных
#                     cursor.execute(f"DELETE FROM rooms_rps WHERE room_id = {room_id}")
#                     db.commit()
#                     return {"message": "room_closed", "player_id": player_id, "room_id": room_id}
#                 else:
#                     # Обновляем информацию о комнате в базе данных
#                     players = json.dumps(players)
#                     cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}", (players,))
#                     cursor.execute(f"UPDATE rooms_rps SET players_count = (?) WHERE room_id = {room_id}", (r[3] - 1,))
#                     cursor.execute(f"UPDATE rooms_rps SET free_places = (?) WHERE room_id = {room_id}", (r[5] + 1,))
#                     db.commit()
#                     return {"message": "success", "player_id": player_id, "room_id": room_id}
#
#         return {"message": "no_player", "player_id": player_id, "room_id": room_id}
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         return "error"
#     finally:
#         # Закрываем соединение с БД при любом исходе
#         if db:
#             db.close()

async def kick_player(player_id: int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        #player_id = str(player_id)

        # Получаем список всех комнат
        cursor.execute("SELECT room_id, in_room FROM rooms_rps")
        rooms = cursor.fetchall()

        removed_rooms = []
        for room_id, players_json in rooms:
            players = json.loads(players_json)

            # Проверяем, находится ли игрок в комнате
            player_exists = any(player['userid'] == player_id for player in players['players'])
            if player_exists:
                # Удаляем игрока из комнаты
                players['players'] = [player for player in players['players'] if player['userid'] != player_id]

                if not players['players']:
                    # Если в комнате не осталось игроков, удаляем комнату
                    cursor.execute(f"DELETE FROM rooms_rps WHERE room_id = {room_id}")
                    removed_rooms.append(room_id)
                else:
                    # Обновляем информацию о комнате в базе данных
                    updated_players_json = json.dumps(players)
                    players_count = len(players['players'])
                    free_places = players_count  # или рассчитайте свободные места, если это необходимо
                    cursor.execute("UPDATE rooms_rps SET in_room = ?, players_count = ?, free_places = ? WHERE room_id = ?",
                                   (updated_players_json, players_count, free_places, room_id))

        db.commit()
        return {"message": "success", "player_id": player_id, "removed_rooms": removed_rooms}
    except Exception as e:
        print(f"Ошибка: {e}")
        return {"message": "error", "error": str(e)}
    finally:
        # Закрываем соединение с БД при любом исходе
        if db:
            db.close()

async def set_choice(room_id, player_id, choice):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = await get_room(room_id, 0)
        if r is None:
            return {"message": "room_is_not_valid", "player_id": player_id, "room_id": room_id}

        players = json.loads(r[1])

        # Проверяем количество игроков в комнате
        if len(players['players']) <= 1 and choice == 'ready':
            return {"message": "not_enough_players", "player_id": player_id, "room_id": room_id}

        if choice == 'none':
            # Сбросить выбор всех игроков на 'none'
            for player in players['players']:
                #if str(player['userid']) == str(player_id):
                player['choice'] = 'none'
        else:
            any_not_ready = any(player['choice'] == 'none' for player in players['players'])
            #any_not_ready = False
            # Обновляем статус текущего игрока
            for player in players['players']:
                if str(player['userid']) == str(player_id):
                    if choice != 'ready' and any_not_ready:
                        # Если кто-то не готов и выбор не 'ready', отменяем ход
                        return {"message": "player_not_ready", "player_id": player_id, "room_id": room_id}
                    else:
                        # В противном случае обновляем 'choice'
                        player['choice'] = choice
                        break

        if choice != "none" and choice != "ready":
            players['win']['winner_id'] = "none"
            players['win']['f_anim'] = "none"
            players['win']['s_anim'] = "none"
            players['win']['users'] = "none"
            players['win']['winner_value'] = "none"
            #players['win']['sended'] = []

        players_serialized = json.dumps(players)
        cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?", (players_serialized, room_id))
        db.commit()
        return {"message": "success", "player_id": player_id, "room_id": room_id, "choice": choice}

    except Exception as e:
        print(f"Ошибка: {e}")
        return {"message": "error"}
    finally:
        db.close()

async def set_prev_choice(room_id, player_id, prev_choice):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = await get_room(room_id, 0)
        if r is None:
            return "not_room"

        players = json.loads(r[1])

        print("prev_choice_new" + str(prev_choice))
        print("player id" + str(player_id))
        #player_id = player_id['userid']
        print(player_id)
        print("room id" + str(room_id))

        # Обновляем статус текущего игрока
        for player in players['players']:
            if str(player['userid']) == str(player_id):
                # В противном случае обновляем 'choice'
                player['prev_choice'] = prev_choice
                break

        players_serialized = json.dumps(players)
        print(players_serialized)
        #cursor.execute("UPDATE rooms_rps SET in_room_2 = ? WHERE room_id = ?", (players_serialized, room_id))
        cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?", (players_serialized, room_id))
        db.commit()
        return "ok"
        #return {"message": "success", "player_id": player_id, "room_id": room_id, "prev_choice": prev_choice}

    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
        #return {"message": "error"}
    finally:
        db.close()

async def set_emoji(room_id: int, player_id: int, emoji_id: str):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = await get_room(room_id, 0)
        if r is None:
            return {"message": "room_is_not_valid", "player_id": player_id, "room_id": room_id}

        players = json.loads(r[1])

        # # Проверяем количество игроков в комнате
        # if len(players['players']) <= 1 and choice == 'ready':
        #     return {"message": "not_enough_players", "player_id": player_id, "room_id": room_id}

        #else:
        # Обновляем статус текущего игрока
        for player in players['players']:
            if str(player['userid']) == str(player_id):
                if emoji_id == "none":
                    emoji_url = "none"
                else:

                    cursor.execute('SELECT active_emoji FROM users WHERE user_id = (?)', (int(player_id),))
                    active_emoji = str(cursor.fetchone()[0])

                    with open('web_url.json', 'r', encoding='utf-8') as f:
                        web_link = json.load(f)
                    emoji_url = web_link["url"] + "/emoji/" + active_emoji + "/" + str(emoji_id)

                player['emoji'] = emoji_url
                break

        players_serialized = json.dumps(players)
        cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?", (players_serialized, room_id))
        db.commit()
        return {"message": "success", "player_id": player_id, "room_id": room_id, "emoji": emoji_url}

    except Exception as e:
        print(f"Ошибка: {e}")
        return {"message": "error"}
    finally:
        db.close()

# async def set_choice(room_id,player_id,choice):
#     try:
#         db = sqlite3.connect(f"{dbn}.db")
#         cursor = db.cursor()
#
#         r = await get_room(room_id, 0)
#         if r == None:
#             return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}
#
#         players = json.loads(r[1])
#
#         for i in range(len(players['players'])):
#             if players['players'][i]['userid'] == player_id:
#                 players['players'][i]['choice'] = choice
#                 players = json.dumps(players)
#                 cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}",(players,))
#                 db.commit()
#                 return {"message":"success","player_id":player_id,"room_id":room_id,"choice":choice}
#
#         return {"message":"no_player","player_id":player_id,"room_id":room_id,"choice":choice}
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         return "error"
#     finally:
#         if db:
#             db.close()


async def game_results(users: dict, winner_id: str, stavka: float, valute: int, room_id: int):
    try:
        print("зашел в функцию")
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        winner_id = int(winner_id)

        ######
        # Здесь вставьте код для получения комнаты (аналог get_room)
        cursor.execute("SELECT * FROM rooms_rps WHERE room_id = ?", (room_id,))
        room = cursor.fetchone()
        if room is None:
            # Обработайте исключительную ситуацию с неверной комнатой
            return "room_is_not_valid", users

        players_in_room = json.loads(room[1])
        bet_type = room[6]

        ######
        stavka_orig = stavka
        stavka = stavka - stavka * bot_fee / 100

        if len(users) >= 2:  # Если он не один в комнате
            for user in users:

                try:
                    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user,))  # Используем placeholder
                    result = cursor.fetchone()
                except:
                    db = sqlite3.connect(f"{dbn}.db")
                    cursor = db.cursor()

                    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user,))  # Используем placeholder
                    result = cursor.fetchone()
                if result:
                    user_id = int(result[0])
                    user_stavka = stavka    #Ставка конкретного юзера, так как вычитается рефералу еще индивидуально
                    if valute == 1: #Коины
                        user_money = float(result[3])
                        if user_id == winner_id:  # Победитель
                            user_referrer_id = result[11]
                            if user_referrer_id == None or str(user_referrer_id) == "":
                                pass
                            else:
                                user_referrer_id = int(user_referrer_id)
                                ###########################################################

                                user_fee_amount = (users_fee / 100) * user_stavka
                                user_stavka = user_stavka - user_fee_amount

                                # Загрузка текущего значения friend_referrer_coins
                                cursor.execute("SELECT referrer_coins, referrer_all_coins FROM users WHERE user_id = ?", (user_referrer_id,))
                                ref_result = cursor.fetchone()

                                if ref_result:
                                    friend_referrer_coins = json.loads(ref_result[0]) if ref_result and ref_result[0] else {}
                                    friend_referrer_all_coins = float(ref_result[1])
                                else:
                                    friend_referrer_coins = {}
                                    friend_referrer_all_coins = float(0.0)

                                # Преобразование user_id в строку для использования в качестве ключа JSON
                                user_id_str = str(user_id)

                                # Проверка существования ключа, если да - инкрементирование, если нет - установка
                                if user_id_str in friend_referrer_coins:
                                    friend_referrer_coins[user_id_str] += user_fee_amount
                                else:
                                    friend_referrer_coins[user_id_str] = user_fee_amount

                                # print(friend_referrer_coins)  # Для отладки
                                friend_referrer_coins_json = json.dumps(friend_referrer_coins)

                                friend_referrer_all_coins += user_fee_amount

                                # Используем параметризованный запрос
                                cursor.execute("UPDATE users SET referrer_coins = ? WHERE user_id = ?", (friend_referrer_coins_json, user_referrer_id))
                                cursor.execute("UPDATE users SET referrer_all_coins = ? WHERE user_id = ?", (friend_referrer_all_coins, user_referrer_id))

                                #########################################################
                            print("победитель: " + str(user_id))
                            print(user_money)
                            #user_money += round(user_stavka, 2)
                            user_money -= user_stavka
                        else:   #Проигравший
                            print("проигравший: " + str(user_id))
                            print(user_money)
                            #user_money -= round(user_stavka, 2)
                            user_money -= user_stavka
                        user_money = round(user_money, 3)
                        print(user_money)
                        cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?", (user_money, user_id))
                    else:   #Токены
                        user_money = float(result[2])
                        if user_id == winner_id:  # Победитель
                            print("победитель: " + str(user_id))
                            print(user_money)
                            #user_money += round(user_stavka, 2)
                            user_money -= user_stavka
                        else:   #Проигравший
                            print("проигравший: " + str(user_id))
                            print(user_money)
                            #user_money -= round(user_stavka, 2)
                            user_money -= user_stavka
                        user_money = round(user_money, 3)
                        print(user_money)
                        cursor.execute("UPDATE users SET tokens = ? WHERE user_id = ?", (user_money, user_id))

                    ###
                    kicked = 0
                    if user_money < stavka_orig:  # Кончились бабки
                        await kick_player(user_id)
                        kicked = 1
                    # for i, player in enumerate(players_in_room['players']):
                    #     if player['userid'] == user:
                    #         if bet_type == 1:
                    #             player['money'] = user_money  # Допустим user_money - это обновленный баланс
                    #         elif bet_type == 2 or bet_type == 3:
                    #             player['tokens'] = user_money
                    #
                    #         players_in_room['players'][i] = player  # Обновляем данные игрока
                    #         break  # Выходим из цикла после нахождения и обновления пользователя

                    for i in range(len(players_in_room['players'])):
                        if players_in_room['players'][i]['userid'] == user_id:
                            if bet_type == 1:
                                players_in_room['players'][i]['money'] = user_money
                            elif bet_type == 3 or bet_type == 2:
                                players_in_room['players'][i]['tokens'] = user_money
                            # players = json.dumps(players_in_room)
                            # cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}", (players_in_room,))

                        # Сериализация обновленных данных комнаты
                    # room_data = json.dumps(players_in_room)
                    # cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?", (room_data, room_id))
                    ###

                    # db.commit()
                    # if db:
                    #     db.close()
                    # await edit_money_in_room(room_id, user_id, user_money)
                    if kicked == 0:
                        users[user]['coins'] = round(user_stavka, 2)
                    else:
                        users[user]['coins'] = "kicked"
                else:
                    pass

            with open('web_url.json', 'r', encoding='utf-8') as f:
                web_link = json.load(f)
            players_info = players_in_room['players']
            fc = players_info[0]['choice']
            sc = players_info[1]['choice']
            prev_fc = players_info[0]['prev_choice']
            prev_sc = players_info[1]['prev_choice']
            f_anim = web_link["url"] + "/cyefa_anim/l-" + prev_fc[0] + fc[0]
            s_anim = web_link["url"] + "/cyefa_anim/r-" + prev_sc[0] + sc[0]

            new_winner_value = str(users.get(str(winner_id), {}).get('coins', 0.0))

            print("SET_NEW WINNER_ID 1")
            print(winner_id)



            players_in_room['win']['winner_id'] = winner_id
            players_in_room['win']['f_anim'] = f_anim
            players_in_room['win']['s_anim'] = s_anim
            players_in_room['win']['users'] = users
            players_in_room['win']['winner_value'] = new_winner_value
            # players_in_room['win']['sended'] = ""

            #updated_data_json = json.dumps(players_in_room)
            room_data = json.dumps(players_in_room)
            cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?", (room_data, room_id))

            db.commit()
            print(users)
            return "ok", users
        else:
            return "alone_in_room", users
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error", users
    finally:
        if db:
            db.close()


async def edit_money_in_room(room_id: int, player_id: int, value: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = await get_room(room_id, 0)
        if r == None:
            return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}

        players = json.loads(r[1])
        bet_type = r[6]

        if(value < r[2]):
            #await kick_player(room_id,player_id)
            await kick_player(player_id)
            return {"message":"player_kicked","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}
        for i in range(len(players['players'])):
            if players['players'][i]['userid'] == player_id:
                if bet_type == 1:
                    players['players'][i]['money'] = value
                # elif bet_type == 2:
                #     players['players'][i]['tickets'] = value
                elif bet_type == 3 or bet_type == 2:
                     players['players'][i]['tokens'] = value
                players = json.dumps(players)
                cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}",(players,))
                db.commit()
                return {"message":"success","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}

        return {"message":"no_player","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def check_user_in_game(user_id):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        query = """
        SELECT COUNT(*)
        FROM rooms_rps
        WHERE in_room LIKE ?
        """

        # Убедимся, что шаблон соответствует формату данных в JSON.
        # Поскольку userid - это число, мы исключили кавычки вокруг него в шаблоне.
        user_id_pattern = f'%\"userid\": {user_id},%'
        cursor.execute(query, (user_id_pattern,))
        result = cursor.fetchone()[0]

        return 1 if result > 0 else 0
    except Exception as e:
        print(e)
        return "error"
    finally:
        if db:
            db.close()

async def edit_money_in_room(room_id: int, player_id: int, value: float):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = await get_room(room_id, 0)
        if r == None:
            return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}

        players = json.loads(r[1])
        bet_type = r[6]

        if(value < r[2]):
            #await kick_player(room_id,player_id)
            await kick_player(player_id)
            return {"message":"player_kicked","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}
        for i in range(len(players['players'])):
            if players['players'][i]['userid'] == player_id:
                if bet_type == 1:
                    players['players'][i]['money'] = value
                # elif bet_type == 2:
                #     players['players'][i]['tickets'] = value
                elif bet_type == 3 or bet_type == 2:
                     players['players'][i]['tokens'] = value
                players = json.dumps(players)
                cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}",(players,))
                db.commit()
                return {"message":"success","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}

        return {"message":"no_player","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def get_rooms():
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        rooms = []
        # Раскомментируйте следующую строку, чтобы отфильтровать комнаты с нулевыми свободными местами
        cursor.execute("SELECT * FROM rooms_rps WHERE free_places != 0")

        for room in cursor.fetchall():
            print(room)
            players_json = room[1]
            players_data = json.loads(players_json)
            players_list = players_data["players"]

            # Обновляем каждого игрока, добавляя его publicname
            for player in players_list:
                user_id = player['userid']
                cursor.execute("SELECT publicname FROM users WHERE user_id = ?", (user_id,))
                publicname = cursor.fetchone()
                if publicname:
                    player['public_name'] = publicname[
                        0]  # Берем первый элемент из результатов, так как fetchone() вернет кортеж

            rooms.append({
                "room_id": room[-2],
                "room_type": room[4],
                "bet": room[2],
                "bet_type": room[6],
                "free_places": room[5],
                "players": players_list,
                "players_count": room[3]
            })
        return {'rooms': rooms}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()

async def edit_misc_value(room_id,value):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute("UPDATE rooms_rps SET misc_value = (?) WHERE room_id = (?)",(f"{value}",room_id))
        db.commit()
        return 'ok'
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()
async def get_misc_value(room_id):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = cursor.execute('SELECT misc_value FROM rooms_rps WHERE room_id = (?)',(room_id,)).fetchone()
        return r[0]
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()
async def who_is_win_mel(room_id):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)',(room_id,))
        r = cursor.fetchone()
        bet_type = r[6]
        bet = r[2]
        value = await get_misc_value(room_id)
        if r == None:
            return {"message":"no_room","room_id":room_id}
        players = json.loads(r[1])
        players = players['players']
        players.sort(key = lambda x:abs(int(x['choice']) - int(value)))
        bet = bet*(len(players) - 3)
        for k,v in enumerate(players):
            if k == 0:
                if bet_type == 1:
                    await edit_money_in_room(room_id,v['userid'],v['money'] + bet*0.5*0.975)
                # elif bet_type == 2:
                #     await edit_money_in_room(room_id,v['userid'],v['tickets'] + bet*0.5*0.975)
                elif bet_type == 3 or bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] + bet*0.5*0.975)
            elif k == 1:
                if bet_type == 1:
                    await edit_money_in_room(room_id,v['userid'],v['money'] + bet*0.4*0.975)
                # elif bet_type == 2:
                #     await edit_money_in_room(room_id,v['userid'],v['tickets'] + bet*0.4*0.975)
                elif bet_type == 3 or bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] + bet*0.4*0.975)
            elif k == 2:
                if bet_type == 1:
                    await edit_money_in_room(room_id,v['userid'],v['money'] + bet*0.1*0.975)
                # elif bet_type == 2:
                #     await edit_money_in_room(room_id,v['userid'],v['tickets'] + bet*0.1*0.975)
                elif bet_type == 3 or bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] + bet*0.1*0.975)
            else:
                if bet_type == 1:
                    await edit_money_in_room(room_id,v['userid'],v['money'] - bet)
                # elif bet_type == 2:
                #     await edit_money_in_room(room_id,v['userid'],v['tickets'] - bet)
                elif bet_type == 3 or bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] - bet)
        return {"message":"success","players":players,"room_id":room_id}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()
async def polling_info(room_id,player_id,server):
    try:
        inf = await asyncio.wait_for(get_room_long_poling(room_id,player_id, server), timeout=120)
    except:
        inf = {"message":"timeout"}
        if inf == None:
            inf = {"message": "None"}
    return inf
