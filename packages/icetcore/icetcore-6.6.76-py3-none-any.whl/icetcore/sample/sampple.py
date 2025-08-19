import time
from icetcore import TCoreAPI, QuoteEvent, TradeEvent, BarType, GreeksType, OrderStruct, SymbolType, OrderSide, TimeInForce, OrderType, PositionEffect
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
        pass

    # 实时greeks
    def ongreeksreal(self, datatype, symbol, data: dict):
        print("实时\n")
        print(data)
        pass

    # subgreeksline订阅的动态线图数据
    def ongreeksline(self, datatype, interval, symbol, data, isreal):
        print(data)
        pass

    # subquote订阅的合约实时行情
    def onquote(self, data):
        # print(data)
        pass

    # subbar订阅的动态K线数据
    def onbar(self, bartype, interval, symbol, data: list, isreal: bool):
        # print("onbar",self._tcoreapi.getsymbol_session("TC.F.SHFE.rb.HOT"))
        # print("############\n",bartype,"  ",interval,"  ",data[1],"\n",data[2],"\n",data[3])
        print("$$$$$$$$$$$$$$$$$$$$$$\n", bartype, "  ", interval, "  ", print(pd.DataFrame(data)))  # data[-3],"\n",data[-2],"\n",data[-1])

    # server时间
    def onservertime(self, serverdt):
        print("!!!!!!!!!!!!!!!", serverdt)
        pass

    # 资金账户列表，当有资金账户登出或者登入时
    def onaccountlist(self, data, count):
        print(data, count)

    # 群组账号
    def ongroupaccount(self, grouplist, nCount):
        pass

    # #实时委托信息
    def onordereportreal(self, data):
        print(data)

    # #实时成交信息
    def onfilledreportreal(self, data):
        print(data)

    # 账户登出登入时委托资料需要清理通知
    def onorderreportreset(self):
        print("onorderreportreset")

    # #期权持仓监控信息
    # def onpositionmoniter(self,data):
    #     print(data)
    # 账户资金信息更新
    def onmargin(self, accmask, data):
        print("###########", accmask, len(data))

    # 账户持仓信息更新
    def onposition(self, accmask, data):
        print("@@@@@@@@@@", accmask, len(data))

    # 账户组合持仓信息更新
    def oncombposition(self, accmask, data):
        print("$$$$$$$$$$", accmask, len(data))

    # 账户组合指令信息更新
    def oncombinationorder(self, accmask, data):
        print("*********", accmask, len(data))


# 事件消息需要继承api中QuoteEvent和TradeEvent类，并重写对应方法，即可在对应的回调方法收到实时更新事件
# TCoreAPI参数也可以不带入事件类名，不带入事件类就无法收到实时消息，只能使用同步接口方法

# api=TCoreAPI(apppath="C:/AlgoMaster2/APPs64")#

# eventobj=APIEvent()
# api=TCoreAPI(apppath="C:/AlgoMaster2/APPs64",eventclass=eventobj)

api = TCoreAPI(apppath="C:/AlgoMaster2/APPs64(DEV)", eventclass=APIEvent)  #

re = api.connect()
time.sleep(1)
api.submargin()
api.subpositionmoniter()
api.subcombposition()
api.subposition()

accoutlist = api.getaccountlist()
# 获取已登入资金账号列表
print(api.getaccountlist())
# 获取可用的群组账号列表
print(api.getgroupaccount())
# 获取热门月列表，填入时间时返回对应时间的热门对应指定月合约，Key是换月时间，value是指定月
# 获取全部时段换月信息，热门月合约对应的指定月
print(api.gethotmonth("TC.F.CFFEX.T.HOT"))
# 获取指定日期热门月合约对应的指定月
print(api.gethotmonth("TC.F.CFFEX.T.HOT", "20240723", "1000"))
# 获取历史合约信息
print(api.getsymbolhistory(SymbolType.Options, "2022121312"))
# 获取当日合约列表
print(api.getallsymbol())
# 获取合成期货合约列表
print(api.get_u_futuresymbol())
# 获取合约信息
print(api.getsymbol_allinfo("TC.O.SSE.510050.202409.C.2.5"))
# 获取合约上市日期
print(api.getlistingdate("TC.O.SSE.510050.202409.C.2.5"))
# 获取合约到期日
print(api.getexpirationdate("TC.O.SSE.510050.202409.C.2.5"))
# 获取合约最小跳动
print(api.getsymbol_ticksize("TC.O.SSE.510050.202409.C.2.5"))
# 获取合约乘数，合约规格大小
print(api.getsymbolvolume_multiple("TC.O.SSE.510050.202409.C.2.5"))
# 获取合约编码
print(api.getsymbol_id("TC.O.SSE.510050.202409.C.2.5"))

# 模糊查找合约，返回数组，数组中包含dict类型的所有查找结果，dict的key为合约代码，value为合约名称
# 在所有类型合约中查找合约代码中存在rb的合约
print(api.symbollookup("rb"))
# 在期权类型合约中查找合约编码为"90001540"的合约
print(api.symbollookup("10005173", "OPT"))
# 获取合约指定日期时间段类有哪些交易日，交易日日期以list返回
print(api.gettradeingdate("TC.O.SSE.510050.202409.C.2.5", 20230122, 20230822))
# 获取合约剩余交易日还有多少天
print(api.gettradeingdays("TC.O.SSE.510050.202409.C.2.5"))
# 判断某个合约在指定日期，是否为节假日，返回结果：0不是，1是假日
print(api.isholiday("20230108", "TC.F.SHFE.rb.202310"))

