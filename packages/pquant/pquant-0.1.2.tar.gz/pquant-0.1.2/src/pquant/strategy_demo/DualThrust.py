# ==========================================================
# 示例策略仅供参考，不建议直接实盘使用。
#
# Dual Thrust是一个趋势跟踪策略，当现价突破上轨时做多，当现价跌穿下轨时做空。
# 上轨：开盘价+K*波动
# 下轨：开盘价-K*波动
# 波动：max(HH - LC, HC - LL)
# 其中HH为N天最高价的最大值，LC为N天收盘价的最小值，HC为N天收盘价的最大值，LL为N天最低价的最小值
#
# ==========================================================

from datetime import datetime
from pquant import *


def on_init(context):

    # 设置全局变量
    context.symbol = "au6666.SHFE"
    context.k1 = context.params["k1"]
    context.k2 = context.params["k2"]
    context.N = context.params["N"]

    subscribe(context.symbol, "1m", 200)
    subscribe(context.symbol, "1d", 100)

    Log(f"策略初始化,{context.symbol}-k1:{context.k1}-k2:{context.k2}-N:{context.N}")


def on_start(context):
    update_line(context)

def update_line(context):
    am = get_market_data(context.symbol, "1d")
    current_bar = get_current_bar(context.symbol, "1d")
    if current_bar:
        open_price = current_bar.open_price
    else:
        open_price = am.open[-1]
    HH = am.high[-context.N:].max()
    HC = am.close[-context.N:].max()
    LC = am.close[-context.N:].min()
    LL = am.low[-context.N:].min()
    range = max(HH - LC, HC - LL)

    context.buy_line = open_price + range * context.k1  # 上轨
    context.sell_line = open_price - range * context.k2  # 下轨

    Log(f" 当日开盘价{open_price} , HH,HC,LC,LL:{HH},{HC},{LC},{LL}, 波动率：{range} 上轨:{context.buy_line},下轨:{context.sell_line}")

def on_bar(context,bars):
    if bars[0].interval.value == "1d":
        update_line(context)
    else:
        bar = bars[0]
        if bar.close_price > context.buy_line:
            send_target_order(bar.vt_symbol,1)

        if bar.close_price < context.sell_line:
            send_target_order(bar.vt_symbol,-1)
