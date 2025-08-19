import time
from icetcore import TCoreAPI, QuoteEvent, TradeEvent, BarType
import numpy as np

crash = 1000000
Vanna = 90000  # 此处设定Vanna对应期权总持仓分析的$*0.01,如当前设定当期权总持仓分析的达到900W的时候停止加仓
delta = 0
vega = 0
maxqty = 3
symbol = "TC.S.SSE.510050"

orderobj = {
    "StrategyType": "Vanna",  # 目前固定Vanna 以後不同策略 依此不同處理
    # 交易帳號
    # "BrokerID":"M2_PAPERTRADE",
    # "Account":"y000-zxlee",
    "BrokerID": "AlgoStars_TOUCHANCE",
    "Account": "1999_2-0033361",
    "StrategyID": "20221226",  # 策略ID 同一策略 每次下必須相同 不同策略必須唯一
    "StrategyName": "Vannapy2",  # 自訂義策略名稱
    "UserKey1": "VannaPy",  # 視需要自行帶上
    "UserKey2": "xxxxxx",  # 視需要自行帶上
    # "UserKey3":"xxxxxx",       #TCTradeAPI自動帶上
    # "ProcessID":"xxxxxx",      #TCTradeAPI自動帶上
    "Security": "TC.O.SSE.510050.202212",  # 交易品種月份
    # "StopCondition":"$Vanna="+str(int(vanna*crash)),      #策略停止條件
    # "StopFactor":0.01,
    "StopCondition": "1%$Vanna=90000",
    "StopFactor": 1,
    "CheckCondition1": "$Delta=" + str(delta),  # 策略檢查條件1 文件中日內對沖 X
    "CheckRange1": 0.02,  # 策略檢查條件1 文件中日內對沖 X
    "CheckCondition2": "$Vega=" + str(vega),  # 策略檢查條件1 文件中日內對沖 Y
    "CheckRange2": 0.0001,  # 策略檢查條件1 文件中日內對沖 Y
    "Cash": crash,  # 總資產 若檢查條件1 2 $Delta=0 $Vega=0 採用此欄運算條件
    "Order": [  # 委託下單資料 這例子是下 負Vanna
        {
            "CallPut": "Call",
            "Condition": "Delta=0.25",  # 因虛值要先下到市場 要先下到市場的 擺在前面
            # "Side":2,
            "Qty": maxqty,  # 運用文件中 max運算出的數量
            "Group": "A",  # 同一Group單 會做OCO OTC...
        },
        {
            "CallPut": "Call",
            "Condition": "Delta=0.65",  # 因實質要待虛值那支成交後 才要先下到市場 所以擺在後面
            # "Side":1,
            "Qty": round(maxqty * 0.25 / 0.65),  # 運用文件中 max運算出的數量
            "Group": "A",  # 同一Group單 會做OCO OTC... 無group可不帶
        },
        {
            "CallPut": "Put",
            "Condition": "Delta=-0.25",  # 因虛值要先下到市場 要先下到市場的 擺在前面
            # "Side":1,
            "Qty": 3,  # 運用文件中 max運算出的數量
            "Group": "B",  # 同一Group單 會做OCO OTC...  無group可不帶
        },
        {
            "CallPut": "Put",
            "Condition": "Delta=-0.65",  # 因實質要待虛值那支成交後 才要先下到市場 所以擺在後面
            # "Side":2,
            "Qty": round(maxqty * 0.25 / 0.65),  # 運用文件中 max運算出的數量
            "Group": "B",  # 同一Group單 會做OCO OTC...
        },
    ],
    "GroupAType": 3,  # Group A 要OTO 所以帶3    1:Normal 2:OCO 3:OTO 4:OTOCO  無group可不帶
    "GroupBType": 3,  # Group B 要OTO 所以帶3   無group可不帶
}


class APIEvent(TradeEvent, QuoteEvent):
    def __init__(self) -> None:
        super().__init__()
        self.hisdk = []
        self.his5klen = 0
        self.his5k = []

    def onconnected(self, apitype: str):
        print(apitype)

    def ondisconnected(self, apitype: str):
        print(apitype)

    def onbar(self, datatype, interval, symbol, data: list, isreal: bool):
        if datatype == BarType.DK and interval == 1:
            self.hisdk = data
        if datatype == BarType.MINUTE and interval == 5:
            if self.his5klen and self.his5klen < len(data):
                ma20 = np.mean([x["Close"] for x in self.hisdk[-21:-2]])  # 当日K不参与计算，所以取到倒数-2
                std20 = np.std([x["Close"] for x in self.hisdk[-21:-2]])  # 5分K最新K是Open产生时判断不参与计算，所以取到倒数-2
                bollup = ma20 + 2 * std20
                bolldown = ma20 - 2 * std20
                pos = (self.his5k[-2]["Close"] - bolldown) / (bollup - bolldown)  # 新K的Open价格形成时用上一根完整K的close参与计算，当根K只有open，收盘未产生不参与计算
                vanna = 0.1 * (pos - 0.5)
                # print(pd.DataFrame(hisdk),"\n",pd.DataFrame(his5k))
                print(pos, "  ", vanna)
                if pos > 0.7:
                    orderobj["StopCondition"] = "1%$Vanna=" + str(Vanna)
                    self._tcoreapi.newstrategyorder(orderobj)
                if pos < 0.3:
                    orderobj["StopCondition"] = "1%$Vanna=-" + str(Vanna)
                    self._tcoreapi.newstrategyorder(orderobj)

                # if vanna>-0.09 and vanna<0.09 and flag:
                #     orderobj["StopCondition"]="$Vanna="+str(int(vanna*100*crash))
                #     self._tcoreapi.newstrategyorder(orderobj)
                #     flag=False

                if pos > 0.3 and pos <= 0.5:
                    orderobj["StopCondition"] = "1%$Vanna=0"
                    self._tcoreapi.newstrategyorder(orderobj)
            self.his5klen = len(data)
            self.his5k = data

    def onordereportreal(self, data):
        print(data)

    # def onfilledreportreal(self,data):
    #     print(data)
    # def onorderreportreset(self):
    #     print("onorderreportreset")
    # def onsymbolhistory(self,symboltype,symboldate,symboldict):
    #     print(symboltype,symboldate,symboldict)
    # def onpositionmoniter(self,data):
    #     print(data)


api = TCoreAPI(apppath="C:/AlgoMaster2/APPs64", eventclass=APIEvent)  #
re = api.connect()
time.sleep(1)

api.subbar(BarType.DK, 1, symbol, starttime="2022071900")
api.subbar(BarType.MINUTE, 5, symbol, starttime="2022121900")
accountlist = api.getaccountlist()
print(accountlist)

api.join()
