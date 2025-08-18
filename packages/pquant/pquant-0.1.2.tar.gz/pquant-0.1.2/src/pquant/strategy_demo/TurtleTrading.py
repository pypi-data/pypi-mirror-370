# ==========================================================
# 示例策略仅供参考，不建议直接实盘使用。
#
# 本策略基于海龟交易法的唐奇安通道。
# 以价格突破唐奇安通道的上下轨作为开仓信号，N倍ATR作为加仓或止损点。
#
# ==========================================================
from pquant import *
from datetime import datetime
from indicator_my import *


def on_init(context):
    # 设置合约标的
    context.symbol = "au6666.SHFE"
    # 设置计算唐奇安通道的参数
    context.n = 20
    # 设置ATR倍数
    context.atr_multiple = 0.5
    # 设置单笔开仓数量
    context.order_volume = 2
    # 设置单笔加减仓数量
    context.change_volume = 2

    subscribe(context.symbol, "1m", 200)
    subscribe(context.symbol, "1d", 100)


def on_start(context):
    update_line(context)


def update_line(context):
    am = get_market_data(context.symbol, "1d")
    context.atr = my_atr(am.high, am.low, am.close, context.n)[-1]
    context.don_upper = my_hhv(am.high, context.n)[-1]
    context.don_lower = my_llv(am.low, context.n)[-1]
    context.atr_half = int(context.atr_multiple * context.atr)
    # 计算加仓点和止损点
    context.long_add_point = context.don_upper + context.atr_half  # 多仓加仓点
    context.long_stop_loss = context.don_upper - context.atr_half  # 多仓止损点
    context.short_add_point = context.don_lower - context.atr_half  # 空仓加仓点
    context.short_stop_loss = context.don_lower + context.atr_half  # 空仓止损点
    Log(f"{context.don_upper}={context.don_lower}={context.atr_half}={context.long_add_point}={context.long_stop_loss}={context.short_add_point}={context.short_stop_loss}")


def on_bar(context, bars):
    if bars[0].interval.value == "1d":
        update_line(context)
    else:
        cancel_all()
        bar = bars[0]
        pos = get_pos(context.symbol)
        if pos == 0:
            if bar.close_price > context.don_upper:
                buy(bar.vt_symbol, bar.close_price, context.order_volume)
            if bar.close_price < context.don_lower:
                short(bar.vt_symbol, bar.close_price, context.order_volume)

        if pos > 0:
            # 当突破加仓点时：加仓
            if bar.close_price > context.long_add_point:
                buy(bar.vt_symbol, bar.close_price, context.order_volume)
                context.long_add_point += context.atr_half
                context.long_stop_loss += context.atr_half
            # 当跌破止损点时：减仓或清仓
            if bar.close_price < context.long_stop_loss:
                if pos > context.order_volume:
                    sell(bar.vt_symbol, bar.close_price, context.order_volume)
                else:
                    sell(bar.vt_symbol, bar.close_price, pos)
                context.long_add_point -= context.atr_half
                context.long_stop_loss -= context.atr_half
        if pos < 0:
            if bar.close_price < context.short_add_point:
                short(bar.vt_symbol, bar.close_price, context.order_volume)
                context.short_add_point -= context.atr_half
                context.short_stop_loss -= context.atr_half
            # 当突破止损点时：减仓或清仓
            if bar.close_price > context.short_stop_loss:
                if pos < -context.order_volume:
                    cover(bar.vt_symbol, bar.close_price, context.order_volume)
                else:
                    cover(bar.vt_symbol, bar.close_price, abs(pos))
                context.short_add_point += context.atr_half
                context.short_stop_loss += context.atr_half


