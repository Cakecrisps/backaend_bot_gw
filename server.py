import binascii
import json

import PIL
import jwt
from quart import Quart, request, render_template, jsonify, Response, send_file, websocket, make_response
#from quart import Quart, request, render_template, jsonify, Response, send_file
import asyncio
from quart_cors import cors
from io import BytesIO
from PIL import Image
import base64
import io
# from bd import *
from bd_items import *
from bd_rooms import *
#import websockets

komis = 0.975
debug = True
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
        #token
        token = token.split('Bearer ')[1]
        return "next"
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
            print("START:")
            print(user_id)

            user_info = await load_user_data(user_id, 1)

            print(user_info)

            translate = await get_translate_type("webapp", user_info['lang'])
            print(translate)

            shop_available = await get_shop_available_new()
            print(shop_available)

            lavka_available = await get_lavka_available()

            daily_bonus = await get_daily_check(user_id)

            collectibles_data = await load_collectibles_data()

            tasks_available = await get_tasks_available(user_info['lang'])
            print(tasks_available)

            #return jsonify({"user_info": user_info, "shop_available": shop_available, "lavka_available": lavka_available, "daily_bonus": daily_bonus, "collectibles_data": collectibles_data}),201  # Возвращаем корректный ответ
            return jsonify(
                {"user_info": user_info, "shop_available": shop_available, "lavka_available": lavka_available,
                 "daily_bonus": daily_bonus,
                 "collectibles_data": collectibles_data,
                 "translate": translate,
                 "tasks_available": tasks_available}), 201  # Возвращаем корректный ответ

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
        #user_id = user_id + "1"
        #user_id = user_id[:-1]
        image_data = await load_user_data(user_id, 2)
        if image_data == "" or image_data == None:
            print("empty_pic")
            image_path = 'bot_settings/media/default_pics/a_man.jpg'
            response = await send_file(image_path, mimetype='image/jpeg')
            return response
        else:
            print("normal_pic")
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
            unix_time = int(time.time())
            photo_url = web_link["url"] + "/avatar/" + str(user_id) + "?t=" + str(unix_time)
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

@app.route('/user_emoji', methods=['GET'])
async def get_emoji_user_link():
    try:
        print(request)
        next_step = await token_auth_and_execute(request)
        if next_step == "next":
            user_id = int(request.args.get('user_id'))
            user_emoji_pack = await get_user_emoji(user_id)
            return jsonify({"user_emoji_pack": user_emoji_pack}),201
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"

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

@app.route('/game_pic/<int:game_id>', methods=['GET'])
async def game_pic_url(game_id):
    try:
    # next_step = await token_auth_and_execute(request)
    # if next_step == "next":
    #     image_data = await load_user_data(game_id, 2)
    #     if image_data == "":
    #         image_path = 'bot_settings/media/default_pics/a_man.jpg'
    #         response = await send_file(image_path, mimetype='image/jpeg')
    #         return response
    #     else:
    #         image_binary = BytesIO(image_data)
    #         response = await send_file(image_binary, mimetype='image/jpeg', as_attachment=False)
    #         return response
        image_path = f'bot_settings/media/game_pics/game_{game_id}.png'
        response = await send_file(image_path, mimetype='image/png')
        return response
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"


@app.route('/cyefa_anim/<pic_id>', methods=['GET'])
async def get_game_pic_cyefa(pic_id):
    try:
        print(pic_id)
        image_path = f'bot_settings/media/games/CyEFa/{pic_id}.png'
        response = await send_file(image_path, mimetype='image/png')
        return response
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"

@app.route('/task_img/<int:taskid>/<int:img>', methods=['GET'])
async def get_taskimg_link(taskid, img):
    try:
        imagedata = await get_imgtask_db(taskid, img)
        if imagedata == None:
            return "error"
        else:
            imagebinary = BytesIO(imagedata)
            response = await send_file(imagebinary, mimetype='image/jpg', as_attachment=False)
            return response
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
@app.route("/poltest",methods = ["POST"])
async def poltest():
    await edit_last_info(5,172359056,'sosi')
    return jsonify({"kal":"kal"})
################################ GAMES

