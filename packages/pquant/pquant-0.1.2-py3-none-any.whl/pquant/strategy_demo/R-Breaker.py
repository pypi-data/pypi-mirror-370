# ==========================================================
# 示例策略仅供参考，不建议直接实盘使用。
#
# R-Breaker是一种短线日内交易策略。
# 策略根据前一个交易日的收盘价、最高价和最低价数据通过一定方式计算出六个价位，从大到小依次为：突破买入价、观察卖出价、反转卖出价、反转买入、观察买入价、突破卖出价。
# 以此来形成当前交易日盘中交易的触发条件，追踪盘中价格走势，实时判断触发条件。
# 具体条件如下：
# 突破
# 在空仓条件下，如果盘中价格超过突破买入价，则采取趋势策略，即在该点位开仓做多。
# 在空仓条件下，如果盘中价格跌破突破卖出价，则采取趋势策略，即在该点位开仓做空。
# 反转
# 持多单，当开仓后的日内最高价超过观察卖出价后，盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线时，采取反转策略，即在该点位反手做空。
# 持空单，当开仓后的日内最低价低于观察买入价后，盘中价格出现反弹，且进一步超过反转买入价构成的阻力线时，采取反转策略，即在该点位反手做多。
# 设定止损条件。当亏损达到设定值后，平仓；尾盘平仓。
#
# ==========================================================
from pquant import *
from datetime import datetime, time


def on_init(context):
    context.symbol = "au6666.SHFE"
    subscribe(context.symbol, "1m", 200)
    subscribe(context.symbol, "1d", 100)


def on_start(context):
    update_line(context)


def update_line(context):
    am = get_market_data(context.symbol, "1d")
    if len(am.high):
        high = am.high[-1]  # 前一日的最高价
        low = am.low[-1]  # 前一日的最低价
        close = am.close[-1]  # 前一日的收盘价
        pivot = (high + low + close) / 3  # 枢轴点

        context.bBreak = high + 2 * (pivot - low)  # 突破买入价
        context.sSetup = pivot + (high - low)  # 观察卖出价
        context.sEnter = 2 * pivot - low  # 反转卖出价
        context.bEnter = 2 * pivot - high  # 反转买入价
        context.bSetup = pivot - (high - low)  # 观察买入价
        context.sBreak = low - 2 * (high - pivot)  # 突破卖出价

        Log(f"{context.bBreak}-{context.sSetup}-{context.sEnter}-{context.bEnter}-{context.bSetup}-{context.sBreak}")


def on_bar(context, bars):
    if bars[0].interval.value == "1d":
        update_line(context)
    else:
        bar = bars[0]
        start_time = time(14, 50)
        end_time = time(15, 0)

        # 收盘前平仓操作
        if start_time <= bar.datetime.time() <= end_time:
            send_target_order(bar.vt_symbol, 0)
            return

        pos = get_pos(context.symbol)
        if pos == 0:
            if bar.close_price > context.bBreak:
                send_target_order(bar.vt_symbol, 1)
            if bar.close_price < context.sBreak:
                send_target_order(bar.vt_symbol, -1)
            return

        current_bar = get_current_bar(context.symbol, "1d")
        today_high = current_bar.high_price
        today_low = current_bar.low_price

        if pos > 0 and today_high > context.sSetup and bar.close_price < context.sEnter:
            send_target_order(bar.vt_symbol, -1)
            return

        if pos < 0 and today_low < context.bSetup and bar.close_price > context.bEnter:
            send_target_order(bar.vt_symbol, 1)
            return


