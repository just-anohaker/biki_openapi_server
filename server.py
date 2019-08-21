from  gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all(thread=False)
from flask import Flask,request,jsonify
import biki.rest_api as restapi
import time

app = Flask(__name__)
api_key = 'b1a5712dfbe38e5d4b9a2d95bb14efb9'
secretkey = 'c75bb0e10aba426c542bb6f97e737e72'
restAPI = restapi.RestAPI(api_key, secretkey)

@app.route('/')
def hello_world():
    time.sleep(10)
    return 'Hello World!'

@app.route('/login', methods=['POST'])
def batch_order():
    restAPI.create_and_cancel_mass_orders('btcusdt', create_orders=[{'side': 'buy', 'type': 'limit', 'volume': 2,'price': 10000},
    {'side': 'buy', 'type': 'limit', 'volume': 1.5,'price': 10000}])


# * type   //1 买入  2 卖出
#  * topPrice  //交易最高价
#  * startPrice //交易最低价
#  * incr //价格增量百分比
#  * size  //挂单数量
#  * sizeIncr //数量递增百分比
#  * instrument_id
@app.route('/batchOrder/gen', methods=['POST'])
def generate_order():
    data = request.json
    print( data )
    params = data["options"]
   # print( data )
    orderCount =int( (params["topPrice"] - params["startPrice"]) / (params["startPrice"] * params["incr"]))
    batchOrder = []
    cost = 0
    sizes = []#订单数量 从小到大
    prices = []#价格 从小到大
    for i in range(0,orderCount,1):
        sizes.append(params["size"] * (1 + params["sizeIncr"] * i))
    for  i in range(0,orderCount,1):
        prices.append(params["startPrice"] + (params["startPrice"] * params["incr"]) * i)
    print( sizes )
    #print("订单---prices"+prices)
    side = ''
    if  params["type"] == 1:#买入   数量从高到低
        sizes.reverse()
        side = 'buy'
    elif  params["type"] == 2:#卖出   数量从低到高
        side = 'sell'
    
    for i in range(0,orderCount,1):
        order ={'side': side, 'type': 'limit', 'volume':  sizes[i],'price': prices[i]}
        batchOrder.append(order)
        cost += float(order["price"]) * order["volume"]
    return jsonify({ "result": True, "orders": batchOrder,"cost":cost})

@app.route('/ticker')
def ticker():
    result = restAPI.get_ticker('btcusdt')
    return result
  
if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    http_server.serve_forever()