@app.route('/createroom', methods=['POST'])
async def createroomrps():
    print(request)
    next_step = await token_auth_and_execute(request)
    if next_step == "next" or True:
        data = await request.json
        creator_id = int(data['user_id'])
        bet = float(data['bet'])
        bet_type = int(data['bet_type'])
        room_type = int(data['room_type'])

        # creator_id = int(request.args.get('user_id'))
        # bet = float(request.args.get('bet'))
        # bet_type = int(request.args.get('bet_type'))
        # room_type = int(request.args.get('room_type'))

        inf = await create_room(creator_id, bet, room_type, bet_type)
        print(inf)

        # Тестово присоединяем Марка
        #new_room_id = inf.get('room_id')
        #add = await add_player(new_room_id, 5858080651)
        #add = await add_player(new_room_id, "5858080651")
        #print("addplayer:")
        #print(add)
        # Тестово присоединяем Марка

        return jsonify(inf), 200

    return jsonify({"error": next_step}), 498

@app.route('/getrooms', methods=['GET'])
async def getroomsrps():
    print(request)
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

@app.route('/get_existing_games', methods=['GET'])
async def get_existing_games_url():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":

        with open('web_url.json', 'r', encoding='utf-8') as f:
            web_link = json.load(f)
        link = web_link["url"] + "/game_pic"

        # inf = await get_rooms()
        existing_games = [
        {
            "id": 1,
            "room_type": 1,
            "users": "2",
            "url": link + "/" + "1",
        },
        {
            "id": 2,
            "room_type": 2,
            "users": "2-10",
            "url": link + "/" + "2",
        },
    ]
        return json.dumps(existing_games),200

    return json.dumps({"error": next_step}), 498



@app.route("/polling",methods = ["POST"])
async def play():
    try:
        print("request")
        print("#"*50)
        next_step = await token_auth_and_execute(request)
        if next_step != "next" and not debug:
            return json.dumps({"error": next_step}), 498
        data = await request.json
        print(data)
        player_id = int(data['user_id'])
        print(player_id)
        room_id = int(data["room_id"])
        print("type")
        print(data["type"])
        if data["type"] == "addplayer":
            await add_player(room_id,player_id)
            inf = polling_info(room_id,player_id,1)
            print(inf)
            return inf
        elif data['type'] == "setchoice":
            choise = data["choice"]
            await set_choice(room_id,player_id,choise)
            inf = polling_info(room_id,player_id,1)
            print(inf)
            return inf
        elif data['type'] == "kickplayer":
            await kick_player(player_id)
            inf = polling_info(room_id,player_id,1)
            print(inf)
            return inf
        elif data['type'] == "wait":
            inf = polling_info(room_id,player_id,1)
            print(inf)
            return inf
        elif data["type"] == "setemoji":
            emoji_id = data["emoji"]
            await set_emoji(room_id,player_id,emoji_id)
            inf = polling_info(room_id,player_id,1)
            print(inf)
            return inf
    except Exception as e:
        print(f"Ошибка: {e}")
        return "error"

@app.route('/getroominfo', methods=['GET'])
async def getroominforps():
    print("запрос с клиента")
    print(request)
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        try:
            inf = await asyncio.wait_for(get_room_long_poling(room_id, 1), timeout=60)
            print(inf)
        except asyncio.TimeoutError:
            inf = {'status': 'no_update'}  # Нет обновления
            print("Таймаут")

        print("отправили на клиент")
        print(inf)
        #return json.dumps(inf), 200
        return jsonify(inf)
        # response = make_response(json.dumps(inf), 200)
        # response.headers['Content-Type'] = 'application/json'
        # return response

    #return json.dumps({"error": next_step}), 498
    return jsonify({"error": next_step}), 498


@app.route('/getroominfo_light', methods=['GET'])
async def getroominfo_lightrps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))

        # Ждем появления новой информации в комнате или таймаута
        try:
            inf = await asyncio.wait_for(get_room(room_id, 2), timeout=60)  # 60 секунд таймаут
        except asyncio.TimeoutError:
            inf = {'status': 'no_update'}  # Нет обновления

        return json.dumps(inf), 200

    return json.dumps({"error": next_step}), 498

