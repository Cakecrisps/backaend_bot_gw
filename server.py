import binascii
import PIL
import jwt
from quart import Quart, request, render_template, jsonify, Response, send_file,websocket
import asyncio
from quart_cors import cors
from io import BytesIO
from PIL import Image
import base64
import io
# from bd import *
from bd_items import *
from bd_rooms import *

komis = 0.975

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
        return "next"
    except jwt.ExpiredSignatureError:
        return "Expired token. Please obtain a new token."
    except jwt.InvalidTokenError:
        return "Invalid token. Access denied."


@app.route("/")
async def hello():
    return await render_template('index.html')



# Маршрут для обработки /setcoinsnewvalue
@app.route('/get_start_info', methods=['GET'])
async def get_start_info_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))

            user_info = await load_user_data(user_id, 1)

            shop_available = await get_shop_available_new()

            lavka_available = await get_lavka_available()

            print("load_bonus")

            daily_bonus = await get_daily_check(user_id)

            collectibles_data = await load_collectibles_data()

            #return jsonify({"user_info": user_info, "shop_available": shop_available, "lavka_available": lavka_available, "daily_bonus": daily_bonus, "collectibles_data": collectibles_data}),201  # Возвращаем корректный ответ
            return jsonify(
                {"user_info": user_info, "shop_available": shop_available, "lavka_available": lavka_available,
                 "daily_bonus": daily_bonus,
                 "collectibles_data": collectibles_data}), 201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/getuserinfo', methods=['GET'])
