import websocket
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException
import gzip
import time
import json
from biki.consts import *

try:
    import thread
except ImportError:
    import _thread as thread

class WsInfo:
    depth = {}
    ticker = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = websocket.WebSocketApp(WS_URL,
                    on_message = lambda ws,msg: self.on_message(ws, msg),
                    on_error   = lambda ws,msg: self.on_error(ws, msg),
                    on_close   = lambda ws:     self.on_close(ws),
                    on_open    = lambda ws:     self.on_open(ws))
        return
    def on_error(self, ws, error):
        print('### error ###')
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        print('### opened ###')

        # sub trade ticker
        # ws.send(WS_TRADE_TICKER_SUB)
        # time.sleep(1)
        ws.send(WS_MARKET_DEPTH_SUB)
        # sub kline
    # ws.send('{"event":"sub","params":{"channel":"market_btcusdt_kline_1min","cb_id":"custom string"}}')
    # time.sleep(1)

        # sub depth
        #ws.send('{"event":"sub","params":{"channel":"market_btcusdt_depth_step0","cb_id":"custom string","asks":150,"bids":150}}')

    def on_message(self, ws, message):
        result = gzip.decompress(message).decode('utf-8')
        if result[:7] == '{"ping"':
            ts = result[8:21]
            pong = '{"pong":' + ts + '}'
            ws.send(pong)
        else:
            #print(result)
            json_data = json.loads(result)
            if json_data['channel'] == WS_DEPTH_CHANNEL:
                self.depth = json_data
            elif json_data['channel'] == WS_TICKER_CHANNEL:
                #print(result)
                self.ticker = json_data['tick']
                
           # self.tickerData = jsonify(result)

wsinfo = WsInfo()
#wsinfo.ws.run_forever()