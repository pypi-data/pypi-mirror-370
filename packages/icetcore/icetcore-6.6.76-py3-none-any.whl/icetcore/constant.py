from dataclasses import dataclass,asdict
from typing import Union


class SymbolType:
    Options = "OPT"
    Futures = "FUT"
    Stocks = "STK"


class BarType:
    MINUTE = 4
    DK = 5
    TICK = 2


class GreeksType:
    DOGSS = 800
    DOGSK = 820
    GREEKS1K = 9
    GREEKSTICK = 10
    GREEKSDK = 19


class OrderSide:
    Buy = 1
    Sell = 2


class TimeInForce:
    ROD = 1
    IOC = 2
    FAK = 2
    FOK = 3


class OrderType:
    Market = 1
    Limit = 2
    Stop = 3
    Stoplimit = 4
    TrailingStop = 5
    TrailingStopLimit = 6
    MarketifTouched = 7
    LimitifTouched = 8
    TrailingLimit = 9
    # 对方价=10
    # 本方价=11
    # 中间价=15

    # 最优价=20
    # 最优价转限价=21
    # 五档市价=22
    # 五档市价转限价=23
    # 市价转限价=24
    # 一定范围市价=25


class PositionEffect:
    Open = 0
    Close = 1
    平今 = 2
    平昨 = 3
    Auto = 4
    备兑开仓 = 10
    备兑平仓 = 11


@dataclass
class OrderStruct:
    Account: str
    BrokerID: str
    Symbol: str
    Side: OrderSide
    OrderQty: int
    OrderType: OrderType
    TimeInForce: TimeInForce
    PositionEffect: PositionEffect
    Price: Union[str, float]="0"
    StopPrice: Union[str, float]="0"
    ContingentSymbol: str = ""
    GroupType: int = 0
    GroupID: str = ""
    UserKey1: str = ""
    UserKey2: str = ""
    # UserKey3:str=""
    Strategy: str = ""
    ChasePrice: str = ""
    TouchPrice: Union[str, float]="0"
    TouchField: int = 0
    TouchCondition: int = 0
    Exchange: str = ""
    Breakeven: str = ""
    BreakevenOffset: str = ""
    # 是否启用流控
    FlowControl: int = 0
    # 是否启用自适应
    FitOrderFreq: int = 0
    # 反向开仓延迟
    DelayTransPosition: int = 0
    # 自成交
    SelfTradePrevention: int = 0
    ExtCommands: str = ""
    GrpAcctOrdType: int = 0
    SpreadType: int = 0
    Synthetic: int = 0
    SymbolA: str = ""
    SymbolB: str = ""
    Security: str = ""
    Security2: str = ""
    Month: str = ""
    Month2: str = ""
    CallPut: str = ""
    CallPut2: str = ""
    Side1: int = 0
    Side2: int = 0
    TrailingField: int = 0
    TrailingType: int = 0
    TrailingAmount: int = 0
    SlicedType: int = 0
    SlicedPriceField: int = 0
    SlicedTicks: int = 0
    DayTrade: int = 0
    DiscloseQty: int = 0
    Variance: int = 0
    Interval: int = 0
    LeftoverAction: int = 0
    Threshold: int = 0
    Consecutive: int = 0
    NumberOfRetries: int = 0
    RetryInterval: int = 0
    StrikePrice: float = 0
    StrikePrice2: float = 0
    TradeType: int = 0
    ExCode: int = 0
    MaxPriceLevels: int = 0


@dataclass
class SpreadOrderStruct:
    SymboolName: str
    Side: str
    OrderQty: str
    Price: str
    BrokerIDA: str = ""
    BrokerIDB: str = ""
    BrokerIDC: str = ""
    BrokerIDD: str = ""
    BrokerIDE: str = ""
    AccountA: str = ""
    AccountB: str = ""
    AccountC: str = ""
    AccountD: str = ""
    AccountE: str = ""
    MaxOrderQty: str = "0"
    OrderInterval: str = ""
    PositionEffect: str = ""
    PositionEffectA: str = ""
    PositionEffectB: str = ""
    PositionEffectC: str = "-1"
    PositionEffectD: str = "-1"
    PositionEffectE: str = "-1"
    TakeProfit: str = ""
    StopLoss: str = ""
    TrailingAmount: str = ""
    Consecutive: str = ""
    OCOsUpTicks: str = ""
    OCOsDownTicks: str = ""
    OCOsTime: str = ""
    StartTime: str = ""
    EndTime: str = ""
    ActiveChasePrice: str = ""
    ChasePrice: str = ""
    TransferPosType: str = ""
    TransferBasis: str = ""
    GroupID: str = ""
    GroupType: str = ""
    PosSizingID: str = ""
    ExtCommands: str = ""
    Strategy: str = ""
    UserKey1: str = ""
    UserKey2: str = ""