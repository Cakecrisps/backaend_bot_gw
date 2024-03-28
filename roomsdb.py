import random
import sqlite3
import json
from bd import load_user_data
db = sqlite3.connect('rooms.db')
curs = db.cursor()


async def get_rooms_count():
    return len(curs.execute("SELECT * FROM rooms_sps").fetchall())


async def create_room(creatorid,bet,room_type,bet_type):
    c = await load_user_data(creatorid,1)
    money = c['coins']
    tokens = c['tokens']
    tickets = c['tickets']
    if money > bet:
        print(str({creatorid:{"choise":None,"money":money}}))
        r_c = await get_rooms_count()

        if room_type == 1:
            free_places = 1
            value = '-'
        else:
            free_places = 7
            value = f"{random.randint(1,100)}"

        curs.execute(f"INSERT INTO rooms_sps VALUES (?,?,?,?,?,?,?,?,?)",(creatorid,json.dumps({"players":[{"userid":creatorid,"choise":None,"money":money,"tickets":tickets,"tokens":tokens},]}),float(bet),1,room_type,free_places,bet_type,value,r_c + 1))
        db.commit()
        return {"message":"success","creator":creatorid,"room_id":r_c+1}
    else:
        return {"message":"not_enough_coins","creator":creatorid}


async def get_room(room_id : int):
    curs.execute('SELECT * FROM rooms_sps WHERE room_id = (?)',(room_id,))
    r = curs.fetchone()
    print(r)
    return r


async def who_is_win_sps(room_id : int):
    curs.execute('SELECT * FROM rooms_sps WHERE room_id = (?)',(room_id,))
    r = curs.fetchone()
    if r:
        print(r)
        us = json.loads(r[1])
        players = us['players']
        if len(players) != 1 and r[4] == 1:
            fc = players[0]['choise']
            sc = players[1]['choise']
            print(fc,sc)
            if fc == sc:
                return {"message":"success","winner":"draw","room_id":room_id}
            elif fc == "scissors" and sc == "paper":
                return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
            elif fc == "scissors" and sc == "stone":
                return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
            elif fc == "paper" and sc == "stone":
                return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
            elif fc == "paper" and sc == "scissors":
                return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
            elif fc == "stone" and sc == "paper":
                return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
            elif fc == "stone" and sc == "scissors":
                return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}

            elif sc == "scissors" and fc == "paper":
                return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
            elif sc == "scissors" and fc == "stone":
                return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
            elif sc == "paper" and fc == "stone":
                return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
            elif sc == "paper" and fc == "scissors":
                return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
            elif sc == "stone" and fc == "paper":
                return {"message":"success","winner":players[0],"loser":players[1],"room_id":room_id}
            elif sc == "stone" and fc == "scissors":
                return {"message":"success","winner":players[1],"loser":players[0],"room_id":room_id}
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
    tickets = c['tickets']
    tokens = c['tokens']
    if r[6] == 1 and money < r[2]:
        return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
    elif r[6] == 2 and tickets < r[2]:
        return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
    elif r[6] == 3 and tokens < r[2]:
        return {"message":"not_enough_money","player_id":player_id,"room_id":room_id}
    if r[5] != 0:
        players['players'].append({"userid":player_id,"choise":None,"money":money,"tickets":tickets,"tokens":tokens})
        players = json.dumps(players)
        curs.execute(f"UPDATE rooms_sps SET in_rooom = (?) WHERE room_id = {room_id}",(players,))
        curs.execute(f"UPDATE rooms_sps SET players_count = (?) WHERE room_id = {room_id}",(r[3]+1,))
        curs.execute(f"UPDATE rooms_sps SET free_places = (?) WHERE room_id = {room_id}",(r[5] - 1,))
        db.commit()
        return {"message":"success","player_id":player_id,"room_id":room_id}
    return {"message":"no_places","player_id":player_id,"room_id":room_id}


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
            curs.execute(f"UPDATE rooms_sps SET players_count = (?) WHERE room_id = {room_id}",(r[3]-1,))
            curs.execute(f"UPDATE rooms_sps SET free_places = (?) WHERE room_id = {room_id}",(r[5] + 1,))
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


async def edit_money_in_room(room_id,player_id,value):
    r = await get_room(room_id)
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
            curs.execute(f"UPDATE rooms_sps SET in_rooom = (?) WHERE room_id = {room_id}",(players,))
            db.commit()
            return {"message":"success","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}

    return {"message":"no_player","player_id":player_id,"room_id":room_id,"value":value,"bet_type":bet_type}


async def get_rooms(min_bet,max_bet,game_types,bet_type):
    rooms = []
    for j in game_types:
        print(j)
        curs.execute(f"SELECT * FROM rooms_sps WHERE free_places != {0} AND bet > {min_bet} AND bet < {max_bet} AND room_type = {j} AND bet_type = {bet_type}")
        for i in curs.fetchall():
            print(i)
            rooms.append({"room_id":i[-1],"bet":i[2],"free_places":i[5],"players":i[1],"players_count":i[3]})
    return {"min_bet":min_bet,"max_bet":max_bet,"game_types":game_types,"bet_type":bet_type,'rooms':rooms}

async def edit_misc_value(room_id,value):
    curs.execute("UPDATE rooms_sps SET misc_value = (?) WHERE room_id = (?)",(f"{value}",room_id))
    db.commit()
    return 'Ok'
async def get_misc_value(room_id):
    r = curs.execute('SELECT misc_value FROM rooms_sps WHERE room_id = (?)',(room_id,)).fetchone()
    return r[0]
async def who_is_win_mel(room_id):
    curs.execute('SELECT * FROM rooms_sps WHERE room_id = (?)',(room_id,))
    r = curs.fetchone()
    bet_type = r[6]
    bet = r[2]
    value = await get_misc_value(room_id)
    if r == None:
        return {"message":"no_room","room_id":room_id}
    players = json.loads(r[1])
    players = players['players']
    players.sort(key = lambda x:abs(int(x['choise']) - int(value)))
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