@app.route('/addplayer', methods=['PUT'])
async def addplayerrps():
    print(request)
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
async def kickplayerrps():
    print(request)
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        player_id = int(request.args.get('user_id'))
        #room_id = int(request.args.get('room_id'))
        #inf = await kick_player(room_id,player_id)
        inf = await kick_player(player_id)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/setchoice', methods=['PUT'])
async def setchoicerps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        player_id = int(request.args.get('user_id'))
        room_id = int(request.args.get('room_id'))
        choice = request.args.get('choice')
        inf = await set_choice(room_id,player_id,choice)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/setemoji', methods=['PUT'])
async def setemojirps():
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        player_id = int(request.args.get('user_id'))
        room_id = int(request.args.get('room_id'))
        emoji_id = request.args.get('emoji_id')
        inf = await set_emoji(room_id,player_id,emoji_id)
        return json.dumps(inf),200

    return json.dumps({"error": next_step}), 498


@app.route('/whoiswin', methods=['GET'])
async def whoiswin():
    print(request)
    next_step = await token_auth_and_execute(request)
    if next_step == "next":
        room_id = int(request.args.get('room_id'))
        user_id = int(request.args.get('user_id'))

        with open('web_url.json', 'r', encoding='utf-8') as f:
            web_link = json.load(f)

        r = await get_room(room_id,0)

        users = {}
        us = json.loads(r[1])

        winner_data = us.get("win", {})  # Получаем словарь с данными о победителе или пустой словарь, если ключ "win" отсутствует
        winner_id = winner_data.get("winner_id", "none")

        print("winner_id TEST")
        print(winner_id)

        f_anim = winner_data.get("f_anim", web_link["url"] + "/cyefa_anim/l-rr")
        s_anim = winner_data.get("s_anim", web_link["url"] + "/cyefa_anim/r-rr")
        user_list = winner_data.get("users", "none")
        winner_value = winner_data.get("winner_value", "none")

        # winners = us.get("win", [])  # Получаем список победителей или пустой список, если ключ "win" отсутствует
        # for winner in winners:
        #     winner_id = winner.get("winner_id", "none")
        #     f_anim = winner.get("f_anim", "none")
        #     s_anim = winner.get("s_anim", "none")
        #     user_list = winner.get("users", "none")
        #     winner_value = winner.get("winner_value", "none")



        if winner_id == "" or winner_id == "none":
            # user_choice_now = ""
            for player in us["players"]:
                userid = str(player['userid'])
                users[userid] = {'coins': 0.0}
                # if userid == str(user_id):
                #     user_choice_now = str(player['choice'])

            # if user_choice_now == "none" or user_choice_now == "ready":
            #     inf = {'message': 'none'}
            # else:


            if r[4] == 1:   #Цу-Е-Фа
                inf = await who_is_win_rps(room_id, user_id)
                print(inf)
                try:
                    if inf['winner'] != 'draw':
                        #winner_id = inf['winner']['userid']
                        winner_id = inf['winner']
                        #loser_id = inf['loser']['userid']

                        for player in us["players"]:
                            print(str(player['userid']))
                            print(str(winner_id))
                            if str(player['userid']) != str(winner_id):
                                loser_id = player['userid']
                                print("loser done: " + str(loser_id))

                        #winner_id = inf['winner']['userid']
                        #loser_id = inf['loser']['userid']
                        winner = await load_user_data(winner_id, 1)
                        loser = await load_user_data(loser_id, 1)

                        # if user_id == winner_id:
                        users_result, users = await game_results(users, winner_id, float(r[2]), int(r[6]), room_id)
                        if users_result == "ok":
                            inf['winner_value'] = str(users.get(str(winner_id), {}).get('coins', 0.0))
                        else:
                            inf['winner_value'] = "0.0"

                        print("WHOOO = ne draw")
                        # print(inf)
                        # return json.dumps(inf), 200

                        # if r[6] == 1:
                        #     users_results = await game_results(users, winner_id, float(r[2]), int(r[6]))
                        #
                        #     # await new_coins(winner_id, round(r[2] * komis + winner['coins'], 1))
                        #     # await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['coins'], 1))
                        #     # await edit_money_in_room(room_id, loser_id, loser['coins'] - r[2])
                        #     # await new_coins(loser_id, loser['coins'] - r[2])
                        # elif r[6] == 3 or r[6] == 2:
                        #     users_results = await game_results(users, winner_id, float(r[2]), int(r[6]))
                        #     # await new_tokens(winner_id, round(r[2] * komis + winner['tokens'], 1))
                        #     # await edit_money_in_room(room_id, winner_id, round(r[2] * komis + winner['tokens'], 1))
                        #     # await edit_money_in_room(room_id, loser_id, loser['tokens'] - r[2])
                        #     # await new_tokens(loser_id, loser['tokens'] - r[2])

                        #print("СБРОСИЛ ЧОЙЗ")
                        #reset_game_1 = await set_choice(room_id, user_id, "none")
                        #reset_game_1 = await set_choice(room_id, winner_id, "none")
                        #reset_game_2 = await set_choice(room_id, loser_id, "none")
                    else:
                        # if str(user_id) == str(winner_id):
                        #     inf['winner_value'] = "0.0"

                        #Обработка win

                        players_info = us['players']
                        fc = players_info[0]['choice']
                        sc = players_info[1]['choice']
                        prev_fc = players_info[0]['prev_choice']
                        prev_sc = players_info[1]['prev_choice']
                        f_anim = web_link["url"] + "/cyefa_anim/l-" + prev_fc[0] + fc[0]
                        s_anim = web_link["url"] + "/cyefa_anim/r-" + prev_sc[0] + sc[0]

                        us['win']['winner_id'] = "draw"
                        us['win']['f_anim'] = f_anim
                        us['win']['s_anim'] = s_anim
                        us['win']['users'] = "none"
                        us['win']['winner_value'] = "none"

                        room_data = json.dumps(us)

                        db = sqlite3.connect(f"{dbn}.db")
                        cursor = db.cursor()

                        cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?", (room_data, room_id))

                        db.commit()
                        db.close()

                        # Обработка win
                    print("ставлю none!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    await set_choice(room_id, user_id, "none")

                    # print("WHOOO = draw")
                    # print(inf)
                    # return json.dumps(inf), 200
                except Exception as e:
                    print(f"Ошибка: {e}")
            elif r[4] == 2:
                inf = await who_is_win_mel(room_id)

                # print("WHOOO = 2 game")
                # print(inf)
                # return json.dumps(inf)
            print("WHO IS WIN RETURN")
        else:   #Если виннер уже определен
            #return {"message": "success", "winner": players[1], "loser": players[0], "room_id": room_id, "f_anim": f_anim, "s_anim": s_anim}
            print("SEND_WINNER_ID")
            print(winner_id)
            inf = {"message": "success", "winner": winner_id, "room_id": room_id, "f_anim": f_anim, "s_anim": s_anim, 'winner_value': winner_value}

        print("WHOOO = REZ")
        print(inf)
        return json.dumps(inf), 200

    return json.dumps({"error": next_step}), 498

#
@app.websocket('/roomwstest')
async def whoiswin_wswqreqw():
    await websocket.accept()  # Принимаем соединение
    try:
        while True:
            #data = await websocket.receive_json()
            #data = await websocket.receive()
            data = await websocket.receive()
            print("Received data:", data)

            # Готовим данные для отправки обратно клиенту
            response = {"message": "connect"}
            # Отправляем данные клиенту в формате JSON
            await websocket.send_json(response)

            # Пауза не обязательна, используется, если нужно замедлить цикл
            # await asyncio.sleep(1)
    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()  # Закрываем соединение при ошибке

# @app.websocket('/testsoket')
# async def whoiswin_wswqreqw():
#     await websocket.accept()
#     try:
#         while True:
#             print("soket")
#             #await websocket.accept()
#             data = await websocket.receive()
#             print(data,1)
#             inf = json.dumps({"message":"connect"})
#             type = str(data["type"])
#             print(data,2)
#
#             await websocket.send(json.dumps(inf))
#
#             await asyncio.sleep(1)
#     except Exception as e:
#         print(f"error: {e}")

# @app.websocket('/roomwstest')
# async def whoiswiddsd_ws():
#     print("soket")
#
#     await websocket.accept()
#     print("soket2")
#     while True:
#
#
#         data = await websocket.receive()
#
#         #data = await websocket.receive_json()
#         #data = websocket.args
#         #data = await websocket.receive()
#
#         #data = await websocket.json_module.loads()
#
#         #data = await websocket.receive_text()
#
#
#         print(data)
#
#
#         inf = {"message": "success"}
#
#         await websocket.send(json.dumps(inf))
#
#         await asyncio.sleep(1)
#
#         print("soket sended")
#
#         #retun jsonify({"message": "Ok"}), 201


#
# @app.websocket('/room')
# async def whoiswin_ws():
#     try:
#         print("soket")
#         while True:
#             data = await websocket.receive()
#             print(data, 1)
#             inf = json.dumps({"message": "connect"})
#             type = str(data["type"])
#             print(data, 2)
#
#             # data = await websocket.receive_json()
#             # inf = json.dumps({"message":"connect"})
#             # type = str(data["type"])
#             # print(data)
#             try:
#                 room_id = int(data['room_id'])
#             except:
#                 pass
#             if type == 'whoiswin':
#                 user_id = int(data['user_id'])
#
#                 with open('web_url.json', 'r', encoding='utf-8') as f:
#                     web_link = json.load(f)
#
#                 r = await get_room(room_id, 0)
#
#                 users = {}
#                 us = json.loads(r[1])
#
#                 winner_data = us.get("win", {})  # Получаем словарь с данными о победителе или пустой словарь, если ключ "win" отсутствует
#                 winner_id = winner_data.get("winner_id", "none")
#
#                 print("winner_id TEST")
#                 print(winner_id)
#
#                 f_anim = winner_data.get("f_anim", web_link["url"] + "/cyefa_anim/l-rr")
#                 s_anim = winner_data.get("s_anim", web_link["url"] + "/cyefa_anim/r-rr")
#                 user_list = winner_data.get("users", "none")
#                 winner_value = winner_data.get("winner_value", "none")
#
#
#
#                 if winner_id == "" or winner_id == "none":
#                     for player in us["players"]:
#                         userid = str(player['userid'])
#                         users[userid] = {'coins': 0.0}
#
#
#                     if r[4] == 1:  # Цу-Е-Фа
#                         inf = await who_is_win_rps(room_id, user_id)
#                         print(inf)
#                         try:
#                             if inf['winner'] != 'draw':
#                                 winner_id = inf['winner']
#
#                                 for player in us["players"]:
#                                     print(str(player['userid']))
#                                     print(str(winner_id))
#                                     if str(player['userid']) != str(winner_id):
#                                         loser_id = player['userid']
#                                         print("loser done: " + str(loser_id))
#
#
#                                 winner = await load_user_data(winner_id, 1)
#                                 loser = await load_user_data(loser_id, 1)
#
#                                 # if user_id == winner_id:
#                                 users_result, users = await game_results(users, winner_id, float(r[2]), int(r[6]),
#                                                                          room_id)
#                                 if users_result == "ok":
#                                     inf['winner_value'] = str(users.get(str(winner_id), {}).get('coins', 0.0))
#                                 else:
#                                     inf['winner_value'] = "0.0"
#
#
#                             else:
#
#
#                                 # Обработка win
#
#                                 players_info = us['players']
#                                 fc = players_info[0]['choice']
#                                 sc = players_info[1]['choice']
#                                 prev_fc = players_info[0]['prev_choice']
#                                 prev_sc = players_info[1]['prev_choice']
#                                 f_anim = web_link["url"] + "/cyefa_anim/l-" + prev_fc[0] + fc[0]
#                                 s_anim = web_link["url"] + "/cyefa_anim/r-" + prev_sc[0] + sc[0]
#
#                                 us['win']['winner_id'] = "draw"
#                                 us['win']['f_anim'] = f_anim
#                                 us['win']['s_anim'] = s_anim
#                                 us['win']['users'] = "none"
#                                 us['win']['winner_value'] = "none"
#
#                                 room_data = json.dumps(us)
#
#                                 db = sqlite3.connect(f"{dbn}.db")
#                                 cursor = db.cursor()
#
#                                 cursor.execute("UPDATE rooms_rps SET in_room = ? WHERE room_id = ?",
#                                                (room_data, room_id))
#
#                                 db.commit()
#                                 db.close()
#
#                             await set_choice(room_id, user_id, "none")
#                         except Exception as e:
#                             print(f"Ошибка: {e}")
#                     elif r[4] == 2:
#                         inf = await who_is_win_mel(room_id)
#                     print("WHO IS WIN RETURN")
#                 else:  # Если виннер уже определен
#                     print("SEND_WINNER_ID")
#                     print(winner_id)
#                     inf = {"message": "success", "winner": winner_id, "room_id": room_id, "f_anim": f_anim,
#                            "s_anim": s_anim, 'winner_value': winner_value}
#
#                 print("WHOOO = REZ")
#                 print(inf)
#                 return json.dumps(inf), 200
#             elif type == 'test':
#                 inf = {"message": "test_success"}
#             elif type == 'choice':
#                 player_id = int(data['user_id'])
#                 choice = str(data['choice'])
#                 inf = await set_choice(room_id,player_id,choice)
#             elif type == 'kickplayer':
#                 player_id = int(data['user_id'])
#                 inf = await kick_player(player_id)
#             elif type == 'addplayer':
#                 player_id = int(data['user_id'])
#                 inf = await add_player(room_id,player_id)
#             elif type == 'emoji':
#                 player_id = int(data['user_id'])
#                 emoji = int(data['emoji'])
#                 inf = json.dumps({"player_id":player_id,"room_id":room_id,"emoji":emoji})
#             elif type == 'room_info':
#                 inf = {"room_info": "room_info"}
#             elif type == 'create_room':
#                 player_id = int(data['user_id'])
#                 bet = int(data['bet'])
#                 bet_type = int(data['bet_type'])
#                 room_type = int(data['room_type'])
#
#                 inf = await create_room(player_id, bet, room_type, bet_type)
#                 room_id = inf.get('room_id')
#                 print(inf)
#
#             try:
#                 room_data = await get_room(room_id, 1)
#                 print(room_data)
#
#                 # Добавляем room_data к словарю inf.
#                 inf["room_data"] = room_data
#             except:
#                 inf["room_data"] = ""
#
#             # Отправляем inf, теперь содержащий все необходимые данные, через веб-сокет.
#             await websocket.send(json.dumps(inf))
#
#             await asyncio.sleep(2)
#
#             #retun jsonify({"message": "Ok"}), 201
#     #except asyncio.CancelledError:
#
#     # except asyncio.CancelledError as ce:
#     #     print(f"Asyncio ошибка: {ce}")
#
#     except asyncio.CancelledError:
#         print('Error')
#
#     # except Exception as e:
#     #     print(f"Ошибка: {e}")
#
#         # print('Error')
#         await websocket.send(json.dumps({"message":"error"}))
#         #await websocket.send(json.dumps({"message":"disc"}))
#         raise
################################ GAMES


# @app.websocket('/roomwstest')
# async def websocket_handler(websocket, path):
#     while True:
#         try:
#             message = await websocket.recv()
#             print(f"Received message: {message}")
#
#             response = f"Received: {message}"
#             await websocket.send(response)
#         except websockets.exceptions.ConnectionClosed:
#             print("Connection closed")
#             break


# async def serve_quart():
#     # Здесь вы можете задать параметры для запуска Quart
#     #await app.run_task(host='127.0.0.1', port=8000)
#     app.run()
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     try:
#         asyncio.ensure_future(serve_quart())
#         loop.run_forever()
#     except KeyboardInterrupt:
#         pass
#     finally:
#         loop.close()


# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     try:
#         asyncio.ensure_future(serve_quart())
#         loop.run_forever()
#     except KeyboardInterrupt:
#         pass
#     finally:
#         loop.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(ngrok_start())
    app.run()

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.create_task(ngrok_start())
#     #app.run(host='127.0.0.1', port=8000)
#     app.run()
