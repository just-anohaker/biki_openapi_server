from gevent import monkey
monkey.patch_all(thread=False)
from flask import Flask,request,jsonify, Blueprint
from flask_cors import CORS
import biki.rest_api as restapi
from ws_info import wsinfo
import json,asyncio,time,logging,copy,os,random,math,atexit
from biki.consts import *
from datetime import datetime
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.triggers.interval import IntervalTrigger
from concurrent.futures import ThreadPoolExecutor
from users_service  import user
import data_base as order_db
from flask_socketio import SocketIO, emit
# from decimal import *
# getcontext().prec = 6
executor = ThreadPoolExecutor(1)

app = Flask(__name__)

socketio = SocketIO(app,cors_allowed_origins= '*',async_mode = 'gevent')
# socketio.init_app(app)#
CORS(app)
app.register_blueprint(user,url_prefix='/api/user')

pending_order = []
sched = GeventScheduler()
pending_order_sched = GeventScheduler()
order_price = {}
SEND_DEPTH = 0.25
depth_data = {}
symbol_info = {'symbol': 'trxusdt', 'count_coin': 'USDT', 'amount_precision': 2, 'base_coin': 'TRX', 'price_precision': 6}
#{"symbol":"xysusdt","count_coin":"USDT","amount_precision":3,"base_coin":"XYS","price_precision":6}
#{'symbol': 'trxusdt', 'count_coin': 'USDT', 'amount_precision': 2, 'base_coin': 'TRX', 'price_precision': 6}
#{'symbol': 'etmusdt', 'count_coin': 'USDT', 'amount_precision': 3, 'base_coin': 'ETM', 'price_precision': 6}
#logging.basicConfig(filename="test.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
log = print # logging.getLogger(__name__)

@app.route('/')
def hello_world():
    time.sleep(10)
    return 'Hello World!'

def res_format(flag,data):
    if flag:
        return jsonify({ "success": True, "result": data})
    else:
        return jsonify({ "success": False, "error": data})

@socketio.on('message')
def depth_socket(ms):
    print("event message "+str(ms))


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
    return res_format(True,{ "result": True, "orders": batchOrder,"cost":floor(cost,4)}) 

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
    symbol = symbol_info['symbol']
    try:
        # for j in range(0,len(batchOrder),1) :
        #     tmp = batchOrder[j, j + 1]
        restAPI.create_and_cancel_mass_orders(symbol=symbol, create_orders=batchOrder)
            # ins = params.instrument_id.toLowerCase()
            # for i in range (0,len(res[ins]),1):
            #     if  res[ins][i].order_id != -1 :
            #         res[ins][i].instrument_id = params.instrument_id
    except Exception as err:
        print(str(err) )
        return res_format(True,{'error': str(err)})

    return res_format(True,{'result':True})  


@app.route('/api/batch_order/limitOrder', methods=['POST'])
def limitOrder() :
    try:
        data = request.json
        print(data)
        params = data["options"]
        acct = data["account"]
        params['type']  = int(params['type'] )
        params['size'] = float( params['size'])
        params["price"]= float(params["price"])
        restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
        side = ''
        if (params['type'] == 1):#买入   
            side = 'buy'
        elif params['type']  == 2:#卖出  
            side = 'sell'
        
        result = restAPI.create_order(params['instrument_id'], 'limit', side, volume = params['size'], price =params["price"])
        print(result)
    except Exception as err:
        print(str(err))
        return res_format(False,{'error':str(err)}) 

    return res_format(True,{'result':True})  



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
    return res_format(True,{'result':True})  


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
    symbol = params['instrument_id']

    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])

    if  params['countPerM'] > 50 :
            return jsonify({
                'result': False,
                'error_message': "too many per min!"
            })

    order_interval = int(60  / params['countPerM']) 


    def auto_run():
        ticker_data = restAPI.get_ticker(params['instrument_id'])
        ticker_data = ticker_data['data']
        print('Tick! The time is: %s' % datetime.now(),ticker_data['buy'],ticker_data['sell'])
        randomPrice = round(random.uniform(ticker_data['buy'], ticker_data['sell']),symbol_info['price_precision'] )#symbol_info['price_precision']
        print('对倒andomPrice',randomPrice)
        perSize = round(random.uniform(params['perStartSize'], params['perTopSize']),symbol_info['amount_precision'] )#symbol_info['amount_precision'] 
        print('对倒perSize',perSize)

        side1 = ''
        side2 = ''
        if (params['type'] == 1) :
            side1 = 'buy'
            side2 = 'sell'
        elif (params['type']  == 2) :
            side1 = 'sell'
            side2 = 'buy'
        elif params['type']  == 3:
            randomint = random.randrange(0, 2)
            if (randomint == 0):
                side1 = 'buy'
                side2 = 'sell'
            else:
                side1 = 'sell'
                side2 = 'buy'        
        toOrder = {'side': side1, 'type': 'limit', 'volume':  perSize,'price': randomPrice}
        toTaker = {'side': side2, 'type': 'limit', 'volume':  perSize,'price': randomPrice}
        # print(" 下单! ",[toOrder,toTaker])
        res = restAPI.create_and_cancel_mass_orders(symbol=symbol, create_orders=[toOrder,toTaker])
        print(" 对倒下单res! ",res)
        if res['code'] == '0':
            orderids = res['data']['mass_place'][0]['order_id']
            # print('create  mass orders :',res,orderids)
            res = restAPI.create_and_cancel_mass_orders(symbol=symbol, cancel_orders=orderids)
            # print('cancel orders :',res)
            if res['code'] == '0':
                for  ido in res['data']['mass_cancel']:
                    if ido['code'] == '0':
                        # print('ido :',ido)
                        res = restAPI.get_order_info(ido['order_id'][0],params['instrument_id'])
                        # print('get_order_info orders :',res)
                        if res['code'] == '0':
                            order_db.orders_add(res['data']['order_info'],acct['httpkey'])
            # res = restAPI.get_order_info(params['instrument_id'],orderids)

        #print('get_order_info:',res)
        # if res['code'] == 0:
        #     mass_place TODO 记录订单完成情况
        # if wsinfo.ticker and  abs(time.time - t) > 5*60*1000 :
        #         print("无法刷量下单! ticker data time exceed %s%s" %(str(time.time - t),"s"))
        
    try:
        if not sched.get_job("biki_auto") :
            # sched.add_job(auto_run, trigger=IntervalTrigger(seconds=3),max_instances=10, seconds=order_interval,id="biki_auto")
            sched.add_job(func=auto_run, id="biki_auto", max_instances=15,trigger=IntervalTrigger(seconds=order_interval))
    except  Exception as err:
        print(err)
        return res_format(False,{'error':str(err)})  
    return res_format(True,{'result':True}) 


