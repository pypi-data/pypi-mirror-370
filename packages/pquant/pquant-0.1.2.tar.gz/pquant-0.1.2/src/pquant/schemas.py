"""策略对象和数据结构定义。

该模块包含枚举类型以及策略回调所使用的数据类，仅用于本地开发时的类型提示。
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from datetime import datetime as Datetime
from typing import Any

class Direction(Enum):
    """
    委托订单、成交记录、持仓方向。
    """
    LONG = "多"
    SHORT = "空"
    NET = "净"


class Offset(Enum):
    """
    委托订单、成交记录开平。
    """
    NONE = ""
    OPEN = "开"
    CLOSE = "平"
    CLOSETODAY = "平今"
    CLOSEYESTERDAY = "平昨"


class Status(Enum):
    """
    委托订单状态
    """
    SUBMITTING = "提交中"
    NOTTRADED = "未成交"
    PARTTRADED = "部分成交"
    ALLTRADED = "全部成交"
    CANCELLED = "已撤销"
    REJECTED = "拒单"


class OrderType(Enum):
    """
    订单类型，目前仅支持限价
    """
    LIMIT = "限价"
    MARKET = "市价"
    STOP = "STOP"
    FAK = "FAK"
    FOK = "FOK"
    RFQ = "询价"


class Exchange(Enum):
    """
    交易所代码
    """
    CFFEX = "CFFEX"         # 中国金融期货交易所
    SHFE = "SHFE"           # 上海期货交易所
    CZCE = "CZCE"           # 郑州商品交易所
    DCE = "DCE"             # 大连商品交易所
    INE = "INE"             # 上海国际能源交易中心
    GFEX = "GFEX"           # 广州期货交易所
    SSE = "SSE"             # 上海证券交易所
    SZSE = "SZSE"           # 深圳证券交易所
    BSE = "BSE"             # 北京证券交易所
    SGE = "SGE"             # 上海黄金交易所
    SMART = "SMART"         # 智能合约，用做自定义国际品种

class Interval(Enum):
    """
    周期代码
    """
    SECOND = "s"
    SECOND_5 = "5s"
    SECOND_10 = "10s"
    SECOND_15 = "15s"
    SECOND_30 = "30s"
    MINUTE = "1m"
    MINUTE_3 = "3m"
    MINUTE_5 = "5m"
    MINUTE_10 = "10m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR = "1h"
    FOUR_HOUR = "4h"
    DAILY = "1d"
    WEEKLY = "w"
    MONTHLY = "month"
    YEARLY = "year"
    TICK = "tick"


class Product(Enum):
    """
    产品类型（目前仅支持期货）
    """
    EQUITY = "股票"
    FUTURES = "期货"
    OPTION = "期权"
    INDEX = "指数"
    FOREX = "外汇"
    SPOT = "现货"
    ETF = "ETF"
    BOND = "债券"
    WARRANT = "权证"
    SPREAD = "价差"
    FUND = "基金"

    
ACTIVE_STATUSES = set([Status.SUBMITTING, Status.NOTTRADED, Status.PARTTRADED])


@dataclass
class BaseData:
    gateway_name: str
    extra: dict = field(default=None, init=False)

@dataclass
class TickData(BaseData):
    """
    Tick数据
    """

    symbol: str                 # 合约代码
    exchange: Exchange          # 交易所
    datetime: Datetime          # Tick时间

    name: str = ""              # 合约名称
    volume: float = 0           # 成交量
    turnover: float = 0         # 成交额
    open_interest: float = 0    # 持仓量
    last_price: float = 0       # 最新价
    last_volume: float = 0      # 最新成交量
    limit_up: float = 0         # 涨停价（仅实盘）
    limit_down: float = 0       # 跌停价（仅实盘）

    open_price: float = 0           # 今开盘价（仅实盘）
    high_price: float = 0           # 今最高价（仅实盘）
    low_price: float = 0            # 今最低价（仅实盘）
    pre_close: float = 0            # 昨收盘价（仅实盘）
    pre_settlement_price: float = 0 # 上一日结算价（仅实盘）

    bid_price_1: float = 0          # 买一价
    bid_price_2: float = 0          # 五档行情仅实盘且CTP支持、仅上期所和上海能源有
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0

    ask_price_1: float = 0          # 卖一价
    ask_price_2: float = 0          # 五档行情仅实盘且CTP支持、仅上期所和上海能源有
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0

    bid_volume_1: float = 0         # 买一量
    bid_volume_2: float = 0         # 五档行情仅实盘且CTP支持、仅上期所和上海能源有
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0

    ask_volume_1: float = 0         # 卖一量
    ask_volume_2: float = 0         # 五档行情仅实盘且CTP支持、仅上期所和上海能源有
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0

    localtime: Datetime | None = None # 本地接收到tick的实际时间

    def __post_init__(self) -> None:
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass
class BarData(BaseData):
    """
    Bar（K线）数据
    """

    symbol: str                 # 合约代码
    exchange: Exchange          # 交易所
    datetime: Datetime          # K线时间

    interval: Interval          # K线周期
    volume: float = 0           # 成交量
    turnover: float = 0         # 成交额
    open_interest: float = 0    # 持仓量
    open_price: float = 0       # 开盘价
    high_price: float = 0       # 最高价
    low_price: float = 0        # 最低价
    close_price: float = 0      # 收盘价
    settlement_price: float | None = None       # 结算价（只有通过query_history查询的日线数据才有值）
    pre_settlement_price: float | None = None   # 上一日结算价（只有通过query_history查询的日线数据才有值）

    def __post_init__(self) -> None:
        """补充合约全名。"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass
