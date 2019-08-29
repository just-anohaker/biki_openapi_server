# http header
API_URL = 'https://openapi.biki.com'
WS_URL = 'wss://ws.biki.com/kline-api/ws'
CONTENT_TYPE = 'Content-Type'

ACEEPT = 'Accept'
COOKIE = 'Cookie'
LOCALE = 'Locale='

APPLICATION_FORM = 'application/x-www-form-urlencoded'

# METHOD
GET = "GET"
POST = "POST"
DELETE = "DELETE"

# REST API URL
REST_ACCOUNT = '/open/api/user/account'
REST_ALL_ORDER = '/open/api/v2/all_order'
REST_ALL_TRADE = '/open/api/all_trade'
REST_CANCEL_ORDER = '/open/api/cancel_order'
REST_CANCEL_ORDER_ALL = '/open/api/cancel_order_all'
REST_CREATE_ORDER = '/open/api/create_order'
REST_ALL_TICKER = '/open/api/get_allticker'
REST_RECORDS = '/open/api/get_records'
REST_TICKER = '/open/api/get_ticker'
REST_TRADES = '/open/api/get_trades'
REST_MARKET = '/open/api/market'
REST_DEPTH = '/open/api/market_dept'
REST_MASS_REPLACE = '/open/api/mass_replaceV2'
REST_NEW_ORDER = '/open/api/v2/new_order'
REST_ORDER_INFO = '/open/api/order_info'
REST_SYMBOLS = '/open/api/common/symbols'

SYMBOL = 'trxusdt'

WS_TICKER_CHANNEL = 'market_%s_trade_ticker'%(SYMBOL)
WS_DEPTH_CHANNEL = 'market_%s_depth_step0'%(SYMBOL)
# WS API
WS_TRADE_TICKER_SUB = '{"event":"sub","params":{"channel":"market_%s_trade_ticker","cb_id":"custom string"}}'%(SYMBOL)
WS_TRADE_TICKER_UNSUB = '{"event":"unsub","params":{"channel":"market_%s_trade_ticker"}}'%(SYMBOL)

WS_MARKET_DEPTH_SUB = '{"event":"sub","params":{"channel":"market_%s_depth_step0","cb_id":"custom string","asks":150,"bids":150}}'%(SYMBOL)
WS_MARKET_DEPTH_UNSUB = '{"event":"unsub","params":{"channel":"market_%s_depth_step0","cb_id":"custom string","asks":150,"bids":150}}'%(SYMBOL)

WS_MARKET_KLINE_SUB = '{"event":"sub","params":{"channel":"market_%s_kline_period","cb_id":"custom string"}}'%(SYMBOL)
WS_MARKET_KLINE_UNSUB = '{"event":"unsub","params":{"channel":"market_%s_kline_period"}}'%(SYMBOL)


