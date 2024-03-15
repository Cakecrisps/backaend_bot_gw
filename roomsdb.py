import sqlite3
import json
from bd import load_user_data
db = sqlite3.connect('rooms.db')
curs = db.cursor()
async def get_rooms_count():
    return len(curs.execute("SELECT * FROM rooms_sps").fetchall())
async def create_room(creatorid,bet):
    c = await load_user_data(creatorid,1)
    money = c['coins']
    if money > bet:
        print(str({creatorid:{"choise":None,"money":money}}))
        r_c = await get_rooms_count()
        curs.execute(
                    f"INSERT INTO rooms_sps VALUES (?,?,?,?)",(creatorid,json.dumps({"players":[{"userid":creatorid,"choise":None,"money":money},]}),float(bet),r_c + 1))
        db.commit()
        return {"message":"success","creator":creatorid,"room_id":r_c+1}
    else:
        return {"message":"not_enough_coins","creator":creatorid}
async def get_room(room_id : int):
    curs.execute('SELECT * FROM rooms_sps WHERE room_id = (?)',(room_id,))
    r = curs.fetchone()
    print(r)
    return r
async def who_is_win(room_id : int):
    curs.execute('SELECT * FROM rooms_sps WHERE room_id = (?)',(room_id,))
    r = curs.fetchone()
    if r:
        print(r)
        us = json.loads(r[1])
        players = us['players']
        if len(players) == 2:
            fc = players[0]['choise']
            sc = players[1]['choise']
            print(fc,sc)
            if fc == sc:
                return {"message":"success","winner":"draw","room_id":room_id}
            elif fc == "scissors" and sc == "paper":
                return {"message":"success","winner":players[0],"room_id":room_id}
            elif fc == "scissors" and sc == "stone":
                return {"message":"success","winner":players[1],"room_id":room_id}
            elif fc == "paper" and sc == "stone":
                return {"message":"success","winner":players[0],"room_id":room_id}
            elif fc == "paper" and sc == "scissors":
                return {"message":"success","winner":players[1],"room_id":room_id}
            elif fc == "stone" and sc == "paper":
                return {"message":"success","winner":players[1],"room_id":room_id}
            elif fc == "stone" and sc == "scissors":
                return {"message":"success","winner":players[0],"room_id":room_id}

            elif sc == "scissors" and fc == "paper":
                return {"message":"success","winner":players[1],"room_id":room_id}
            elif sc == "scissors" and fc == "stone":
                return {"message":"success","winner":players[0],"room_id":room_id}
            elif sc == "paper" and fc == "stone":
                return {"message":"success","winner":players[1],"room_id":room_id}
            elif sc == "paper" and fc == "scissors":
                return {"message":"success","winner":players[0],"room_id":room_id}
            elif sc == "stone" and fc == "paper":
                return {"message":"success","winner":players[0],"room_id":room_id}
            elif sc == "stone" and fc == "scissors":
                return {"message":"success","winner":players[1],"room_id":room_id}
        else:
            return {"message":"not_enough_player","room_id":room_id}
    else:
        return {"message":"room_is_not_valid","room_id":room_id}
async def add_player(room_id,player_id):
    r = await get_room(room_id)
    if r == None:
         return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}
    players = json.loads(r[1])
    c = await load_user_data(player_id,1)
    money = c['coins']
    if len(players['players']) != 2:
        players['players'].append({"userid":player_id,"choise":None,"money":money})
        players = json.dumps(players)
        curs.execute(f"UPDATE rooms_sps SET in_rooom = (?) WHERE room_id = {room_id}",(players,))
        db.commit()
        return {"message":"success","player_id":player_id,"room_id":room_id}
    #curs.execute('UPDATE users SET lang = "{new_lang}"')
    return {"message":"no_player","player_id":player_id,"room_id":room_id}
async def kick_player(room_id,player_id):
    r = await get_room(room_id)
    if r == None:
         return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}
    players = json.loads(r[1])
    for i in range(len(players['players'])):
        #print(players['players'][i])
        if players['players'][i]['userid'] == player_id:
            players['players'].pop(i)
            players = json.dumps(players)
            curs.execute(f"UPDATE rooms_sps SET in_rooom = (?) WHERE room_id = {room_id}",(players,))
            db.commit()
            return {"message":"success","player_id":player_id,"room_id":room_id}
    return {"message":"no_player","player_id":player_id,"room_id":room_id}
async def set_choise(room_id,player_id,choise):
    r = await get_room(room_id)
    if r == None:
        return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}
    players = json.loads(r[1])
    for i in range(len(players['players'])):
        if players['players'][i]['userid'] == player_id:
            players['players'][i]['choise'] = choise
            players = json.dumps(players)
            curs.execute(f"UPDATE rooms_sps SET in_rooom = (?) WHERE room_id = {room_id}",(players,))
            db.commit()
            return {"message":"success","player_id":player_id,"room_id":room_id,"choise":choise}
    return {"message":"no_player","player_id":player_id,"room_id":room_id,"choise":choise}
async def edit_money_in_room(room_id,player_id,coin):
    r = await get_room(room_id)
    if r == None:
        return {"message":"room_is_not_valid","player_id":player_id,"room_id":room_id}
    players = json.loads(r[1])
    for i in range(len(players['players'])):
        if players['players'][i]['userid'] == player_id:
            players['players'][i]['money'] = coin
            print(coin)
            players = json.dumps(players)
            curs.execute(f"UPDATE rooms_sps SET in_rooom = (?) WHERE room_id = {room_id}",(players,))
            db.commit()
            return {"message":"success","player_id":player_id,"room_id":room_id,"coin":coin}
    return {"message":"no_player","player_id":player_id,"room_id":room_id,"coin":coin}
