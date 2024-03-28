import json

import jwt
from quart import Quart, request, render_template, jsonify
import asyncio
from roomsdb import *
komis = 0.975
from bd import *
from quart_cors import cors
# Middleware для CORS
# async def add_cors_headers(response):
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
#     response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
#     return response
# Middleware для CORS
async def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'  # ✅ Добавлен заголовок
    return response

app = Quart(__name__)
app = cors(app)
SECRET_KEY = 'Jh3XrjcNhFXmLd69-tuX62BQivtiQq5Y7YL3VwSf5m8'  # Секретный ключ для подписи токена

app.after_request(add_cors_headers)

async def ngrok_start():
    process = await asyncio.create_subprocess_exec(
        'ngrok', 'http', '5000',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()


# Универсальная функция для проверки токена и выполнения специфической логики
async def token_auth_and_execute(request):
    token = request.headers.get('Authorization')
    if token is None:
        return "Missing token. Access denied."

    try:
        token
        token = token.split('Bearer ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        #return await specific_logic_func(request, payload)
        return "next"
    except jwt.ExpiredSignatureError:
        return "Expired token. Please obtain a new token."
    except jwt.InvalidTokenError:
        return "Invalid token. Access denied."



# код некоторый

@app.route("/")
async def hello():
    return await render_template('index.html')


# Другие маршруты...

# Маршрут для обработки /setcoinsnewvalue
@app.route('/setcoinsnewvalue', methods=['PUT'])
async def setcoinsnewvalue():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        print(request)
        user_id = int(request.args.get('user_id'))
        newcoins = float(request.args.get('newcoins'))
        coins = await new_coins(user_id, newcoins)
        return json.dumps({"message":"Ok"}),201 # Возвращаем корректный ответ

    return json.dumps({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку

# Маршрут для обработки /setcoinsnewvalue
@app.route('/getuserinfo', methods=['GET'])
async def getuserinfo():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        user_id = int(request.args.get('user_id'))
        info = await load_user_data(user_id, 1)
        return json.dumps({"info": info}),201  # Возвращаем корректный ответ

    return json.dumps({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку


@app.route('/createroom', methods=['POST'])
async def createroomsps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        creator_id = int(request.args.get('creator_id'))
        bet = int(request.args.get('bet'))
        bet_type = int(request.args.get('bet_type'))
        room_type = int(request.args.get('room_type'))
        inf = await create_room(creator_id,bet,room_type,bet_type)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/addplayer', methods=['PUT'])
async def addplayersps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        player_id = int(request.args.get('player_id'))
        inf = await add_player(room_id,player_id)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/kickplayer', methods=['PUT'])
async def kickplayersps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        player_id = int(request.args.get('player_id'))
        inf = await kick_player(room_id,player_id)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/setchoise', methods=['PUT'])
async def setchoisesps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        player_id = int(request.args.get('player_id'))
        choise = request.args.get('choise')
        inf = await set_choise(room_id,player_id,choise)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/whoiswin', methods=['GET'])
async def whoiswin():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        r = await get_room(room_id)
        if r[4] == 1:
            inf = await who_is_win_sps(room_id)
            print(inf)
            if inf['winner'] != 'draw':
                winner_id = inf['winner']['userid']
                loser_id = inf['loser']['userid']
                winner = await load_user_data(winner_id,1)
                loser =  await load_user_data(loser_id,1)
                if r[6] == 1:
                    await new_coins(winner_id,round(r[2]*komis + winner['coins'],1))
                    await edit_money_in_room(room_id,winner_id,round(r[2]*komis + winner['coins'],1))
                    await edit_money_in_room(room_id,loser_id,loser['coins'] - r[2])
                    await new_coins(loser_id,loser['coins'] - r[2])
                elif r[6] == 2:
                    await new_tickets(winner_id,round(r[2]*komis + winner['tickets'],1))
                    await edit_money_in_room(room_id,winner_id,round(r[2]*komis + winner['tickets'],1))
                    await edit_money_in_room(room_id,loser_id,loser['tickets'] - r[2])
                    await new_tickets(loser_id,loser['tickets'] - r[2])
                elif r[6] == 3:
                    await new_tokens(winner_id,round(r[2]*komis + winner['tokens'],1))
                    await edit_money_in_room(room_id,winner_id,round(r[2]*komis + winner['tokens'],1))
                    await edit_money_in_room(room_id,loser_id,loser['tokens'] - r[2])
                    await new_tokens(loser_id,loser['tokens'] - r[2])
        elif r[4] == 2:
            inf = await who_is_win_mel(room_id)
            return json.dumps(inf)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/getrooms', methods=['GET'])
async def getroomssps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        min_bet = float(request.args.get('min_bet'))
        max_bet = float(request.args.get('max_bet'))
        game_types = list(map(int,str(request.args.get('game_types')).split(',')))
        bet_type = int(request.args.get('bet_type'))
        inf = await get_rooms(min_bet,max_bet,game_types,bet_type)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


# @app.route('/setcoinsnewvalue', methods=['GET'])
# async def setcoinsnewvalue():
#     user_id = int(request.args.get('user_id'))
#     newcoins = float(request.args.get('newcoins'))
#
#     token = request.headers.get('Authorization')
#
#     print(str(token))
#
#     if token is None:
#         return "Missing token. Access denied."
#
#     try:
#         token = token.split('Bearer ')[1]
#         print(str(token))
#         payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#
#         coins = await new_coins(user_id, newcoins)
#         return "ok"
#
#     except jwt.ExpiredSignatureError:
#         return "Expired token. Please obtain a new token."
#
#     except jwt.InvalidTokenError:
#         return "Invalid token. Access denied."


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(ngrok_start())
    app.run()

####Рабочий код:

# from quart import Quart, request, render_template, jsonify
# import asyncio
# from bd import *
#
# app = Quart(__name__)
#
# async def ngrok_start():
#     process = await asyncio.create_subprocess_exec(
#         'ngrok', 'http', '5000',
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE
#     )
#     stdout, stderr = await process.communicate()
#
# @app.route("/")
# async def hello():
#     return await render_template('index.html')
#
# @app.route('/getuserinfo', methods=['GET'])
# async def getuserinfo():
#     user_id = int(request.args.get('user_id'))
#     info = await load_user_data(user_id, 1)
#     return jsonify({"info": info})  # Возвращаем корректный ответ
#
# @app.route('/setcoinsnewvalue', methods=['GET'])
# async def setcoinsnewvalue():
#     user_id = int(request.args.get('user_id'))
#     newcoins = float(request.args.get('newcoins'))
#     coins = await new_coins(user_id, newcoins)
#     return "ok"
#
# @app.route('/settokensnewvalue', methods=['GET'])
# async def settokensnewvalue():
#     user_id = int(request.args.get('user_id'))
#     newtokens = float(request.args.get('newtokens'))
#     tokens = await new_tokens(user_id, newtokens)
#     return "ok"
#
# @app.route('/settiketsnewvalue', methods=['GET'])
# async def settiketsnewvalue():
#     user_id = int(request.args.get('user_id'))
#     newtikets = int(request.args.get('newtikets'))
#     tikets = await new_tickets(user_id, newtikets)
#     return "ok"
#
# @app.route('/setroomidvalue', methods=['GET'])
# async def setroomidvalue():
#     user_id = int(request.args.get('user_id'))
#     room_id = int(request.args.get('room_id'))
#     new = await new_room_id(user_id, room_id)
#     return "ok"
#
# @app.route('/setcollectibles', methods=['GET'])
# async def setcollectibles():
#     user_id = int(request.args.get('user_id'))
#     collectibles = str(request.args.get('collectibles'))
#     new = await new_collectibles(user_id, collectibles)
#     return "ok"
#
# @app.route('/setactive_skin', methods=['GET'])
# async def setactive_skin():
#     user_id = int(request.args.get('user_id'))
#     active_skin = int(request.args.get('active_skin'))
#     new = await new_active_skin(user_id, active_skin)
#     return "ok"
#
# @app.route('/setdays_online', methods=['GET'])
# async def setdays_online():
#     user_id = int(request.args.get('user_id'))
#     days_online = int(request.args.get('days_online'))
#     new = await new_days_online(user_id, days_online)
#     return "ok"
#
# @app.route('/setall_games_played_count', methods=['GET'])
# async def setall_games_played_count():
#     user_id = int(request.args.get('user_id'))
#     all_games_played_count = int(request.args.get('all_games'))
#     new = await new_all_games_played_count(user_id, all_games_played_count)
#     return "ok"
#
# @app.route('/setwins', methods=['GET'])
# async def setwins():
#     user_id = int(request.args.get('user_id'))
#     wins = int(request.args.get('wins'))
#     new = await new_wins(user_id, wins)
#     return "ok"
#
# @app.route('/setloses', methods=['GET'])
# async def setloses():
#     user_id = int(request.args.get('user_id'))
#     loses = int(request.args.get('loses'))
#     new = await new_loses(user_id, loses)
#     return "ok"
#
# @app.route('/settokenwins', methods=['GET'])
# async def settokenwins():
#     user_id = int(request.args.get('user_id'))
#     tokenwins = int(request.args.get('tokenwins'))
#     new = await new_tokenwins(user_id, tokenwins)
#     return "ok"
#
# @app.route('/settokenloses', methods=['GET'])
# async def settokenloses():
#     user_id = int(request.args.get('user_id'))
#     tokenloses = int(request.args.get('tokenloses'))
#     new = await new_tokenloses(user_id, tokenloses)
#     return "ok"
#
# @app.route('/setcoinwins', methods=['GET'])
# async def setcoinwins():
#     user_id = int(request.args.get('user_id'))
#     coinwins = int(request.args.get('coinwins'))
#     new = await new_coinwins(user_id, coinwins)
#     return "ok"
#
# @app.route('/setcoinloses', methods=['GET'])
# async def setcoinloses():
#     user_id = int(request.args.get('user_id'))
#     coinloses = int(request.args.get('coinloses'))
#     new = await new_coinloses(user_id, coinloses)
#     return "ok"
#
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.create_task(ngrok_start())
#     app.run()
