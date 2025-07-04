import asyncio
import json
import re
import signal
from urllib.parse import unquote
import uuid
import rnet
from rnet import Message, WebSocket
import hashlib
import binascii

def make_respkey(webkey):
    d = hashlib.sha1(webkey)
    d.update(b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
    respkey = d.digest()
    respkey = binascii.b2a_base64(respkey)[:-1]
    return respkey



async def send_message(ws:WebSocket):
    r_id = str(uuid.uuid4().hex[0:32])
    await ws.send(Message.from_text('hello fcserver\n\0'))
    await ws.send(Message.from_text(f'1 0 0 20071025 0 {r_id}@guest:guest\n',))
    print(f'Websocket server {r_id} connected')
    # await asyncio.sleep(0.01)


async def receive_message(ws:WebSocket):
    # async for message in ws:
    #     print("Received: ", message)
        buff = ''
        php_message = ''
        ws_close = 0
        _socket_re = re.compile(r'''(\w+) (\w+) (\w+) (\w+) (\w+)''')
        while ws_close == 0:
            socket_buffer = await ws.recv()
            socket_buffer = f"{buff}{socket_buffer}"
            buff = ''
            while True:
                print(len(socket_buffer))
                ws_answer =_socket_re.search(socket_buffer)
                print(ws_answer)
                if not bool(ws_answer):
                    break
                
                FC = ws_answer.group(1)
                FCTYPE = int(FC[6:])

                FC = ws_answer.group(1)
                FCTYPE = int(FC[6:])
                print(FCTYPE)

                message_length = int(FC[0:6])
                message = socket_buffer[6:6 + message_length]

                if len(message) < message_length:
                    buff = ''.join(socket_buffer)
                    break

                message = unquote(message)
                username='BUSTY_EMA'
                if FCTYPE == 1 and username:
                    await ws.send(Message.from_text(f'10 0 0 20 0 {username}\n'))
                elif FCTYPE == 81:
                    php_message = message
                    if username is None:
                        ws_close = 1
                elif FCTYPE == 10:
                    ws_close = 1
                print(message)

                socket_buffer = socket_buffer[6 + message_length:]

                if len(socket_buffer) == 0:
                    break

        await ws.send(Message.from_text('99 0 0 0 0'))
        await ws.close()
        # _dict_re = re.compile(r'''(?P<data>{.*})''')
        # php_data = _dict_re.search(php_message)
        # php_data = json.loads(php_data.group('data'))
        # print()
        # key=php_data['respkey']
        print(php_message)
        # print(message)
        # print(f"https://www.myfreecams.com/php/FcwExtResp.php?host=wchat54&respkey={key}&type=14&opts=256&serv=1054&arg1=709&arg2=21&owner=0&nc=2915592&debug=cams")
        # return message, php_message


async def main():
    # xchat = str(random.choice(chat_servers))
    host = "wss://wchat63.myfreecams.com/fcsl"
    ws = await rnet.websocket(host)
    r_id = str(uuid.uuid4().hex[0:32])
    try_to_connect=0
    while (try_to_connect < 5):
        try:
            await ws.send(Message.from_text('hello fcserver\n\0'))
            await ws.send(Message.from_text(f'1 0 0 20071025 0 {r_id}@guest:guest\n'))
            await receive_message(ws)
            try_to_connect = 5
        except Exception:
            try_to_connect += 1
            print(f'Failed to connect to WS server: {try_to_connect}')
            if try_to_connect == 5:
                print('Can\'t connect to the websocket')
                raise
            return

#         buff = ''
#         php_message = ''
#         message=''
#         ws_close = 0
#         _socket_re = re.compile(r'''(\w+) (\w+) (\w+) (\w+) (\w+)''')
#         while ws_close == 0:
#             socket_buffer = ws.recv()
#             socket_buffer = f"{buff}{socket_buffer}"
#             buff = ''
#             while True:
#                 ws_answer =_socket_re.search(socket_buffer)
#                 if bool(ws_answer) == 0:
#                     break

#                 FC = ws_answer.group(1)
#                 FCTYPE = int(FC[6:])

#                 message_length = int(FC[0:6])
#                 message = socket_buffer[6:6 + message_length]

#                 if len(message) < message_length:
#                     buff = ''.join(socket_buffer)
#                     break

#                 message = unquote(message)
#                 username='BUSTY_EMA'
#                 if FCTYPE == 1 and username:
#                     await ws.send(Message.from_text(f'10 0 0 20 0 {username}\n'))
#                 elif FCTYPE == 81:
#                     php_message = message
#                     if username is None:
#                         ws_close = 1
#                 elif FCTYPE == 10:
#                     ws_close = 1


#                 socket_buffer = socket_buffer[6 + message_length:]

#                 if len(socket_buffer) == 0:
#                     break

#                 await ws.send(Message.from_text('99 0 0 0 0'))
#                 await ws.close()

#             _dict_re = re.compile(r'''(?P<data>{.*})''')
#             php_data = _dict_re.search(php_message)
#             php_data = json.loads(php_data.group('data'))

#             key=php_data['respkey']
#         print(php_message)
#         print(message)
#         print(f"https://www.myfreecams.com/php/FcwExtResp.php?host=wchat54&respkey={key}&type=14&opts=256&serv=1054&arg1=709&arg2=21&owner=0&nc=2915592&debug=cams")
#         return message, php_message


if __name__ == "__main__":
    asyncio.run(main())
    # print(make_respkey(b'jWxbwRkkztQUqHS2uM21KsLhfw8='))