@app.route('/api/auto_maker/stop', methods=['POST'])
def stop_auto_maker():
    data = request.json
    # acct = data["account"]
    if sched.get_job('biki_auto'):
        sched.remove_job('biki_auto')
    return res_format(True,True)


@app.route('/api/auto_maker/isRunning', methods=['POST'])
def auto_maker_isrun():
    data = request.json
    # acct = data["account"]
    if sched.get_job('biki_auto'):
        return res_format(True,True) 
    else:
        return res_format(True,False) 
        
@app.route('/api/auto_maker/getOrderInfo', methods=['POST'])
def get_order_info():
    data = request.json
    acct = data["account"]
    res=order_db.orders_get(acct['httpkey'])
    return jsonify({ "success": True,"result":{'list':res,'count':len(res)}})

@app.route('/api/batch_order/startDepInfo', methods=['POST'])
def depinfo():
    depth_time = time.time()
    data = request.json
    print( data )
    params = data["options"]
    restAPI = restapi.RestAPI(params['httpkey'], params['httpsecret'])
    def get_new_order():
       
        res= restAPI.get_new_order(params['instrument_id'])
        # print("get_new_order",res )
        nonlocal depth_time
        pending_order = res['data']['resultList']
        #print('Tick! The time is: %s pendingorder %s' % (datetime.now(),pending_order))
          # ws.send(message)
        if wsinfo.depth and (time.time() - depth_time > SEND_DEPTH) :
            order_price.clear()
            if pending_order:
                for order in pending_order:
                    if order['price'] in order_price:
                        order_price[float(order['price'])] = float(order_price.get(order['price'])) + float(order['remain_volume'])
                    else :
                        order_price[float(order['price'])] = float(order['remain_volume'])
            else:
                tem_a = copy.copy(wsinfo.depth['tick']['asks']) 
                tem_b = copy.copy( wsinfo.depth['tick']['buys'] )
                depth_data = {
                     "asks": tem_a,
                     "bids": tem_b,
                     "ts":wsinfo.depth['ts']
                }            
            # print('order_price',order_price)
            tem_a = copy.copy(wsinfo.depth['tick']['asks']) 
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
            tem_b = copy.copy( wsinfo.depth['tick']['buys'] )
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

            depth_data = {
                     "asks": tem_a,
                      "bids": tem_b,
                      "ts":wsinfo.depth['ts']
                }
            # global socketio
            symbol = symbol_info['symbol']
            socketio.emit("depth" + ":" + symbol,depth_data)
            depth_time = time.time()
    try:        
        if pending_order_sched.get_job(params['httpkey']):
            print("server has started !")
            return res_format(True,{'result':"server has started"}) 
        else:
            executor.submit(start_wsinfo)  
            # pending_order_sched.add_job(get_new_order, 'interval',max_instances=10, seconds=1,id=params['httpkey']) 
            pending_order_sched.add_job(func=get_new_order, id=params['httpkey'],max_instances=10,trigger=IntervalTrigger(seconds=1))
    except  Exception as err:
            print('Exception!!!',err)
            return res_format(False,{'error':str(err)})   

    return res_format(True,{'result':True})  


