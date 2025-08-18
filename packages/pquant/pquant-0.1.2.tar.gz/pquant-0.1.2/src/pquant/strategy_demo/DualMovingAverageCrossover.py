# ==========================================================
# 示例策略仅供参考，不建议直接实盘使用。
#
# 本策略以分钟级别数据建立双均线模型，短周期为20，长周期为60
# 当短期均线由上向下穿越长期均线时做空
# 当短期均线由下向上穿越长期均线时做多
# ==========================================================
from pquant import *
from indicator_my import *


def on_init(context):
    context.symbol = context.params["symbol"]  # 读取策略参数配置，此处也可以直接设置合约代码，例如：“TA509.CZCE”
    context.long_period = context.params["long_period"]
    context.short_period = context.params["short_period"]

    context.volume = 1  # 下单手数
    context.interval = "5m"

    subscribe(context.symbol, context.interval, 200)


def on_start(context):
    Log(f"[{context.symbol}] on_start")


def on_stop(context):
    Log(f"[{context.symbol}] on_stop")


def on_bar(context, bars):
    bar = bars[0]
    am = get_market_data(context.symbol, context.interval)  # 获取制定合约、制定周期的数据集

    # indicator_my 函数中包含大部分的麦语言函数, 返回的是‘numpy’数组
    short_ma = my_ma(am.close, context.short_period)
    long_ma = my_ma(am.close, context.long_period)

    if len(short_ma) < 2 or len(long_ma) < 2:
        return

    if short_ma[-2] <= long_ma[-2] and short_ma[-1] > long_ma[-1]:
        send_target_order(context.symbol, context.volume, bar.close_price)  # 设置目标仓位

    elif short_ma[-2] >= long_ma[-2] and short_ma[-1] < long_ma[-1]:
        send_target_order(context.symbol, -context.volume, bar.close_price)