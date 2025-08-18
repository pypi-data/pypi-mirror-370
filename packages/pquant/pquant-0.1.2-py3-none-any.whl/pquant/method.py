"""策略方法定义。

这些函数仅提供接口说明，实际执行由口袋量化平台提供。
"""

from .schemas import *


def send_order(
    vt_symbol: str,
    direction: Direction,
    offset: Offset,
    price: float,
    volume: float,
) -> list[str]:
    """发送委托订单。

    Args:
        vt_symbol: 合约代码，格式如 ``au2408.SHFE``。
        direction: 委托方向。
        offset: 开平方向。
        price: 委托价格。
        volume: 委托数量。

    Returns:
        list[str]: vt_orderid 列表。
    """
    pass


def cancel_order(vt_orderid: str) -> None:
    """撤销单个委托。

    Args:
        vt_orderid: 订单号。
    """
    pass


def cancel_all(vt_symbol: str) -> None:
    """撤销指定合约的所有委托。

    Args:
        vt_symbol: 合约代码。
    """
    pass


def buy(vt_symbol: str, price: float, volume: float) -> list[str]:
    """买入开仓。

    Args:
        vt_symbol: 合约代码。
        price: 委托价格。
        volume: 委托数量。

    Returns:
        list[str]: vt_orderid 列表。
    """
    pass


def sell(vt_symbol: str, price: float, volume: float) -> list[str]:
    """卖出平仓。

    Args:
        vt_symbol: 合约代码。
        price: 委托价格。
        volume: 委托数量。

    Returns:
        list[str]: vt_orderid 列表。
    """
    pass


def short(vt_symbol: str, price: float, volume: float) -> list[str]:
    """卖出开仓。

    Args:
        vt_symbol: 合约代码。
        price: 委托价格。
        volume: 委托数量。

    Returns:
        list[str]: vt_orderid 列表。
    """
    pass


def cover(vt_symbol: str, price: float, volume: float) -> list[str]:
    """买入平仓。

    Args:
        vt_symbol: 合约代码。
        price: 委托价格。
        volume: 委托数量。

    Returns:
        list[str]: vt_orderid 列表。
    """
    pass


def send_target_order(vt_symbol: str, target: int) -> None:
    """设置目标仓位。

    当接收到最新价格推送时，系统会自动调整到目标仓位。若与手动下单
    混合使用，手动下单后目标仓位将失效。

    Args:
        vt_symbol: 合约代码。
        target: 目标仓位数量。
    """
    pass


def get_pos(vt_symbol: str) -> int:
    """查询当前净持仓。

    Args:
        vt_symbol: 合约代码。

    Returns:
        int: 当前净持仓。
    """
    pass


def subscribe(
    vt_symbol: str, interval_str: str, count: int = 200, wait_group: bool = False
) -> bool:
    """订阅行情数据。

    Args:
        vt_symbol: 合约代码。
        interval_str: 周期字符串，如 ``"1m"``、``"5m"`` 等。
        count: 初始拉取的K线数量，默认200。
        wait_group: 当订阅多个合约时是否等待所有合约都更新后再回调。

    Returns:
        bool: 订阅是否成功。
    """
    pass


def get_market_data(vt_symbol: str, interval_str: str) -> ArrayManager | None:
    """获取历史K线数据。

    Args:
        vt_symbol: 合约代码。
        interval_str: 周期字符串。

    Returns:
        ArrayManager | None: 对应周期的 ``ArrayManager``，若未订阅则为 ``None``。
    """
    pass


def get_current_bar(vt_symbol: str, interval_str: str) -> BarData | None:
    """获取当前正在合成的K线。

    Args:
        vt_symbol: 合约代码。
        interval_str: 周期字符串。

    Returns:
        BarData | None: 当前K线数据，若无则为 ``None``。
    """
    pass


def get_current_tick(vt_symbol: str) -> TickData | None:
    """获取最新 Tick。

    Args:
        vt_symbol: 合约代码，必须是当前策略已订阅的品种。

    Returns:
        TickData | None: 最新 Tick 数据，若无则为 ``None``。
    """
    pass


def get_contract(vt_symbol: str) -> ContractData | None:
    """获取合约信息。

    Args:
        vt_symbol: 合约代码。

    Returns:
        ContractData | None: 合约信息，若无则为 ``None``。
    """
    pass


def query_history(
    vt_symbol: str,
    interval_str: str,
    start: Datetime | None = None,
    end: Datetime | None = None,
    number: int | None = None,
) -> list[BarData] | list[TickData]:
    """查询历史数据。

    - 查询指定范围数据，传入 ``start`` 和 ``end``。
    - 查询最新 ``number`` 条数据，仅传入 ``number``。
    - 查看end时间前 ``number`` 条数据，传入 ``end`` 和 ``number``（Tick、秒级别无法查询）。
    - 查询数据量过大会影响效率。

    Args:
        vt_symbol: 合约代码。
        interval_str: 周期字符串。
        start: 起始时间。
        end: 结束时间。
        number: 查询条数，当仅提供该参数时 ``end`` 默认为当前时间。

    Returns:
        list[BarData] | list[TickData]: 历史数据列表。
    """
    pass


def _G(*args: Any):
    """本地持久化变量。

    该函数提供一个可持久化的键值存储。根据传入参数执行不同操作：

    - ``_G()``            -> 返回当前任务 ID。
    - ``_G(key)``         -> 读取键为 ``key`` 的值。
    - ``_G(key, value)``  -> 保存或更新键值对。
    - ``_G(key, None)``   -> 删除键为 ``key`` 的值。
    - ``_G(None)``        -> 清除所有键值对。

    Args:
        *args: 根据参数数量和内容执行不同操作。

    Returns:
        Any: 对应键的值或任务 ID。
    """
    pass


def Log(msg: str) -> None:
    """记录日志信息。

    Args:
        msg: 日志内容。
    """
    pass

