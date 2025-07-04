# -*- coding: utf-8 -*-

import json
import re
import uuid
from websocket import WebSocket, create_connection
from urllib.parse import parse_qsl, unquote, urljoin, urlparse
def _websocket_data():
        '''Get data from the websocket.

        Args:
            username: Model Username
            chat_servers: servername from self._get_servers

        Returns:
            message: data to create a video url.
            php_message: data for self._php_fallback
        '''
        ws=WebSocket()

        try_to_connect = 0
        while (try_to_connect < 5):
            try:
                # xchat = str(random.choice(chat_servers))
                host = "wss://wchat54.myfreecams.com/fcsl"
                ws = create_connection(host)
                ws.send('hello fcserver\n\0')
                r_id = str(uuid.uuid4().hex[0:32])
                ws.send('1 0 0 20071025 0 {0}@guest:guest\n'.format(r_id))
                try_to_connect = 5
            except Exception:
                try_to_connect += 1
                print('Failed to connect to WS server: {0} - try {1}'.format("r_id", try_to_connect))
                if try_to_connect == 5:
                    print('can\'t connect to the websocket')
                    raise

        buff = ''
        php_message = ''
        message=''
        ws_close = 0
        _socket_re = re.compile(r'''(\w+) (\w+) (\w+) (\w+) (\w+)''')
        while ws_close == 0:
            socket_buffer = ws.recv()
            socket_buffer = f"{buff}{socket_buffer}"
            buff = ''
            while True:
                ws_answer =_socket_re.search(socket_buffer)
                if bool(ws_answer) == 0:
                    break

                FC = ws_answer.group(1)
                # print("fc",FC)
                FCTYPE = int(FC[6:])
                # print("fctype",FCTYPE)

                message_length = int(FC[0:6])
                message = socket_buffer[6:6 + message_length]

                if len(message) < message_length:
                    buff = ''.join(socket_buffer)
                    break

                message = unquote(message)
                username='BUSTY_EMA'
                if FCTYPE == 1 and username:
                    print("fctype=1",message)
                    ws.send('10 0 0 20 0 {0}\n'.format(username))
                elif FCTYPE == 81:
                    php_message = message
                    if username is None:
                        ws_close = 1
                elif FCTYPE == 10:
                    ws_close = 1
                # print(message)

                socket_buffer = socket_buffer[6 + message_length:]

                if len(socket_buffer) == 0:
                    break

        ws.send('99 0 0 0 0')
        ws.close()
        _dict_re = re.compile(r'''(?P<data>{.*})''')
        php_data = _dict_re.search(php_message)
        php_data = json.loads(php_data.group('data'))
        print()
        key=php_data['respkey']
        print(php_message)
        print(message)
        print(f"https://www.myfreecams.com/php/FcwExtResp.php?host=wchat54&respkey={key}&type=14&opts=256&serv=1054&arg1=709&arg2=21&owner=0&nc=2915592&debug=cams")
        return message, php_message

_websocket_data()