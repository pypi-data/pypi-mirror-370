"""策略模板示例。"""

from datetime import datetime
from pquant import *


def on_init(context):
    # type: (Context) -> None
    """初始化回调。

    在策略启动时执行，可用于订阅合约、设置全局变量、读取外部参数等。
    """
    # 设置全局变量
    context.symbol = "au2508.SHFE"

    subscribe(context.symbol, "30m", 200)
    subscribe("au2508.SHFE", "1m", 200)

    # 读取外部定义的参数（如果有）
    # context.params["test_params"]
    Log("策略初始化")


def on_start(context):
    # type: (Context) -> None
    """启动回调。

    当 :func:`on_init` 完成后执行，可在此读取合约信息和历史数据。
    """
    contract_data = get_contract(context.symbol)

    # 获取指定合约指定周期的合约历史数据
    market_data = get_market_data(context.symbol, "30m")
    last_open = market_data.open[-1]
    last_high = market_data.high[-1]
    last_low = market_data.low[-1]
    last_close = market_data.close[-1]
    last_volume = market_data.volume[-1]
    last_ts = market_data.time[-1]
    dt = datetime.fromtimestamp(float(last_ts))
    chinese_time = dt.strftime("%Y年%m月%d日 %H时%M分%S秒")

    Log(
        f"{contract_data.ctp_name} {chinese_time} 开高低收量："
        f"{last_open}-{last_high}-{last_low}-{last_close}-{last_volume}"
    )


def on_stop(context):
    # type: (Context) -> None
    """策略停止时调用。"""
    Log("停止策略")


def on_tick(context, tick):
    # type: (Context,TickData) -> None
    """Tick 数据回调。"""
    pass


def on_trade(context, trade):
    # type: (Context,TradeData) -> None
    """成交回报。"""
    Log(f"on_trade_tradeid:{trade.tradeid}")


def on_order(context, order):
    # type: (Context,OrderData) -> None
    """委托状态回调。"""
    Log(f"on_order{order.orderid}--{order.price}--{order.volume}")


def on_bar(context, bars):
    # type: (Context,list[BarData]) -> None
    """K线数据回调。

    当订阅多个合约并且都设置 ``wait_group=True`` 时，
    会在所有合约数据到齐后同时回调。
    """
    bar = bars[0]
    Log(f"{bar.vt_symbol} - {bar.datetime.strftime('%Y-%m-%d %H:%M:%S')} - {bar.close_price}")

    # 获取净持仓
    pos = get_pos(bar.vt_symbol)

    # 下单方式1：设置目标仓位，在接收到最新价格时自动下单
    if pos != 5:
        send_target_order(bar.vt_symbol, 5)
    else:
        send_target_order(bar.vt_symbol, 0)

    # 下单方式2：手动下单
    # buy 买入开仓 sell 卖出平仓  short 卖出开仓  cover 买入平仓
    # 和 send_target_order 混合使用时，手动下单后目标仓位将失效
    # if pos != 5:
    #     buy(bar.vt_symbol, bar.close_price, 5)
    # else:
    #     sell(bar.vt_symbol, bar.close_price, 5)

