# 표준
import os
# 서드파티
from pyupbit import Upbit
import pandas as pd
# 커스텀
from src.telegram import send_message

client = Upbit(os.getenv('UPBIT_AK'), os.getenv('UPBIT_SK'))

def get_balance():
    balance = client.get_balances()
    df = pd.DataFrame(balance).set_index('currency')\
        .loc[:, ['balance', 'avg_buy_price']].astype(float)\
        .drop('USDT')
    balance = df.query('avg_buy_price > 0')
    df.loc['KRW'].avg_buy_price = 1
    return (balance, (df.balance * df.avg_buy_price).sum())

def exit_position(balance, candidate):
    exit_table = balance.join(
        candidate, how='left')\
        .query('risk.isna()').loc[:,['balance']]
    if len(exit_table):
        send_message('[EXIT]')
        send_message(exit_table)
    for r in exit_table.itertuples():
        send_message(f'매도 주문 : {r.Index}')
        client.sell_market_order(
            f'KRW-{r.Index}', r.balance)

def enter_position(balance, candidate, budget):
    enter_table = balance.join(candidate, how='right')\
        .query('balance.isna()').loc[:,['risk']]
    if len(enter_table):
        send_message('[ENTER]')
        send_message(enter_table)
    for r in enter_table.itertuples():
        send_message(f'매수 주문 : {r.Index}')
        client.buy_market_order(
            f'KRW-{r.Index}', r.risk * budget)