class OrderData(BaseData):
    """
    委托订单数据
    """

    symbol: str             # 合约代码
    exchange: Exchange      # 交易所
    orderid: str            # 委托订单号

    type: OrderType = OrderType.LIMIT   # 委托类型
    direction: Direction | None = None  # 方向
    offset: Offset = Offset.NONE        # 开平
    price: float = 0                    # 委托价格
    decimal_price: Decimal = 0          # 委托价格(高精度)
    volume: float = 0                   # 委托数量
    traded: float = 0                   # 已成交数量
    status: Status = Status.SUBMITTING  # 委托状态
    status_msg: str = None              # 委托状态CTP返回中文信息（委托失败时有）
    datetime: Datetime | None = None    # 委托时间
    reference: str = ""                 # 参考信息（暂时无用）
    symbol_name = ""                    # 合约名称

    def __post_init__(self) -> None:
        """补充复合ID。"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.vt_orderid: str = f"{self.gateway_name}.{self.orderid}"

    def is_active(self) -> bool:
        """
        检查委托是否处于活跃状态。是否是提交中、未成交、部分成交状态。
        """
        if self.status in ACTIVE_STATUSES:
            return True
        else:
            return False

    def is_submitting(self) -> bool:
        """
        检查委托是否处于提交中状态。
        """
        return self.status == Status.SUBMITTING


@dataclass
class TradeData(BaseData):
    """
    成交数据
    """

    symbol: str             # 合约代码
    exchange: Exchange      # 交易所
    orderid: str            # 委托订单号
    tradeid: str            # 成交号
    direction: Direction    # 方向

    offset: Offset = Offset.NONE            # 开平
    price: float = 0                        # 成交价格
    decimal_price: Decimal = 0              # 成交价格(高精度)
    volume: float = 0                       # 成交数量
    datetime: Datetime | None = None        # 成交时间
    symbol_name:str = ""                    # 合约名称

    def __post_init__(self) -> None:
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.vt_orderid: str = f"{self.gateway_name}.{self.orderid}"
        self.vt_tradeid: str = f"{self.gateway_name}.{self.tradeid}"


@dataclass
class ContractData(BaseData):
    """
    合约信息
    """

    symbol: str             # 合约代码
    exchange: Exchange      # 交易所
    name: str               # 合约名称
    product: Product        # 合约类型
    size: float             # 合约乘数
    pricetick: float        # 最小价格变动单位
    pre_code: str | None = ""   # 品种代码
    ctp_name: str | None = ""   # CTP合约名称
    long_margin_ratio: float | None = 0.0   # 多头保证金比例
    short_margin_ratio: float | None = 0.0  # 空头保证金比例
    open_fee_ratio: float | None = 0.0      # 开仓手续费比例
    close_fee_ratio: float | None = 0.0     # 平仓手续费比例
    close_yt_fee_ratio: float | None = 0.0  # 平昨手续费比例
    open_fee_hand: float | None = 0.0       # 开仓手续费(手数)
    close_fee_hand: float | None = 0.0      # 平仓手续费(手数)
    close_yt_fee_hand: float | None = 0.0   # 平昨手续费(手数)

    create_date: str = ""       # 合约创建日期
    open_date: str = ""         # 合约上市日期
    expire_date: str = ""       # 合约到期日期
    start_deliv_date: str = ""  # 开始交割日期
    end_deliv_date: str = ""    # 结束交割日期
    local_name: str = ""        # 本地合约名称

    def __post_init__(self) -> None:
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"



class ArrayManager:
    """K线数据管理器。

    保存最近 ``size`` 条K线数据，便于策略进行指标计算。
    所有数组属性的长度均为 ``size``。
    """

    def __init__(self, size: int = 100) -> None:
        self.size: int = size
        # 以下属性返回值为 np.ndarray 类型，数量为最后 size 条
        self.open = []          # 开盘价数组
        self.high = []          # 最高价数组
        self.low = []           # 最低价数组
        self.close = []         # 收盘价数组
        self.volume = []        # 成交量数组
        self.turnover = []      # 成交额数组
        self.open_interest = [] # 持仓量数组
        self.time = []          # 时间戳数组，13 位时间戳
        self.datetime = []      # datetime 数组，datetime.datetime 类型



class Context:
    """策略上下文对象。

    运行策略时用于保存临时变量，例如在 ``on_init`` 中设置
    ``context.symbol = "au2508.SHFE"``，随后可在 ``on_start`` 等回调中读取。
    停止策略后，context 中的内容会被清空。
    """

    def __init__(self) -> None:
        # 1：实盘 2：回测
        self.model = "0"
        # 动态参数,初始时会自动从外部读取 ，使用时 context.params["xxx"] 获取
        self.params: dict[str, Any] = {}
