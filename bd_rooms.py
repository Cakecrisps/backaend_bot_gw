import sqlite3
import json
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


async def create_room(creatorid,bet,room_type,bet_type):
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

        if bet_type == 1:
            pass
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

            cursor.execute(f"INSERT INTO rooms_rps VALUES (?,?,?,?,?,?,?,?,?)",(creatorid,json.dumps({"players":[{"userid":creatorid,"choice":"none","money":money,"tickets":tickets,"tokens":tokens},]}),float(bet),1,room_type,free_places,bet_type,value,r_c + 1))
            #cursor.execute(f"INSERT INTO rooms_rps VALUES (?,?,?,?,?,?,?,?)",(creatorid,json.dumps({"players":[{"userid":creatorid,"choice":None,"money":money,"tickets":tickets,"tokens":tokens},]}),float(bet),1,room_type,free_places,bet_type,r_c + 1))
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


async def get_room(room_id : int, server: int):
    try:
        print("222")
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        if server == 0:
            cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)',(room_id,))
            r = cursor.fetchone()
            print(r)
            return r
        else:
            print("3")
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

                print("4")

                # Вот тут мы добавим информацию о каждом игроке
                for player in in_room_data['players']:
                    print(player['userid'])
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

                return {**in_room_data, **data}
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def who_is_win_sps(room_id : int):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        cursor.execute('SELECT * FROM rooms_rps WHERE room_id = (?)',(room_id,))
        r = cursor.fetchone()
        if r:
            print(r)
            us = json.loads(r[1])
            players = us['players']
            if len(players) != 1 and r[4] == 1:
                fc = players[0]['choice']
                sc = players[1]['choice']
                print(fc,sc)
                if fc == sc:
                    return {"message":"success","winner":"draw","room_id":room_id}
                elif fc == "scissors" and sc == "paper":
                    return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
                elif fc == "scissors" and sc == "rock":
                    return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
                elif fc == "paper" and sc == "rock":
                    return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
                elif fc == "paper" and sc == "scissors":
                    return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
                elif fc == "rock" and sc == "paper":
                    return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
                elif fc == "rock" and sc == "scissors":
                    return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}

                elif sc == "scissors" and fc == "paper":
                    return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
                elif sc == "scissors" and fc == "rock":
                    return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
                elif sc == "paper" and fc == "rock":
                    return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
                elif sc == "paper" and fc == "scissors":
                    return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
                elif sc == "rock" and fc == "paper":
                    return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
                elif sc == "rock" and fc == "scissors":
                    return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
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

        r = await get_room(room_id, 0)
        if r == None:
             return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}

        players = json.loads(r[1])
        # c = await load_user_data(player_id,1)
        # money = c['coins']
        # tickets = c['tickets']
        # tokens = c['tokens']

        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (player_id,))
        user_db = cursor.fetchone()
        tokens = float(user_db[2])
        money = float(user_db[3])
        tickets = int(user_db[4])

        if r[6] == 1 and money < r[2]:
            return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
        elif r[6] == 2 and tickets < r[2]:
            return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
        elif r[6] == 3 and tokens < r[2]:
            return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
        if r[5] != 0:
            players['players'].append({"userid":player_id,"choice":"none","money":money,"tickets":tickets,"tokens":tokens})
            players = json.dumps(players)
            cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}",(players,))
            cursor.execute(f"UPDATE rooms_rps SET players_count = (?) WHERE room_id = {room_id}",(r[3]+1,))
            cursor.execute(f"UPDATE rooms_rps SET free_places = (?) WHERE room_id = {room_id}",(r[5] - 1,))
            db.commit()
            return {"message":"success","player_id":player_id,"room_id":room_id}
        return {"message":"no_places","player_id":player_id,"room_id":room_id}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()


async def kick_player(room_id,player_id):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = await get_room(room_id, 0)
        if r == None:
             return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}

        players = json.loads(r[1])

        for i in range(len(players['players'])):
            #print(players['players'][i])
            if players['players'][i]['userid'] == player_id:
                players['players'].pop(i)
                players = json.dumps(players)
                cursor.execute(f"UPDATE rooms_rps SET in_room = (?) WHERE room_id = {room_id}",(players,))
                cursor.execute(f"UPDATE rooms_rps SET players_count = (?) WHERE room_id = {room_id}",(r[3]-1,))
                cursor.execute(f"UPDATE rooms_rps SET free_places = (?) WHERE room_id = {room_id}",(r[5] + 1,))
                db.commit()
                return {"message":"success","player_id":player_id,"room_id":room_id}

        return {"message":"no_player","player_id":player_id,"room_id":room_id}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
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
                player['choice'] = 'none'
        else:
            any_not_ready = any(player['choice'] == 'none' for player in players['players'])
            # Обновляем статус текущего игрока
            for player in players['players']:
                if player['userid'] == player_id:
                    if choice != 'ready' and any_not_ready:
                        # Если кто-то не готов и выбор не 'ready', отменяем ход
                        return {"message": "player_not_ready", "player_id": player_id, "room_id": room_id}
                    else:
                        # В противном случае обновляем 'choice'
                        player['choice'] = choice
                        break

        players_serialized = json.dumps(players)
        cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?", (players_serialized, room_id))
        db.commit()
        return {"message": "success", "player_id": player_id, "room_id": room_id, "choice": choice}

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


async def edit_money_in_room(room_id,player_id,value):
    try:
        db = sqlite3.connect(f"{dbn}.db")
        cursor = db.cursor()

        r = await get_room(room_id, 0)
        if r == None:
            return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}

        players = json.loads(r[1])
        bet_type = r[6]

        if(value < r[2]):
            await kick_player(room_id,player_id)
            return {"message":"player_kicked","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}
        for i in range(len(players['players'])):
            if players['players'][i]['userid'] == player_id:
                if bet_type == 1:
                    players['players'][i]['money'] = value
                elif bet_type == 2:
                    players['players'][i]['tickets'] = value
                elif bet_type == 3:
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
                    player['public_name'] = publicname[0]  # Берем первый элемент из результатов, так как fetchone() вернет кортеж

            rooms.append({
                "room_id": room[-1],
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
                elif bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tickets'] + bet*0.5*0.975)
                elif bet_type == 3:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] + bet*0.5*0.975)
            elif k == 1:
                if bet_type == 1:
                    await edit_money_in_room(room_id,v['userid'],v['money'] + bet*0.4*0.975)
                elif bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tickets'] + bet*0.4*0.975)
                elif bet_type == 3:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] + bet*0.4*0.975)
            elif k == 2:
                if bet_type == 1:
                    await edit_money_in_room(room_id,v['userid'],v['money'] + bet*0.1*0.975)
                elif bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tickets'] + bet*0.1*0.975)
                elif bet_type == 3:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] + bet*0.1*0.975)
            else:
                if bet_type == 1:
                    await edit_money_in_room(room_id,v['userid'],v['money'] - bet)
                elif bet_type == 2:
                    await edit_money_in_room(room_id,v['userid'],v['tickets'] - bet)
                elif bet_type == 3:
                    await edit_money_in_room(room_id,v['userid'],v['tokens'] - bet)
        return {"message":"success","players":players,"room_id":room_id}
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"
    finally:
        if db:
            db.close()