async def getuserinfo():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            info = await load_user_data(user_id, 1)
            return jsonify({"info": info}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

# @app.route('/image1.jpeg')
# async def serve_image():
#     image_path = 'image1.jpg'
#     response = await send_file(image_path, mimetype='image/jpeg')
#     return response

@app.route('/avatar/<int:user_id>', methods=['GET'])
async def get_avatar(user_id):
    try:
    # next_step = await token_auth_and_execute(request)
    # if next_step == "next":
        image_data = await load_user_data(user_id, 2)
        if image_data == "":
            image_path = 'bot_settings/media/default_pics/a_man.jpg'
            response = await send_file(image_path, mimetype='image/jpeg')
            return response
        else:
            image_binary = BytesIO(image_data)
            response = await send_file(image_binary, mimetype='image/jpeg', as_attachment=False)
            return response
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"


@app.route('/getuserphoto', methods=['GET'])
async def getuserphoto_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            with open('web_url.json', 'r', encoding='utf-8') as f:
                web_link = json.load(f)
            photo_url = web_link["url"] + "/avatar/" + str(user_id)
            print(photo_url)
            return jsonify({"info": photo_url}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/emoji/<int:packid>/<int:emotion>', methods=['GET'])
async def get_emoji_link(packid, emotion):
    try:
        imagedata = await get_emoji_db(packid, emotion)
        if imagedata == "error":
            # Обработка ошибки, возможно, возвращая какой-то статус ошибки
            # или сообщение пользователю.
            return "error"
        else:
            imagebinary = BytesIO(imagedata)
            response = await send_file(imagebinary, mimetype='image/png', as_attachment=False)
            return response
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"

@app.route('/getemojiphoto', methods=['GET'])
async def getemojiphoto_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            pack_id = int(request.args.get('pack_id'))
            emotion_id = int(request.args.get('emotion_id'))
            with open('web_url.json', 'r', encoding='utf-8') as f:
                web_link = json.load(f)
            photo_url = web_link["url"] + "/emoji/" + str(pack_id) + "/" + str(emotion_id)
            return jsonify({"info": photo_url}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/get_item_image/<int:item_id>', methods=['GET'])                 ##################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Почему то показывает socket.send() raised exception.
async def get_item_image_link(item_id):
    try:
        imagedata = await get_item_image_db(item_id, "pic")
        if imagedata == "error":
            # Обработка ошибки, возможно, возвращая какой-то статус ошибки
            # или сообщение пользователю.
            return "error"
        else:
            imagebinary = BytesIO(imagedata)
            # response = await send_file(imagebinary, mimetype='image/png', as_attachment=False)
            # return response
            try:
                response = await send_file(imagebinary, mimetype='image/png', as_attachment=False)
                return response
            except Exception as e:
                print(f"Ошибка отправки файла: {e}")
                return Response("Internal Server Error", status=500)
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"

@app.route('/get_item_image_mask/<int:item_id>', methods=['GET'])                 ##################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Почему то показывает socket.send() raised exception.
async def get_item_image_mask_link(item_id):
    try:
        imagedata = await get_item_image_db(item_id, "mask")
        if imagedata == "error":
            # Обработка ошибки, возможно, возвращая какой-то статус ошибки
            # или сообщение пользователю.
            return "error"
        else:
            imagebinary = BytesIO(imagedata)
            # response = await send_file(imagebinary, mimetype='image/png', as_attachment=False)
            # return response
            try:
                response = await send_file(imagebinary, mimetype='image/png', as_attachment=False)
                return response
            except Exception as e:
                print(f"Ошибка отправки файла: {e}")
                return Response("Internal Server Error", status=500)
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"

@app.route('/get_shop_available', methods=['GET'])
async def get_shop_available_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            info = await get_shop_available_new()
            return jsonify({"shop": info}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/get_lavka_available', methods=['GET'])
async def get_lavka_available_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            info = await get_lavka_available()
            return jsonify({"lavka": info}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/load_collectibles_data', methods=['GET'])
async def load_collectibles_data_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            info = await load_collectibles_data()
            return jsonify({"collectibles": info}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/get_daily_check', methods=['GET'])
async def get_daily_check_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            info = await get_daily_check(user_id)
            return jsonify({"bonus": info}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/shop_buy_item', methods=['PUT'])
async def shop_buy_item_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            item_id = int(request.args.get('item_id'))
            buy_count = int(request.args.get('count'))
            buy = await shop_buy_item(user_id, item_id, buy_count)
            print(buy)
            return jsonify({"message": buy}), 201  # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/set_daily_zero', methods=['PUT'])
async def set_daily_zero_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            set_zero = await set_daily_zero(user_id)
            return jsonify({"message":"Ok"}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setcoinsnewvalue', methods=['PUT'])
async def setcoinsnewvalue():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            newcoins = float(request.args.get('newcoins'))
            coins = await new_coins(user_id, newcoins)
            return jsonify({"message":"Ok"}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/settokensnewvalue', methods=['PUT'])
async def settokensnewvalue():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            newtokens = float(request.args.get('newtokens'))
            tokens = await new_tokens(user_id, newtokens)
            return jsonify({"message":"Ok"}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498


@app.route('/setticketsnewvalue', methods=['PUT'])
async def setticketsnewvalue():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            newtickets = int(request.args.get('newtickets'))
            tickets = await new_tickets(user_id, newtickets)
            return jsonify({"message":"Ok"}),201 # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/add_exp', methods=['PUT'])
async def add_exp_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            new_exp_add = float(request.args.get('new_exp'))
            get_exp = await new_exp(user_id, new_exp_add)
            return jsonify({"message":get_exp}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498


@app.route('/add_sell_lavka', methods=['PUT'])
async def add_sell_lavka_url():
    try:
        print(request)
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            item_id = int(request.args.get('item_id'))
            price = float(request.args.get('price'))
            sell = await add_sell_lavka(user_id, item_id, price)
            return jsonify({"message":sell}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/buy_lavka', methods=['PUT'])
async def buy_lavka_url():
    try:
        print(request)
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            nft_id = int(request.args.get('nft_id'))
            buy = await lavka_buy_item(user_id, nft_id)
            return jsonify({"message":buy}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/cancel_sell_lavka', methods=['PUT'])
async def cancel_sell_lavka_url():
    try:
        print(request)
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            item_id = int(request.args.get('item_id'))
            buy = await lavka_sell_cancel(user_id, item_id)
            return jsonify({"message":buy}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/get_refs_info', methods=['GET'])  #Получить список друзей и кол-во сколько они принесли
async def get_refs_info_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            result_data = await get_refs_info(user_id)
            return jsonify({"result_data": result_data}), 201  # Возвращаем корректный ответ

            return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/get_leaderboard_top_users', methods=['GET'])  #Получить список друзей и кол-во сколько они принесли
async def get_leaderboard_top_users_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            top_users = await get_leaderboard_top_users()
            return jsonify({"top_users": top_users}), 201  # Возвращаем корректный ответ

            return jsonify({"error": next_step}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/transfer_refs_to_balance', methods=['PUT'])  #Забрать накопившиеся коины на баланс
async def transfer_refs_to_balance_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            user_coins, total_balance = await transfer_refs_to_balance(user_id)
            return jsonify({"new_coins":str(user_coins), "transfered":str(total_balance)}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/add_refs_coins', methods=['PUT'])  # Добавить тому, кто пригласил юзера процент за катку
async def add_refs_coins_url():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            add_refs_coins = float(request.args.get('add_refs_coins'))
            coins = await add_refs_coins_count(user_id, add_refs_coins)
            return jsonify({"message": coins}),201 # Возвращаем корректный ответ

        return jsonify({"message":"TokenIsNotValid"}),498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setroomidvalue', methods=['PUT'])
async def setroomidvalue():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            room_id = int(request.args.get('room_id'))
            new = await new_room_id(user_id, room_id)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/add_collectible', methods=['PUT'])
async def setcollectibles_url():
    print(request)
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            collectibles = int(request.args.get('add_collectible'))
            count = request.args.get('count')
            if count == "" or count == "None" or count == None:
                count = 1
            else:
                count = int(count)
            new = await new_collectibles(user_id, collectibles, count)
            return jsonify({"message": new}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setactive_skin', methods=['PUT'])
async def setactive_skin():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            active_skin = int(request.args.get('active_skin'))
            new = await new_active_skin(user_id, active_skin)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498  # Возвращаем сообщение об ошибке, если токен не прошел проверку
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setactive_emoji', methods=['PUT'])
async def setactive_emoji():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            active_emoji = int(request.args.get('active_emoji'))
            new = await new_active_emoji(user_id, active_emoji)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setdays_online', methods=['PUT'])
async def setdays_online():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            days_online = int(request.args.get('days_online'))
            new = await new_days_online(user_id, days_online)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setall_games_played_count', methods=['PUT'])
async def setall_games_played_count():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            all_games_played_count = int(request.args.get('all_games'))
            new = await new_all_games_played_count(user_id, all_games_played_count)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setwins', methods=['PUT'])
async def setwins():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            wins = int(request.args.get('wins'))
            new = await new_wins(user_id, wins)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setloses', methods=['PUT'])
async def setloses():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            loses = int(request.args.get('loses'))
            new = await new_loses(user_id, loses)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/settokenwins', methods=['PUT'])
async def settokenwins():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            tokenwins = int(request.args.get('tokenwins'))
            new = await new_tokenwins(user_id, tokenwins)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498


@app.route('/settokenloses', methods=['PUT'])
async def settokenloses():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            tokenloses = int(request.args.get('tokenloses'))
            new = await new_tokenloses(user_id, tokenloses)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setcoinwins', methods=['PUT'])
async def setcoinwins():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            coinwins = int(request.args.get('coinwins'))
            new = await new_coinwins(user_id, coinwins)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setcoinloses', methods=['PUT'])
async def setcoinloses():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            coinloses = int(request.args.get('coinloses'))
            new = await new_coinloses(user_id, coinloses)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

################################ ТОВАРЫ:
@app.route('/getitemdata', methods=['GET'])
async def getitemdata():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            item_id = int(request.args.get('item_id'))
            info = await load_item_data(item_id, 1)
            return jsonify({"info": info}),201  # Возвращаем корректный ответ

        return jsonify({"error": next_step}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

@app.route('/setitem_count', methods=['PUT'])
async def setitem_count():
    try:
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            item_id = int(request.args.get('item_id'))
            item_count = int(request.args.get('item_count'))
            new = await item_count_change(item_id, item_count)
            return jsonify({"message": "Ok"}), 201  # Возвращаем корректный ответ

        return jsonify({"message": "TokenIsNotValid"}), 498
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "error"}), 498

################################ ТОВАРЫ

################################ GAMES

@app.route('/createroom', methods=['POST'])
async def createroomsps():
    print(request)
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        data = await request.json
        # creator_id = int(data['user_id'])
        # bet = int(data['bet'])
        # bet_type = int(data['bet_type'])
        # room_type = int(data['room_type'])

        creator_id = int(request.args.get('user_id'))
        bet = float(request.args.get('bet'))
        bet_type = int(request.args.get('bet_type'))
        room_type = int(request.args.get('room_type'))

        inf = await create_room(creator_id, bet, room_type, bet_type)
        print(inf)

        # Тестово присоединяем Марка
        new_room_id = inf.get('room_id')
        #add = await add_player(new_room_id, 5858080651)
        add = await add_player(new_room_id, "5858080651")
        print("addplayer:")
        print(add)
        # Тестово присоединяем Марка

        return jsonify(inf), 200

    return jsonify({"error": next_step}), 498

@app.route('/getrooms', methods=['GET'])
async def getroomssps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        # min_bet = float(request.args.get('min_bet'))
        # max_bet = float(request.args.get('max_bet'))
        # game_types = list(map(int,str(request.args.get('game_types')).split(',')))
        # bet_type = int(request.args.get('bet_type'))
        #inf = await get_rooms(min_bet,max_bet,game_types,bet_type)
        inf = await get_rooms()
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498

@app.route('/getroominfo', methods=['GET'])
async def getroominfosps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        print("111")
        inf = await get_room(room_id, 1)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498

@app.route('/addplayer', methods=['PUT'])
async def addplayersps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        player_id = int(request.args.get('user_id'))
        room_id = int(request.args.get('room_id'))
        inf = await add_player(room_id,player_id)
        return jsonify({"message": inf}), 201  # Возвращаем корректный ответ
        #return json.dumps(inf),200

    #return json.dumps({"error": next_step}), 498
    return jsonify({"error": next_step}), 498


@app.route('/kickplayer', methods=['PUT'])
async def kickplayersps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        player_id = int(request.args.get('user_id'))
        room_id = int(request.args.get('room_id'))
        inf = await kick_player(room_id,player_id)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/setchoice', methods=['PUT'])
async def setchoicesps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        player_id = int(request.args.get('user_id'))
        room_id = int(request.args.get('room_id'))
        choice = request.args.get('choice')
        inf = await set_choice(room_id,player_id,choice)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/whoiswin', methods=['GET'])
async def whoiswin():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        r = await get_room(room_id,0)
        if r[4] == 1:   #Цу-Е-Фа
            inf = await who_is_win_sps(room_id)
            print(inf)
            if inf['winner'] != 'draw':
                winner_id = inf['winner']['userid']
                loser_id = inf['loser']['userid']
                winner = await load_user_data(winner_id, 1)
                loser = await load_user_data(loser_id, 1)
                if r[6] == 1:
                    await new_coins(winner_id, round(r[2] * komis + winner['coins'], 1))
                    await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['coins'], 1))
                    await edit_money_in_room(room_id, loser_id, loser['coins'] - r[2])
                    await new_coins(loser_id, loser['coins'] - r[2])
                elif r[6] == 2:
                    await new_tickets(winner_id, round(r[2] * komis + winner['tickets'], 1))
                    await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['tickets'], 1))
                    await edit_money_in_room(room_id, loser_id, loser['tickets'] - r[2])
                    await new_tickets(loser_id, loser['tickets'] - r[2])
                elif r[6] == 3:
                    await new_tokens(winner_id, round(r[2] * komis + winner['tokens'], 1))
                    await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['tokens'], 1))
                    await edit_money_in_room(room_id, loser_id, loser['tokens'] - r[2])
                    await new_tokens(loser_id, loser['tokens'] - r[2])
        elif r[4] == 2:
            inf = await who_is_win_mel(room_id)
            return json.dumps(inf)
        return json.dumps(inf), 200

    return json.dumps({"error": next_step}), 498

@app.websocket('/setchoise')
async def setchoise_ws():
    try:
        while True:
            player_id = int(websocket.args.get('user_id'))
            room_id = int(websocket.args.get('room_id'))
            choice = websocket.args.get('choice')
            inf = await set_choice(room_id,player_id,choice)
            await websocket.send(inf)
    except asyncio.CancelledError:
        raise
    
@app.websocket('/addplayer')
async def addplayer_ws():
    try:
        while True:
            player_id = int(websocket.args.get('user_id'))
            room_id = int(websocket.args.get('room_id'))
            choice = websocket.args.get('choice')
            inf = await set_choice(room_id,player_id,choice)
            await websocket.send(inf)
    except asyncio.CancelledError:
        raise
    
@app.websocket('/kickplayer')
async def kickplayer_ws():
    try:
        while True:
            player_id = int(request.args.get('user_id'))
            room_id = int(request.args.get('room_id'))
            inf = await kick_player(room_id,player_id)
            await websocket.send(inf)
    except asyncio.CancelledError:
        raise
    
@app.websocket('/whoiswin')
async def whoiswin_ws():
    try:
        while True:
            room_id = int(websocket.args.get('room_id'))
            r = await get_room(room_id,0)
            if r[4] == 1:   #Цу-Е-Фа
                inf = await who_is_win_sps(room_id)
                print(inf)
                if inf['winner'] != 'draw':
                    winner_id = inf['winner']['userid']
                    loser_id = inf['loser']['userid']
                    winner = await load_user_data(winner_id, 1)
                    loser = await load_user_data(loser_id, 1)
                    if r[6] == 1:
                        await new_coins(winner_id, round(r[2] * komis + winner['coins'], 1))
                        await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['coins'], 1))
                        await edit_money_in_room(room_id, loser_id, loser['coins'] - r[2])
                        await new_coins(loser_id, loser['coins'] - r[2])
                    elif r[6] == 2:
                        await new_tickets(winner_id, round(r[2] * komis + winner['tickets'], 1))
                        await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['tickets'], 1))
                        await edit_money_in_room(room_id, loser_id, loser['tickets'] - r[2])
                        await new_tickets(loser_id, loser['tickets'] - r[2])
                    elif r[6] == 3:
                        await new_tokens(winner_id, round(r[2] * komis + winner['tokens'], 1))
                        await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['tokens'], 1))
                        await edit_money_in_room(room_id, loser_id, loser['tokens'] - r[2])
                        await new_tokens(loser_id, loser['tokens'] - r[2])
            elif r[4] == 2:
                inf = await who_is_win_mel(room_id)
            await websocket.send(inf)
    except asyncio.CancelledError:
        raise
################################ GAMES

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(ngrok_start())
    app.run()