# 获取合约交易时段
print(api.getsymbol_session("TC.F.SHFE.rb.HOT"))
# #订阅动态K线数据，数据从onbar回调方法中返回
api.subbar(BarType.MINUTE, 5, "TC.F.CFFEX.T.HOT", starttime="2023082201")
api.subbar(BarType.MINUTE, 5, "TC.O.SSE.510050.202409.C.2.5", starttime="2023082201")  # TC.F.SHFE.rb.HOT
api.subbar(BarType.MINUTE, 1, "TC.F.SHFE.rb.HOT", starttime="2023082201")
api.subbar(BarType.MINUTE, 5, "TC.F.SHFE.rb.HOT", starttime="2023082201")
api.subbar(BarType.DK, 1, "TC.F.SHFE.rb.HOT", starttime="2023012201")
# print(datetime.now())
# 获取历史行情数据
print(pd.DataFrame(api.getquotehistory(BarType.MINUTE, 5, "TC.F.SHFE.au.HOT", starttime="2023082201")))

# 获取ATM
# -2:实值两档期权合约
# -1:实值一档期权合约
#  0:平值期权合约
#  1:虚值期权合约
print(api.getATM("TC.O.SSE.510050.202409.C", 2))

# print(datetime.now()
# 获取历史Greeks
print(api.getgreekshistory(GreeksType.GREEKS1K, 1, "TC.F.U_SSE.510050.202409", "2023082201"))
# 获取合约的greeks数据
print(api.getgreekshistory(GreeksType.DOGSK, 5, "TC.O.SSE.510050.202409.C.2.5", "2023082200", "2023082207"))
# 订阅实时greeks数据
api.subgreeksreal("TC.O.SSE.510050.202409.C.2.5")
# 订阅实时行情数据
api.subquote("TC.O.SSE.510050.202409.C.2.5")
# 订阅动态Greeks线图数据
api.subgreeksline(GreeksType.DOGSK, 5, "TC.O.SSE.510050.202409.C.2.75", starttime="2023082201")  # TC.F.SHFE.rb.HOT

# 获取已登入账户列表
accoutlist = api.getaccountlist()
print(accoutlist)
# 获取账户资金信息
if accoutlist:
    print(api.getaccmargin(accoutlist[0]["AccMask"]))
# 获取账户持仓
print(api.getposition("CTP_NHGPQQ_SIM-8050-90096859"))
# 获取当天全部委托
print(api.getorderreport())
# 获取当天全部挂单，尚未成交的挂单
print(api.getactiveorder())
# 获取当天全部成交回报
filled = api.getfilledreport()
print(len(filled), "  ", filled)
# 获取当天全部成交回报明细
detailfilled = api.getdetailfilledreport()


strAccountMask = ""
if accoutlist:
    print("当前已登入资金账户\n", pd.DataFrame.from_dict(accoutlist[0], orient="index").T)
    # 获取账户列表中的第一个账户
    strAccountMask = accoutlist[0]["AccMask"]
    if strAccountMask != "":
        # 查询组合报单记录
        comborderreport = api.getcombinationorder(strAccountMask)
        print(comborderreport)
        # 查询组合持仓
        combposition = api.getcombposition(strAccountMask)
        print(combposition)
        # 拆分组合持仓
        api.optcombsplit(strAccountMask, combposition[0]["Symbol"], combposition[0]["Quantity"], combposition[0]["CombinationType"], combposition[0]["OptCombID"])
        # 建组合持仓
        api.optcomb(strAccountMask, "TC.O.SSE.510050.202409.C.2.65", "TC.O.SSE.510050.202409.C.2.7", 1, 4)

        # 下单
        OrderStruct.Symbol = "TC.F.CZCE.SR.HOT"
        OrderStruct.BrokerID = accoutlist[0]["BrokerID"]
        OrderStruct.Account = accoutlist[0]["Account"]
        OrderStruct.Price = 4044
        # OrderStruct.StopPrice=4044
        OrderStruct.TimeInForce = TimeInForce.IOC
        OrderStruct.Side = OrderSide.Sell
        OrderStruct.OrderType = OrderType.Limit
        OrderStruct.OrderQty = 100
        OrderStruct.PositionEffect = PositionEffect.Auto
        OrderStruct.Synthetic = 0
        OrderStruct.SelfTradePrevention = 3
        ordkey, msg = api.neworder(OrderStruct)
        for ord in api.getorderinfo(ordkey):
            api.cancelorder(ord["ReportID"])
        print(ordkey, msg)
        if ordkey is not None:
            while True:
                if api.getorderinfo(ordkey):
                    print("#####################新增委托：", api.getorderinfo(ordkey)[-1]["ReportID"])  #
                    time.sleep(2)
                    # 改单
                    api.replaceorder(api.getorderinfo(ordkey)["ReportID"], price=839)
                    # 删单
                    api.cancelorder(api.getorderinfo(ordkey)["ReportID"])
                    break

api.join()
