import time
from icetcore import TCoreAPI, QuoteEvent, TradeEvent, BarType, GreeksType
import pandas as pd


class APIEvent(TradeEvent, QuoteEvent):
    # 连线成功通知apitype="quoteapi"是行情api的通知，"tradeapi"是交易通知
    def onconnected(self, apitype: str):
        print(apitype)

    # 断线成功通知
    def ondisconnected(self, apitype: str):
        print(apitype)

    # subATM订阅的ATM合约信息，动态推送期权的ATM平值,OTM-1C虚值一档认购，OTM-1P虚值一档认沽，和认购期权合约列表
    def onATM(self, datatype, symbol, data: dict):
        print(data)

    # 实时greeks
    def ongreeksline(self, datatype, interval, symbol, data, isreal):
        print(pd.DataFrame(data))

    # 实时greeks
    def ongreeksreal(self, datatype, symbol, data: dict):
        print(pd.DataFrame(data))

    # subquote订阅的合约实时行情
    def onquote(self, data):
        # if data['Symbol']=='TC.F.U_SSE.510050.202301':
        print(data)

    # subbar订阅的动态K线数据
    def onbar(self, bartype, interval, symbol, data: list, isreal: bool):
        print("$$$$$$$$$$$$$$$$$$$$$$\n", bartype, "  ", interval, "  ", data[-3], "\n", data[-2], "\n", data[-1])


api = TCoreAPI(apppath="C:/AlgoMaster2/APPs64", eventclass=APIEvent)  #
re = api.connect()  # (appid="AlgoMaster")
time.sleep(1)
api.subATM("TC.O.SSE.510050.202302.C")
# 订阅实时greeks数据
api.subgreeksreal("TC.O.SSE.510050.202301.C.2.5")
# 订阅动态greeks line数据
api.subgreeksline(GreeksType.DOGSK, 1, "TC.F.U_SSE.510050.202302", "2023013101", isinterval=False)
# 订阅实时行情数据
api.subquote("TC.O.SSE.510050.202212.C.2.5")
# 订阅动态bar数据
api.subbar(BarType.MINUTE, 5, "TC.F.CFFEX.T.HOT", starttime="2022120101")
api.subbar(BarType.MINUTE, 5, "TC.F.SHFE.rb.HOT", starttime="2022120101")

api.join()
