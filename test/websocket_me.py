import websocket,sys,time
sys.path.append("../biki")
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException
import gzip
import time
import json
from  consts import *

try:
    import thread
except ImportError:
    import _thread as thread


def on_error(ws, error):
    print('### error ###')
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print('### opened ###')
    
    # sub trade ticker
    ws.send("connect")
    time.sleep(1)

    # sub kline
    ws.send('{"event":"sub","params":{"channel":"market_btcusdt_kline_1min","cb_id":"custom string"}}')
    time.sleep(1)

    # sub depth
    ws.send('{"event":"sub","params":{"channel":"market_btcusdt_depth_step0","cb_id":"custom string","asks":150,"bids":150}}')
    time.sleep(1)
    
def on_message(ws, message):
    # result = gzip.decompress(message).decode('utf-8')
    # if result[:7] == '{"ping"':
    #     ts = result[8:21]
    #     pong = '{"pong":' + ts + '}'
    #     ws.send(pong)
    # else:
    ws.send(message)
    print(message)


if __name__ == '__main__':
    # Debug
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('ws://127.0.0.1:5000/test',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever()
    