def start_wsinfo():
    wsinfo.ws.run_forever()
    return 
@atexit.register
def exit_app():
    print('exit server!')
    wsinfo.ws.close()

@app.route('/stopDepthInfo', methods=['POST'])
def stop_wsinfo():
    wsinfo.ws.close()
    return res_format(True,{'result':True})  


'''
 * params:
 * {
 * instrument_id  
 * pagesize   
 * page  
 * }
 * account:
 * 
 *'''

@app.route('/api/batch_order/getOrderData', methods=['POST'])
def get_order_data():
    data = request.json
    params = data["options"]
    acct = data["account"]

    symbol = params['instrument_id']
    
    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
    try:
        res_data = restAPI.get_all_trade(symbol)
    except Exception as err:
        return res_format(False,{'error':str(err)}) 
    return res_format(True,{'result':{'list':res_data['data']['resultList'],'length':len(res_data['data']['resultList'])}})  
'''
  * params:
 * {
 * type   //1 买入  2 卖出
 * topPrice  //交易最高价
 * startPrice //交易最低价
 * instrument_id
 * }
 account
 */
'''
@app.route('/api/batch_order/cancel', methods=['POST'])
def cancel_batch_order():
    data = request.json
    params = data["options"]
    acct = data["account"]
    params['startPrice'] =float(params['startPrice'] )
    params['topPrice'] =float(params['topPrice'] )
    print(data)
    symbol = params['instrument_id']
    
    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])
        
    try :
        res_data = restAPI.get_new_order(symbol)
        order_ids = []
        # res.forEach(function (ele) {
        #     # console.log("价格和id" + ele.price + "---" + ele.order_id)
        #     if (params.startPrice <= ele.price && params.topPrice >= ele.price) {
        #         order_ids.push(ele.order_id)
        #     } else if (params.startPrice == 0 && params.topPrice == 0) {
        #         order_ids.push(ele.order_id)
        #     }
        # })
        result = 'no orders'
        orders = res_data['data']['resultList']
        if params['startPrice'] == float(0) and params['topPrice'] == float(0) :
            try:
                print('cancel all')
                result = restAPI.cancel_order_all(symbol)
            except Exception as e:
                print(e)
                return res_format(False,{'error':str(e)})  
            return res_format(True,{'result':result})  
        if orders:
            for ele in orders:
                print("价格和id" , ele['price'] , ele['id'])
                if params['startPrice'] <= float(ele['price'])  and params['topPrice'] >= float(ele['price']) :
                    order_ids.append(ele['id'])

        if len(order_ids) > 0:
                # for (let j = 0; j < order_ids.length; j += 10) {
                #     let tmp = order_ids.slice(j, j + 10)
                #     let result = await authClient.spot().postCancelBatchOrders([{ 'instrument_id': params.instrument_id, 'order_ids': tmp }]);
                #     await sleep(50);//每秒20次 限制是每2秒50次
                #     console.log("撤消订单tmp---" + JSON.stringify(result))//
                # }
                result = restAPI.create_and_cancel_mass_orders(symbol, cancel_orders=order_ids)
                print('create_and_cancel_mass_orders ' ,result)
    except Exception as e:
        print(e)
        return res_format(False,{'error':str(e)})  
    return res_format(True,{'result':result})  


'''
/* params:
* {
* type // 1 双边，2 买方 ，3 卖方
* distance  //盘口距离
* startSize //开始数量
* topSize //最大数量
* countPerM //每分钟挂撤次数
* count //随机个数
* }
* acct:{}
* */
'''
@app.route('/api/auto_market', methods=['POST'])
def start_auto_market():
    data = request.json
    params = data["options"]
    acct = data["account"]
    params['distance'] = int(params['distance'])
    params['count'] = int(params['count'])
    params['startSize'] = float(params['startSize'])
    params['countPerM'] = int(params['countPerM'])
    params['type'] =  int(params['type'])
    symbol =params['instrument_id']

    restAPI = restapi.RestAPI(acct['httpkey'], acct['httpsecret'])

    return

def auto_market(params,acct):
    #TODO

    return
def get_symbol(symbol):
        restAPI = restapi.RestAPI('','')
        result = restAPI.get_symbols()
        res = result['data']
        if res:
            for element in res:
                if element['symbol'] == symbol:
                    return element
        return None
if __name__ == '__main__':
    # ctx = app.app_context()
    # ctx.push()
    sched.start()   
    pending_order_sched.start()
    socketio.run(app,host='0.0.0.0',port= 5000)
    # http_server = WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    # http_server.serve_forever()
    