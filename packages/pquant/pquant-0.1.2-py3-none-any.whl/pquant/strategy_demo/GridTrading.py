# ==========================================================
# 示例策略仅供参考，不建议直接实盘使用。
#
# 网格交易法是一种利用行情震荡进行获利的策略。它通过捕捉市场的震荡波动，在价格区间内低买高卖，实现获利。
# 该策略的核心是将价格走势划分为多个区间，形成类似“网格”的结构，当市场价格触碰到网格线时自动执行买入或卖出操作，从而通过反复的价差交易赚取利润。
#
# ==========================================================
from pquant import *
import numpy as np
import pandas as pd
from datetime import datetime, time


def on_init(context):
    # 记录上一次交易时网格范围的变化情况
    context.grid_change_last = [0, 0]
    # 记录上一次交易时网格范围
    context.last_grid = 0
    # 记录网格中枢价格
    context.grid_center = 0
    # 网格等级
    context.band = []
    # 网格标签
    context.grid_tags = []
    # 网格价格
    context.grid_prices = []

    context.symbol = "au6666.SHFE"

    subscribe(context.symbol, "1m", 200)
    subscribe(context.symbol, "1d", 100)
    Log(f"初始参数-网格编号 {context.grid_tags}")


def on_start(context):
    # 设置网格数量
    grid_count = context.params['grid_count']
    # 设置网格标签
    context.grid_tags = [-i for i in range(1, grid_count + 1)][::-1] + [i for i in range(1, grid_count + 1)]
    # 获取网格线数量
    price_len = grid_count * 2 + 1
    # 设置初始的网格线的价格
    context.grid_prices = [-100000] * price_len
    Log(f"初始参数-网格间隔【{context.params['grid_interval']}】 网格单边数量【{context.params['grid_count']}】")
    Log(f"初始参数-网格编号 {context.grid_tags}")


def on_d_bar(context, bar):
    # 网格中枢定义方式：获取前一天的收盘价作为新的一天的网格中枢价格
    context.grid_center = bar.close_price
    grid_count = context.params['grid_count']
    grid_interval = context.params['grid_interval']
    # 网格区间线比例
    band_list = [1 + (i - grid_count) * grid_interval for i in range(2 * grid_count + 1)]
    # 获取网格线的具体价格
    context.band = np.array(band_list) * context.grid_center
    Log(f"设置网格中枢为：{bar.datetime.date()}的收盘价：{context.grid_center}")
    context.grid_prices = [f"{x:10.2f}" for x in context.band]
    Log(f"网格区间为 |{'|'.join(context.grid_prices)}|")
    context.grid_change_last = [0, 0]
    context.last_grid = 0


def on_stop(context):
    Log(f"未平仓数量{context.position}")


def on_bar(context, bars):
    if bars[0].interval.value == "1d":
        on_d_bar(context, bars[0])
    else:
        cancel_all()
        bar = bars[0]
        start_time = time(14, 50)
        end_time = time(15, 0)

        # 收盘前平仓操作
        if start_time <= bar.datetime.time() <= end_time:
            send_target_order(bar.vt_symbol, 0)
            return

        if len(context.band) == 0:
            return

        # 获取收盘价所在网格区域
        grid = pd.cut([bar.close_price], context.band, labels=context.grid_tags)[0]

        if np.isnan(grid):
            Log("价格波动超过网格范围，可适当调节网格宽度和数量")

        if context.last_grid == 0:
            context.last_grid = grid
            return

        pos = get_pos(context.symbol)
        # 假设上一根K线所在的网格小于当前网格
        if context.last_grid < grid:
            # 记录新旧格子范围（按照大小排序）
            grid_change_new = [context.last_grid, grid]
            # 如果前一次开仓是4-5，这一次是5-4，算是没有突破，不成交
            if grid_change_new != context.grid_change_last:
                Log(f"从{context.last_grid}往{grid}")
                # 更新前一次的数据
                context.last_grid = grid
                context.grid_change_last = grid_change_new
                # 如果有多仓，平多，否则开空
                if pos > 0:
                    sell(bar.vt_symbol, bar.close_price, context.params['grid_trade_count'])
                else:
                    short(bar.vt_symbol, bar.close_price, context.params['grid_trade_count'])

        if context.last_grid > grid:
            grid_change_new = [grid, context.last_grid]
            if grid_change_new != context.grid_change_last:
                Log(f"从{context.last_grid}往{grid}")
                context.last_grid = grid
                context.grid_change_last = grid_change_new
                # 如果有空仓，平空，否则开多
                if pos < 0:
                    cover(bar.vt_symbol, bar.close_price, context.params['grid_trade_count'])
                else:
                    buy(bar.vt_symbol, bar.close_price, context.params['grid_trade_count'])
