from  gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all(thread=False)
from flask_sockets import Sockets
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
from flask import Flask,request,jsonify, Blueprint
from flask_cors import CORS
import biki.rest_api as restapi
from ws_info import wsinfo
import json,asyncio,time,logging,copy,os,random,math
from biki.consts import *
from datetime import datetime
from apscheduler.schedulers.gevent import GeventScheduler
from concurrent.futures import ThreadPoolExecutor
from users_service  import user

# from decimal import *
# getcontext().prec = 6
executor = ThreadPoolExecutor(1)
# ws = Blueprint(r'ws', __name__)
app = Flask(__name__)
CORS(app)
sockets = Sockets(app)
app.register_blueprint(user,url_prefix='/api/user')
# sockets.register_blueprint(ws, url_prefix=r'/')

# httpkey = 'b1a5712dfbe38e5d4b9a2d95bb14efb9'
# httpsecret = 'c75bb0e10aba426c542bb6f97e737e72'


wscons = set()
pending_order = []
sched = GeventScheduler()
pending_order_sched = GeventScheduler()
order_price = {}
SEND_DEPTH = 0.25

#logging.basicConfig(filename="test.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
log = print # logging.getLogger(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'
def res(flag,data):
    if flag:
        return jsonify({ "success": True, "result": data})
    else:
        return jsonify({ "success": False, "error": data})

@sockets.route('/ws')
def depth_socket(ws):
    print("connect "+str(ws))
    wscons.add(ws)
    while not ws.closed:
        message = ws.receive()
        print("ws receive"+message)
      

# * type   //1 买入  2 卖出
#  * topPrice  //交易最高价
#  * startPrice //交易最低价
#  * incr //价格增量百分比
#  * size  //挂单数量
#  * sizeIncr //数量递增百分比
#  * instrument_id
@app.route('/api/batch_order/gen', methods=['POST'])
def generate_order():
    data = request.json
    print( data )
    params = data["options"]
   # print( data )
    orderCount =int( (params["topPrice"] - params["startPrice"]) / (params["startPrice"] * params["incr"]))
    print( orderCount )
    batchOrder = []
    cost = 0
    sizes = []#订单数量 从小到大
    prices = []#价格 从小到大
    for i in range(0,orderCount,1):
        x=params["size"] * (1 + params["sizeIncr"] * i)
        sizes.append(floor(x,2))
    for  i in range(0,orderCount,1):
        x = params["startPrice"] + (params["startPrice"] * params["incr"]) * i
        prices.append(floor(x,4))
    print( sizes )
    #print("订单---prices"+prices)
    side = ''
    if  params["type"] == 1:#买入   数量从高到低
        sizes.reverse()
        side = 'buy'
    elif  params["type"] == 2:#卖出   数量从低到高
        side = 'sell'
    
    for i in range(0,orderCount,1):
        order ={'client_oid':i,'side': side, 'type': 'limit', 'volume':  sizes[i],'price': prices[i]}
        batchOrder.append(order)
        cost += float(order["price"]) * order["volume"]
    return res(True,{ "result": True, "orders": batchOrder,"cost":floor(cost,4)}) 

def floor(x,y):
    x*=10**y
    x=math.floor(x)
    x/=10**y
    return x

@app.route('/api/batch_order/toBatchOrder', methods=['POST'])
def batch_order():
    data = request.json
    print( data )
    params = data["options"]
    batchOrder = params['orders']
    acct = data["account"]
    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
    try:
        # for j in range(0,len(batchOrder),1) :
        #     tmp = batchOrder[j, j + 1]
             restAPI.create_and_cancel_mass_orders(symbol=SYMBOL, create_orders=batchOrder)
            # ins = params.instrument_id.toLowerCase()
            # for i in range (0,len(res[ins]),1):
            #     if  res[ins][i].order_id != -1 :
            #         res[ins][i].instrument_id = params.instrument_id
    except Exception as err:
        print(str(err) )
        return res(True,{'error': str(err)})

    return res(True,{'result':True})  


