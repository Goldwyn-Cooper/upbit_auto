from src.technical import *
from src.data import *
from src.telegram import *
from src.account import *

def get_candidate():
    fs = get_filtered_symbol()
    send_message(', '.join(fs))
    prices = {}
    volatility = {}
    for s in fs:
        p = get_price(s)
        if len(p) < FIBO[-1]:
            continue
        prices[s] = p
        volatility[s] = tr(p)
    corr = correlation(volatility)
    cluster = clustering(corr)
    scoring = lambda x: sum([momentum(prices[x].close, f) for f in FIBO]) / len(FIBO)
    cluster['momentum'] = cluster.symbol.apply(scoring)
    risk = lambda x: min(1, 0.01 / (atr(volatility[x], max(FIBO)) / prices[x].close.iloc[-1])) / 4
    cluster['risk'] = cluster.symbol.apply(risk)
    return cluster\
                .loc[(cluster.groupby('group')['momentum'].idxmax())]\
                .query('momentum > 0')\
                .sort_values('momentum', ascending=False)\
                .head(4).set_index('symbol')

if __name__ == '__main__':
    send_message('💻🤖🔄📈🪙')
    send_message('[BALANCE]')
    balance, budget = get_balance()
    send_message(f'보유자산 : ₩{int(budget):,}')
    send_message(balance)
    candidate = get_candidate()
    send_message('[CANDIDATE]')
    send_message(candidate)
    exit_position(balance, candidate)
    enter_position(balance, candidate, budget)