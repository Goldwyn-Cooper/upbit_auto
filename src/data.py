# 표준
import time
# 서드파티
import pandas as pd
import requests
import pyupbit

MARKETCAP='https://crix-api-cdn.upbit.com/v1/crix/marketcap?currency=KRW'
TRADABLE='https://s3.ap-northeast-2.amazonaws.com/crix-production/crix_master'

def get_marketcap_from_upbit():
    response = requests.get(MARKETCAP) 
    cols = ('koreanName', 'symbol', 'marketCap', 'accTradePrice24h')
    return pd.DataFrame(response.json()).loc[:, cols]

def get_observable_symbol(marketcap: pd.DataFrame):
    # expr = 'symbol != "BTC" and symbol != "ETH"'
    expr = 'symbol != "BTC"'
    alt = marketcap.query(expr)
    expr = f'marketCap > {alt.marketCap.mean()}\
             and accTradePrice24h > {alt.accTradePrice24h.mean()}'
    return marketcap.query(expr).set_index('symbol')

def get_tradable_from_upbit():
    response = requests.get(TRADABLE)
    expr = 'pair.str.contains("KRW") and marketState == "ACTIVE" and exchange == "UPBIT"'
    return pd.DataFrame(response.json())\
        .query(expr).loc[:, ('koreanName', 'baseCurrencyCode')]\
        .set_index('baseCurrencyCode')

def get_filtered_symbol():
    marketcap = get_marketcap_from_upbit()
    observable = get_observable_symbol(marketcap)
    tradable = get_tradable_from_upbit()
    return observable.join(tradable, lsuffix='_x', rsuffix='_y', how='inner')\
            .index.to_list()

def get_price(symbol):
    time.sleep(0.04)
    return pyupbit.get_ohlcv(f'KRW-{symbol}')\
            .loc[:, ['high', 'low', 'close']]