@app.route('/api/batch_order/limitOrder', methods=['POST'])
def limitOrder() :
    try:
        data = request.json
        print(data)
        params = data["options"]
        acct = data["account"]
        restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
        side = ''
        if (params['type'] == 1):#买入   
            side = 'buy'
        elif params['type']  == 2:#卖出  
            side = 'sell'
        
        result = restAPI.create_order(params['instrument_id'], 'limit', side, volume = params['size'], price =params["price"])
    except Exception as err:
        print(str(err))
        return res(False,{'error':str(err)}) 

    return res(True,{'result':True})  



@app.route('/api/batch_order/marketOrder', methods=['POST'])
def marketOrder():
    data = request.json
    print(data)
    params = data["options"]
    acct = data["account"]
    params['type']  = int(params['type'])
   
    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
    side = ''
    if (params['type'] == 1):#买入    
        side = 'buy'
        a= float( params['notional'])
        result = restAPI.create_order(params['instrument_id'], 'market', side, volume = a)
    elif params['type']  == 2:#卖出 
        side = 'sell'
        a = float( params['size'])
        result = restAPI.create_order(params['instrument_id'], 'market', side, volume = a)
    return res(True,{'result':True})  


@app.route('/api/auto_maker', methods=['POST'])
def auto_trade():
    ''' 
    每次挂单数量
    perStartSize
    perTopSize 
    countPerM  //每分钟成交多少笔
    instrument_id
    '''  
    
    data = request.json
    params = data["options"]
    acct = data["account"]
    params['perStartSize'] = float(params['perStartSize'])
    params['perTopSize'] = float(params['perTopSize'])
    params['countPerM'] = int(params['countPerM'])
    params['type'] =  int(params['type'])
    params['instrument_id']

    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
    # side = ''
    # if (params.type == 1):#买入   
    #     side = 'buy'
    #     result = restAPI.create_order(params['instrument_id'], 'market', side, volume = params['volume'])
    # elif params.type == 2:#卖出  
    #     side = 'sell'
    #     result = restAPI.create_order(params['instrument_id'], 'market', side, volume = params['volume'])
    if  params['countPerM'] > 200 :
            return jsonify({
                'result': False,
                'error_message': "too many per min!"
            })
        
    # if (this.isAutoMaker()) {
    #     return {
    #         result: false,
    #         error_message: "is auto makering!"
    #     }
    #     }
    order_interval = int(60  / params['countPerM']) 


    def auto_run():
        ticker_data = restAPI.get_ticker(params['instrument_id'])
        ticker_data = ticker_data['data']
        print('Tick! The time is: %s' % datetime.now(),ticker_data['buy'],ticker_data['sell'])
        randomPrice = round(random.uniform(ticker_data['buy'], ticker_data['sell']), 4)
        print('randomPrice',randomPrice)
        perSize = round(random.uniform(params['perStartSize'], params['perTopSize']), 2)
        print('perSize',perSize)

        side1 = ''
        side2 = ''
        if (params['type'] == 1) :
            side1 = 'buy'
            side2 = 'sell'
        elif (params['type']  == 2) :
            side1 = 'sell'
            side2 = 'buy'
        elif params['type']  == 3:
            randomint = random.randomint(0, 1)
            if (randomint == 0):
                side1 = 'buy'
                side2 = 'sell'
            else:
                side1 = 'sell'
                side2 = 'buy'        
        toOrder = {'side': side1, 'type': 'limit', 'volume':  perSize,'price': randomPrice}
        toTaker = {'side': side2, 'type': 'limit', 'volume':  perSize,'price': randomPrice}
        print(" 下单! ",[toOrder,toTaker])
        res = restAPI.create_and_cancel_mass_orders(symbol=params['instrument_id'], create_orders=[toOrder,toTaker])
        print('create_orders:',res)
        # if res['code'] == 0:
        #     mass_place TODO 记录订单完成情况
        # if wsinfo.ticker and  abs(time.time - t) > 5*60*1000 :
        #         print("无法刷量下单! ticker data time exceed %s%s" %(str(time.time - t),"s"))
        
        
    if not sched.get_job(acct['httpkey']) :
        sched.add_job(auto_run, 'interval',max_instances=10, seconds=5,id="biki_auto")
        try:
            sched.start()
        except  Exception as err:
            print(err)
    
    return res(True,{'result':True}) 


