# ==========================================================================================
# 示例策略仅供参考，不建议直接实盘使用。
#
# 跨品种套利是指利用两种不同、但相互关联的资产间的价格差异进行套利交易。
# 本策略以焦炭主连和焦煤主连为标的，以布林带的形式，在价格偏离过大时开仓，在价格偏离回归正常时平仓。
# ==========================================================================================
from pquant import *
from indicator_my import *
import numpy as np


def on_init(context):
    context.symbol_a = "j2509.DCE"
    context.symbol_b = "jm2509.DCE"
    context.volume = 1
    context.period = 30  # 计算布林价差的周期参数

    # 因为是日线级别的，这边订阅日线周期即可，wait_group 保证一起返回
    subscribe(context.symbol_a, "1d", 50, wait_group=True)
    subscribe(context.symbol_b, "1d", 50, wait_group=True)


def on_start(context):
    Log(f"跨品种套利策略 on_start")


def on_stop(context):
    Log(f"跨品种套利策略 on_stop")


def on_bar(context, bars):
    # 获取最新的报价、以及合约信息
    am_a = get_market_data(context.symbol_a, "1d")
    am_b = get_market_data(context.symbol_b, "1d")
    if len(am_a.close) < context.period or len(am_b.close) < context.period:
        Log(f"数据集不够！！！")
        return

    multiplier_a = get_contract(context.symbol_a).size
    multiplier_b = get_contract(context.symbol_b).size

    # 计算价差
    spread = am_a.close[-context.period:] * multiplier_a - am_b.close[-context.period] * multiplier_b
    up = np.mean(spread) + 0.5 * np.std(spread)
    down = np.mean(spread) - 0.5 * np.std(spread)
    spread_now = spread[-1]

    Log(f"布林上轨：{up} 布林下轨：{down} 最新价差：{spread_now}")

    if spread_now > up:  # 价差突破上轨时，做空symbol_a，做多symbol_b，设置各种目标仓位
        send_target_order(context.symbol_a, -context.volume, am_a.close[-1])
        send_target_order(context.symbol_b, context.volume, am_b.close[-1])

    elif spread_now < down:  # 价差突破下轨时，做多symbol_a，做空symbol_b，设置各种目标仓位
        send_target_order(context.symbol_a, context.volume, am_a.close[-1])
        send_target_order(context.symbol_b, -context.volume, am_b.close[-1])

    else:  # 价差回归时，设置目标仓位为0
        send_target_order(context.symbol_a, 0, am_a.close[-1])
        send_target_order(context.symbol_b, 0, am_b.close[-1])