@app.route('/api/auto_maker/stop', methods=['POST'])
def stop_auto_maker():
    data = request.json
    # acct = data["account"]
    if sched.get_job('biki_auto'):
        sched.remove_job('biki_auto')
    return res(True,True)


@app.route('/api/auto_maker/isRunning', methods=['POST'])
def auto_maker_isrun():
    data = request.json
    # acct = data["account"]
    if sched.get_job('biki_auto'):
        return res(True,True) 
    else:
        return res(True,False) 

@app.route('/api/batch_order/startDepInfo', methods=['POST'])
def depinfo():
    depth_time = time.time()
    data = request.json
    print( data )
    params = data["options"]
    acct = data["account"]
    if sched.get_job(acct['httpkey']):
        return res(True,{'result':True})  
    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
    executor.submit(start_wsinfo) 
    def get_new_order():
        res= restAPI.get_new_order(params['instrument_id'])
        # print(time.time() ,depth_time,SEND_DEPTH )
        nonlocal depth_time
        pending_order = res['data']['resultList']
        #print('Tick! The time is: %s pendingorder %s' % (datetime.now(),pending_order))
          # ws.send(message)
        if wsinfo.depth and (time.time() - depth_time > SEND_DEPTH) :
            order_price.clear()
            for order in pending_order:
                if order['price'] in order_price:
                    order_price[float(order['price'])] = float(order_price.get(order['price'])) + float(order['remain_volume'])
                else :
                    order_price[float(order['price'])] = float(order['remain_volume'])
            print('order_price',order_price)
            tem_a = copy.copy(wsinfo.depth['asks']) 
            for  index in range (len(tem_a)):
                element = tem_a[index]
                if element[0] in order_price:
                    if len(tem_a[index]) >2 :
                        print("before error1111", tem_a[index] )
                    
                    tempv =  copy.copy( tem_a[index])
                    if len(tempv)<=2: 
                        tempv.append(order_price[element[0]])
                    else:
                        tempv[2] = order_price[element[0]]
                    tem_a[index]  =  tempv
                    #tem_a[index][2] = order_price[str(element[0])]
            tem_b = copy.copy( wsinfo.depth['buys'] )
            for  index in range (len(tem_b)):
                element = tem_b[index]
                if element[0] in order_price:
                    if len(tem_b[index]) >2 :
                        print("before error1111", tem_b[index] )
                    
                    tempv =  copy.copy( tem_b[index])
                    if len(tempv)<=2: 
                        tempv.append(order_price[element[0]])
                    else:
                        tempv[2] = order_price[element[0]]
                    tem_b[index]  =  tempv

            # print('tem_a',tem_b)
            #print('ws.send',tem_a)
            #time.sleep(2)#0.005
            for ws in wscons:
                ws.send( json.dumps({"depth" + ":" + SYMBOL:{
                    "asks": tem_a,
                    "bids": tem_b
                }}))
            depth_time = time.time()
    pending_order_sched.add_job(get_new_order, 'interval',max_instances=10, seconds=10,id='biki_auto')
    try:
        pending_order_sched.start()
    except  Exception as err:
            print(err)
    
    return res(True,{'result':True})  


def start_wsinfo():
    wsinfo.ws.run_forever()
    return 

@app.route('/stopDepthInfo', methods=['POST'])
def stop_wsinfo():
    wsinfo.ws.close()
    return res(True,{'result':True})  


if __name__ == '__main__':
    # ctx = app.app_context()
    # ctx.push()

    http_server = WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
    