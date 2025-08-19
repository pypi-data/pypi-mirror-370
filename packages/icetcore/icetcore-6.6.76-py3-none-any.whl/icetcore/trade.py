import os
import uuid
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import pytz
from icetcore.constant import OrderStruct,SpreadOrderStruct,asdict
from comtypes.client import GetEvents
from comtypes import connectionpoints, CoInitializeEx, COINIT_MULTITHREADED, GUID, CoUninitialize, COMError, automation
from comtypes.messageloop import run
from comtypes.client import GetModule, CreateObject
from comtypes.server import IClassFactory
from ctypes import windll, oledll, POINTER, byref
import json
import platform
import threading

def iff(itemvalue, tcsize=1):
    if itemvalue != -9223372036854775808 and itemvalue != "":
        # print("#!@!@#!@",itemvalue,tcsize)
        return int(itemvalue) / tcsize
    elif itemvalue == "":
        return 0
    else:
        return None


def wrap_outparam(punk):
    if not punk:
        return None
    return punk


class TradeEventMeta(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._tcoreapi = None

    @abstractmethod
    def onconnected(self, strapi):
        pass

    @abstractmethod
    def ondisconnected(self, strapi):
        pass

    @abstractmethod
    def onsystemmessage(self, MsgType, MsgCode, MsgString):
        pass

    @abstractmethod
    def onaccountlist(self, data, count):
        pass

    @abstractmethod
    def ongroupaccount(self, grouplist, nCount):
        pass

    @abstractmethod
    def onordereportreal(self, data):
        pass

    @abstractmethod
    def onfilledreportreal(self, data):
        pass

    @abstractmethod
    def onorderreportreset(self):
        pass

    @abstractmethod
    def onpositionmoniter(self, data):
        pass

    @abstractmethod
    def onmargin(self, accmask, data):
        pass

    @abstractmethod
    def onposition(self, accmask, data):
        pass

    @abstractmethod
    def oncombposition(self, accmask, data):
        pass

    @abstractmethod
    def oncombinationorder(self, accmask, data):
        pass


class BaseEvents(metaclass=ABCMeta):
    def __init__(self):
        self.tz = pytz.timezone("Etc/GMT+8")
        self.win32event = windll.kernel32
        self.tradeapi = None
        self.extendevent = None

        self.cmsgevent = self.win32event.CreateEventW(None, 0, 0, None)
        self.qryaccdataevent = self.win32event.CreateEventW(None, 0, 0, None)
        self.symbollistready = False
        self.hotmonthready = False
        self.symblookready = False
        self.symbinfoready = False

        self.accountcout = 0
        self.groupaccout = 0
        self.positioncout = {}
        self.combpositioncout = {}
        self.margincout = {}
        self.combordercout = {}
        self.orderinfo = {}
        self.isbasecurrency = True
        self.issubmargin = False
        self.issubposition = False
        self.issubcombposition = False
        self.issubpositionmoniter = False

    def onconnected(self, strapi):
        if self.extendevent:
            self.extendevent.onconnected(strapi)

    def ondisconnected(self, strapi):
        if self.extendevent:
            self.extendevent.ondisconnected(strapi)

    def onsystemmessage(self, MsgType, MsgCode, MsgString):
        if self.extendevent:
            self.extendevent.onsystemmessage(MsgType, MsgCode, MsgString)

    def onaccountlist(self, accoutlist, count):
        if self.extendevent:
            self.extendevent.onaccountlist(accoutlist, count)

    def ongroupaccount(self, grouplist, nCount):
        if self.extendevent:
            self.extendevent.ongroupaccount(grouplist, nCount)

    def onordereportreal(self, data):
        if data["UserKey1"] in self.orderinfo.keys():
            if data["ReportID"] not in self.orderinfo[data["UserKey1"]]:
                self.orderinfo[data["UserKey1"]].append(data["ReportID"])
        else:
            self.orderinfo[data["UserKey1"]] = [data["ReportID"]]
        if self.extendevent:
            self.extendevent.onordereportreal(data)

    def onfilledreportreal(self, data):
        if self.extendevent:
            self.extendevent.onfilledreportreal(data)

    def onorderreportreset(self):
        if self.extendevent:
            self.extendevent.onorderreportreset()

    def onpositionmoniter(self, data):
        if self.extendevent:
            self.extendevent.onpositionmoniter(data)

    def _getallposition(self,AcctMask, nCount):
        data = []
        for i in range(nCount):
            pos = self.tradeapi.getposition(i, AcctMask)
            data.append(pos)
        self.extendevent.onposition(AcctMask, data)

    def _getallcombposition(self,AcctMask, nCount):
        data = []
        for i in range(nCount):
            combpos = self.tradeapi.getcombposition(i, AcctMask)
            if combpos:
                data.append(combpos)
        self.extendevent.oncombposition(AcctMask, data)

    def _getallcombinationorder(self,AcctMask, nCount):
        data = []
        for i in range(nCount):
            combord = self.tradeapi.getcombinationorder(i, AcctMask)
            data.append(combord)
        self.extendevent.oncombinationorder(AcctMask, data)
    def _getallaccmargin(self,AcctMask, nCount):
        data = []
        for i in range(nCount):
            margin = self.tradeapi.getaccmargin(i, AcctMask)
            if self.isbasecurrency:
                if margin["CurrencyToClient"] == "BaseCurrency":
                    data.append(margin)
            else:
                data.append(margin)
        self.extendevent.onmargin(AcctMask, data)

    def OnCommandMsg(self, MsgType, MsgCode, MsgString):
        if int(MsgType) == 2 and int(MsgCode) == 1:
            self.win32event.SetEvent(self.cmsgevent)
            self.onconnected("trade")
        elif int(MsgType) == 1 and int(MsgCode) == 1:
            self.ondisconnected("trade")
            self.win32event.SetEvent(self.cmsgevent)
            print("登入失败", MsgString)
        elif int(MsgType) == 2 and int(MsgCode) == 0:
            self.ondisconnected("trade")
        else:
            self.onsystemmessage(MsgType, MsgCode, MsgString)

    def OnAccountUpdate(self, nType, AcctMask, nCount):
        if nCount == -100 or nCount == -200:
            return
        if nType == 1:
            self.accountcout = nCount
            if self.extendevent:
                accoutlist = []
                for i in range(nCount):
                    acc = self.tradeapi.getaccoutlist(1, i)
                    accoutlist.append(acc)
                self.onaccountlist(accoutlist, nCount)
        elif nType == 7:
            self.positioncout[AcctMask] = nCount
            if self.extendevent and self.issubposition:
                threading.Thread(
                target=self._getallposition,
                args=(
                    AcctMask,
                    nCount,
                ),
                ).start()
        # elif nType == 8:
        #     self.combpositioncout[AcctMask] = nCount
        #     if self.extendevent and self.issubcombposition:
        #         data = []
        #         for i in range(nCount):
        #             combpos = self.tradeapi.getcombposition(i, AcctMask)
        #             if combpos:
        #                 data.append(combpos)
        #         self.extendevent.oncombposition(AcctMask, data)
        elif nType == 9:
            self.margincout[AcctMask] = nCount
            if self.extendevent and self.issubmargin:
                threading.Thread(
                target=self._getallaccmargin,
                args=(
                    AcctMask,
                    nCount,
                ),
                ).start()

        elif nType == 11:
            self.combpositioncout[AcctMask] = nCount
            self.win32event.SetEvent(self.qryaccdataevent)
            if self.extendevent and self.issubcombposition:
                threading.Thread(
                target=self._getallcombposition,
                args=(
                    AcctMask,
                    nCount,
                ),
                ).start()

        elif nType == 31:
            self.groupaccout = nCount
            if self.extendevent:
                grouplist = []
                for i in range(nCount):
                    acc = self.tradeapi.getaccoutlist(31, i)
                    grouplist.append(acc)
                self.ongroupaccount(grouplist, nCount)

        elif nType == 32:
            self.combordercout[AcctMask] = nCount
            if self.extendevent:
                threading.Thread(
                target=self._getallcombinationorder,
                args=(
                    AcctMask,
                    nCount,
                ),
                ).start()

        # elif nType==100:
        #     print("ADT_ACCOUNT_DATA_READY")
        # print("OnAccountUpdate",nType, AcctMask, nCount,datetime.strftime(datetime.now(),"%Y%m%d %H:%M:%S"))

    def OnExecutionReport(self, strReportID):
        self.onordereportreal(self.tradeapi.getreportbyid(strReportID))

    def OnFilledReport(self, strReportID):
        realFilled = self.tradeapi.getfilledreportbyid(strReportID)
        realFilled["ReportID"] = strReportID.split("-")[0]
        self.onfilledreportreal(realFilled)

    def OnPositionTracker(self):
        if self.extendevent and self.issubpositionmoniter:
            threading.Thread(
                target=self.onpositionmoniter,
                args=(
                    self.tradeapi.getpositionmoniter(),
                ),
                ).start()

    def OnReportReset(self):
        self.onorderreportreset()

    def OnSetTopic(self, strTopic, lParam, strParam, pvParam):
        v = automation.VARIANT()
        automation._VariantCopyInd(v, pvParam)
        sym = None
        if os.path.exists(v.value):
            with open(v.value.replace("\\", "/"), "rb+") as symblist:
                symbolstr = symblist.read().decode(encoding="utf16")
                symbolstr = symbolstr.encode("utf-8")
                sym = json.loads(symbolstr)
                # self.onsymbolhistory(strParam,lParam,sym)
        else:
            icmpathlist = v.value.split("\\")
            icmpath = icmpathlist[0] + "/" + icmpathlist[1] + "/" + icmpathlist[2] + "/" + icmpathlist[3] + "/Configs/ContractList_" + strParam.replace("History-", "") + ".ini"
            print("无历史合约,当前返回今日合约数据")
            with open(icmpath.replace("\\", "/"), "rb+") as symblist:
                symbolstr = symblist.read().decode(encoding="utf16")
                symbolstr = symbolstr.replace('"I.', '"TC.')
                symbolstr = symbolstr.encode("utf-8")
                sym = json.loads(symbolstr)
                for opt in sym["Node"]:
                    if "Node" in opt.keys():
                        for optlist in opt["Node"]:
                            if "OPT" in strParam:
                                for optlist2 in optlist["Node"]:
                                    for syblist in optlist2["Node"]:
                                        syblist["InstrumentID"] = []
                                        syblist["ExpirationDate"] = []
                                        syblist["TradeingDays"] = []
                                        for symb in syblist["Contracts"]:
                                            syblist["InstrumentID"].append(self.tradeapi.getsymbol_id(symb))
                                            syblist["ExpirationDate"].append(self.tradeapi.getexpirationdate(symb))
                                            syblist["TradeingDays"].append(self.tradeapi.gettradeingdays(symb))
                            else:
                                optlist["InstrumentID"] = []
                                optlist["ExpirationDate"] = []
                                optlist["TradeingDays"] = []
                                for symb in optlist["Contracts"]:
                                    if "000000" in symb:
                                        optlist["InstrumentID"].append("")
                                        optlist["ExpirationDate"].append("")
                                        optlist["TradeingDays"].append("")
                                    else:
                                        optlist["InstrumentID"].append(self.tradeapi.getsymbol_id(symb))
                                        optlist["ExpirationDate"].append(self.tradeapi.getexpirationdate(symb))
        self.onsymbolhistory(strParam.replace("History-", ""), lParam, sym)
        self.tradeapi.topicunsub("ICECREAM.RETURN")

    def OnSymbolClassificationsUpdate(self):
        self.symbollistready = True

    def OnHotMonthUpdate(self):
        self.hotmonthready = True

    def OnSymbolLookupUpdate(self):
        self.symblookready = True

    def OnInstrumentInfoUpdate(self):
        self.symbinfoready = True
    # def OnGeneralQueryReturn(self,lIndex, strQueryName, varQueryResult):
    #     v = automation.VARIANT()
    #     automation._VariantCopyInd(v, varQueryResult)
        # print(lIndex, strQueryName, v.value)
    # def OnExecTCReport(self, ReportID):
    #     print("$$$$$$$$$$$$$$$$$$$$$",ReportID)
    #     self.onordereport(self.tradeapi.getreportbyid(ReportID))
    # def OnExtendReport(self, nType, strReportData):
    #     if nType==32:
    #         print("OnExtendReport",nType, strReportData)
    # def OnCancelReplaceError(self, strReportID):
    #     print("OnCancelReplaceError",strReportID)
    # def OnSpreadReport(self, bstrSpdReportID):
    #     print("OnSpreadReport",bstrSpdReportID)
    # def OnSpreadPosition(self, bstrSpdSymbol):
    #     print("OnSpreadPosition",bstrSpdSymbol)


class TradeClass:
    def __init__(self, eventclass: type, dllpath, debugmode=None):
        POINTER(automation.IDispatch).__ctypes_from_outparam__ = wrap_outparam  # type: ignore
        self.apppath = dllpath
        apidll = ""
        self.connresult=None
        
        self.eventobj = BaseEvents()
        self.eventobj.tradeapi = self
        self.eventobj.extendevent = eventclass
        if platform.architecture()[0] == "64bit":
            apidll = dllpath + "/TCoreRelease/Components/TCTradeWrapperAPI64.dll"
        else:
            apidll = dllpath + "/TCoreRelease/Components/TCTradeWrapperAPI.dll"
        self.mod = GetModule(apidll)
        self.dll = oledll.LoadLibrary(apidll)
        clsid = self.mod.CTCTradeAPIEx._reg_clsid_
        ptradefac = self.mod.ICTCTradeAPIEx
        self.ptrade = self.createDispatch(clsid, ptradefac)
        # CreateObject("TCore.TradeAPIEx.1")
        # self.cookie = git.RegisterInterfaceInGlobal(self.ptrade)
        self.tz = pytz.timezone("Etc/GMT+8")
        self.debuglevel = debugmode
        self.ordererr = {
            "-10": "unknow error",
            "-11": "买卖别错误",
            "-12": "复式单商品代码解晰错误",
            "-13": "下单账号, 不可下此交易所商品",
            "-14": "下单错误, 不支持的价格 或 OrderType 或 TimeInForce ",
            "-15": "不支援证券下单",
            "-20": "联机未建立",
            "-22": "价格的 TickSize 错误",
            "-23": "下单数量超过该商品的上下限",
            "-24": "下单数量错误",
            "-25": "价格不能小于和等于 0 (市价类型不会去检查)",
            "-34": " 不支持的合约",
            "-38": " 无API下单权限",
            "-99": " 暂停支援",
        }

    def createDispatch(self, clsid, modulefactpry):
        interface = POINTER(IClassFactory)()
        self.dll.DllGetClassObject(byref(clsid), byref(GUID("{00000001-0000-0000-C000-000000000046}")), byref(interface))
        disp = interface.CreateInstance(POINTER(modulefactpry)(), modulefactpry)
        return disp

    def get_fileversion(self, filename):
        parser = CreateObject("Scripting.FileSystemObject")
        version = parser.GetFileVersion(filename)
        return version

    # 注册事件
    def connect(self, appid: str, servicekey: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            # disp = git.GetInterfaceFromGlobal(self.cookie)
            # interp=GetBestInterface(disp)
            interface = self.mod._ICTCTradeAPIExEvents
            self.connresult=GetEvents(self.ptrade,self.eventobj,interface)
            self.ptrade.Connect(".", appid, servicekey, 1)
            self.setaccountsubscriptionlevel(3)

    def disconnect(self):
        try:
            self.ptrade.Disconnect()
            CoUninitialize()
        except COMError as e:
            print("连接错误:", e)

    def getexpirationdate(self, symbol: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                expirationdate = self.ptrade.GetExpirationDate(symbol)
                if self.debuglevel and not expirationdate:
                    self.writelog("getexpirationdate为空:{0}".format(symbol))
                return expirationdate
            except Exception as e:
                if self.debuglevel:
                    self.writelog("getexpirationdate:{0},{1}".format(symbol, e))
                print("getexpirationDate错误:", e)

    # 获取剩余交易日
    def gettradeingdays(self, symbol: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                lEndDate = self.getexpirationdate(symbol)
                if lEndDate:
                    return self.ptrade.GetTradeingDays(symbol, int(lEndDate))
                else:
                    if self.debuglevel:
                        self.writelog("gettradeingdays 到期日数据错误:{0}".format(symbol))
                    raise Exception("到期日数据错误")
            except Exception as e:
                if self.debuglevel:
                    self.writelog("gettradeingdays:{0},{1}".format(symbol, e))
                print("gettradeingdays错误:", e)

    # 获取剩余交易日
    def gettradeingdate(self, symbol: str, startDate: str, endDate: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                tradingdate = self.ptrade.GetTradeingDate(symbol, int(startDate), int(endDate))
                if self.debuglevel and not tradingdate:
                    self.writelog("gettradeingdate:{0},{1},{2}".format(symbol, startDate, endDate))
                return tradingdate
            except COMError as e:
                if self.debuglevel:
                    self.writelog("gettradeingdate:{0},{1},{2}".format(symbol, startDate, endDate))
                print("gettradeingdays错误:", e)

    def gethotmonth(self, symbol: str, strdate="", strtime=""):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                temp = {}
                if strdate and strtime:
                    strhot = self.ptrade.GetHotMonthByDateTime(symbol, str(strdate), str(strtime))
                    if self.debuglevel and not strhot:
                        self.writelog("gethotmonth为空:{0},{1},{2}".format(symbol, strdate, strtime))
                    hot = strhot.split("~")[0].split(":")
                    temp[datetime.strptime(str(hot[1]), "%Y%m%d%H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)] = hot[0]
                    return temp
                else:
                    self.ptrade.GetHotMonthByDateTime(symbol, str(strdate), str(strtime))
                    with open("C:\\ProgramData\\TCore\\HotChange\\" + symbol + ".txt", "r+") as symblist:
                        for count, line in enumerate(symblist):
                            if count != 0:
                                linedata = line.split("->")
                                temp[
                                    datetime.strptime(linedata[0] + " " + self.getsymbol_session(symbol).split(";")[-1].split("~")[-1], "%Y%m%d %H:%M").replace(tzinfo=self.tz)
                                    + timedelta(hours=8)
                                    + timedelta(seconds=1)
                                ] = symbol.replace("HOT", str(linedata[1].strip("\n")))
                    return temp
            except COMError as e:
                if self.debuglevel:
                    self.writelog("gethotmonth:{0},{1},{2},{3}".format(symbol, strdate, strtime, e.details))
                print("gethotmonth错误:", e)

    def subsymbolhistory(self, symboltype, dt):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            if os.path.exists(self.apppath + "/TCoreRelease/Configs/ContractList_" + symboltype + ".ini"):
                with open(self.apppath + "/TCoreRelease/Configs/ContractList_" + symboltype + ".ini", "rb+") as symblist:
                    symbolstr = symblist.read().decode(encoding="utf16")
                    if "VOLTRADER_" in symbolstr:
                        self.topicsub("ICECREAM.RETURN")
                        self.topicpublish("ICECREAM.RECOVER", int(dt), symboltype, None)
                    else:
                        self.topicsub("ICECREAM.RETURN")
                        self.topicpublish("ICECREAM.RECOVER", int(dt), "History-" + symboltype, None)
            else:
                self.topicsub("ICECREAM.RETURN")
                self.topicpublish("ICECREAM.RECOVER", int(dt), symboltype, None)

    def getsymbol_ticksize(self, symbol: str):
        return float(self._getsymbolInfo("2", symbol))

    def getsymbol_session(self, symbol: str):
        return self._getsymbolInfo("3", symbol)

    def getsymbolvolume_multiple(self, symbol: str):
        return float(self._getsymbolInfo("6", symbol))

    def getsymbol_id(self, symbol: str):
        symbsplit=symbol.split(".")
        if ".HOT/H" in symbol and "TC.F." in symbol:
            return symbsplit[3]+"HOT/H"
        elif ".HOT/Q" in symbol and "TC.F." in symbol:
            return symbsplit[3]+"HOT/Q"
        elif ".HOT" in symbol and "TC.F." in symbol and "/" not in symbol:
            return symbsplit[3]+"HOT"
        elif ".HOT" in symbol and "TC.O." in symbol:
            return symbsplit[3]+"HOT-"+symbsplit[5]+"-"+symbol.replace("TC.O."+symbsplit[2]+"."+symbsplit[3]+"."+symbsplit[4]+"."+symbsplit[5],"").replace(".","")
        elif ".000000" in symbol and "TC.F." in symbol:
            return symbsplit[3]+"0000"
        else:
            return self._getsymbolInfo("Instrument", symbol)


    def getsymbol_allinfo(self, symbol: str):
        return self._getsymbolInfo("ALL", symbol)

    def _getsymbolInfo(self, strType: str, symbol: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.GetInstrumentInfo(strType, symbol)
            except COMError as e:
                print("getsymbolInfo错误:", e)

    def getallsymbol(self, symboltype="", exchange="", month=""):
        symbolist = []
        if symboltype == "" or symboltype in "FUTURES":
            ex = self.__getsymbollist("FUT", "", "", "", "")
            for y1 in [x1.split(",")[0] for x1 in ex.split("|")]:
                if exchange == "" or exchange in y1:
                    ex1 = self.__getsymbollist("FUT", y1, "", "", "")
                    for y2 in [x2.split(",")[0] for x2 in ex1.split("|")]:
                        if month == "":
                            if "HOT" not in y2:
                                ex2 = self.__getsymbollist("FUT", y1, y2, "", "")
                                for x3 in ex2.split("|"):
                                    symbol= x3.split(",")[0]
                                    symbolist.append(symbol)
                                    if "000000" in symbol:
                                        symbolist.append(symbol.replace("000000","HOT"))
                                        symbolist.append(symbol.replace("000000","HOT")+"/Q")
                                        symbolist.append(symbol.replace("000000","HOT")+"/H")
                                # symbolist = symbolist + [x3.split(",")[0] for x3 in ex2.split("|")]
                        else:
                            if month in y2:
                                ex2 = self.__getsymbollist("FUT", y1, y2, "", "")
                                symbolist = symbolist + [x3.split(",")[0] for x3 in ex2.split("|")]
        if symboltype == "" or symboltype in "OPTIONS":
            ex = self.__getsymbollist("OPT", "", "", "", "")
            for y1 in [x1.split(",")[0] for x1 in ex.split("|")]:
                if exchange == "" or exchange in y1:
                    ex1 = self.__getsymbollist("OPT", y1, "", "", "")
                    for y2 in [x2.split(",")[0] for x2 in ex1.split("|")]:
                        ex2 = self.__getsymbollist("OPT", y1, y2, "", "")
                        for y3 in [x3.split(",")[0] for x3 in ex2.split("|")]:
                            if month == "":
                                if "HOT" not in y3:
                                    ex3 = self.__getsymbollist("OPT", y1, y2, y3, "Call")
                                    symbolist = symbolist + [x4.split(",")[0] for x4 in ex3.split("|")]
                                    ex4 = self.__getsymbollist("OPT", y1, y2, y3, "Put")
                                    symbolist = symbolist + [x5.split(",")[0] for x5 in ex4.split("|")]
                                else:
                                    ex3 = self.__getsymbollist("OPT", y1, y2, y3, "Call")
                                    for x4 in ex3.split("|"):
                                        symbol= x4.split(",")[0]
                                        symbsplit=symbol.split(".")
                                        symbolist.append(symbol.replace(symbsplit[4],"HOT"))
                                        symbolist.append(symbol.replace(symbsplit[4],"HOT").replace(".C.",".P."))
                            else:
                                if month in y3:
                                    ex3 = self.__getsymbollist("OPT", y1, y2, y3, "Call")
                                    symbolist = symbolist + [x4.split(",")[0] for x4 in ex3.split("|")]
                                    ex4 = self.__getsymbollist("OPT", y1, y2, y3, "Put")
                                    symbolist = symbolist + [x5.split(",")[0] for x5 in ex4.split("|")]
        if symboltype == "" or symboltype in "STKSTOCKS":
            ex = self.__getsymbollist("STK", "", "", "", "")
            for y1 in [x.split(",")[0] for x in ex.split("|")][0:2]:
                if exchange == "" or exchange in y1:
                    ex1 = self.__getsymbollist("STK", y1, "", "", "")
                    for y2 in [x1.split(",")[0] for x1 in ex1.split("|")]:
                        ex2 = self.__getsymbollist("STK", y1, y2, "", "")
                        for x2 in ex2.split("|"):
                            symbol=x2.split(",")[0]
                            symbolist.append(symbol)
                            if "TC.S.SSE.000" not in symbol and "TC.S.SZSE.399" not in symbol:
                                symbolist.append(symbol+"/Q")
                                symbolist.append(symbol+"/H")
                        # symbolist = symbolist + [x2.split(",")[0] for x2 in ex2.split("|")]
        return symbolist
    
    def getsynu_futuresymbol(self):
        symbolist = []
        ex = self.__getsymbollist("SYMSELECT", "", "", "", "")
        for y1 in [x1.split(",")[0] for x1 in ex.split("|")]:
            ex1 = self.__getsymbollist("SYMSELECT", y1, "SynU", "", "")
            for y2 in [x2.split(",")[0] for x2 in ex1.split("|")]:
                ex2 = self.__getsymbollist("SYMSELECT", y1, "SynU", y2, "")
                symbolist = symbolist + [x3.split(",")[0] for x3 in ex2.split("|")]
                # symbolist=symbolist+[{"symbol":x3.split(",")[0],"name":x3.split(",")[1]} for x3 in ex2.split("|")]
        return symbolist

    def __getsymbollist(self, Classify, Exchange, Symbol, Month, CallPut):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                re = self.ptrade.GetSymbolClassifications(Classify, Exchange, Symbol, Month, CallPut)
                if self.debuglevel and not re:
                    self.writelog("GetSymbolClassifications为空:{0},{1},{2},{3},{4}".format(Classify, Exchange, Symbol, Month, CallPut))
                return re
            except COMError as e:
                print("getsymbol错误:", e)

    def cancelorder(self, reportID: str, orderkey: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                re = self.ptrade.CancelOrder(reportID, orderkey)
                if self.debuglevel and re <= 0:
                    self.writelog("python cancelorder:{0},{1},{2}".format(reportID, orderkey, re))
                return re
            except COMError as e:
                if self.debuglevel:
                    self.writelog("python cancelorder:{0},{1},{2}".format(reportID, orderkey, e))
                print("CancelOrder错误:", e)

    def changeorderaction(self, bstrReportID, lAction):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.ChangeOrderAction(bstrReportID, lAction)
            except COMError as e:
                print("CancelOrder错误:", e)

    def optcomb(self, strAcctMask, SymbolA, SideA, SymbolB,SideB, Volume: int, CombinationType: int, CombID=""):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            strParam = "SYMBOLA=" + SymbolA +"&SIDEA=" + str(SideA) + "&SYMBOLB=" + SymbolB+ "&SIDEB=" + str(SideB) + "&VOLUME=" + str(Volume) + "&ACTIONTYPE=1" + "&OPTCOMB_CODE=" + str(CombinationType) + "&OPTCOMB_ID=" + CombID
            return self._generalquery(1, "OPTCOMB", strParam, 1, strAcctMask)

    def optcombsplit(self, strAcctMask, Symbol: str, Volume: int, CombinationType: int, CombID=""):  # strParam &SIDEA=2&SIDEB=2
        #if "&" not in Symbol:
        #     symlist = Symbol.split("&")[0].split(".")
        # else:
        #    print("合约代码格式错误，组合合约才可拆分")
        #    return
        # temp = symlist[0] + "." + symlist[1] + "." + symlist[2] + "."
        # Symbol = Symbol.replace(temp, "")
        # Symbol = Symbol.replace("&", "^")
        # Symbol = symlist[0] + "." + symlist[1] + "2." + symlist[2] + "." + Symbol
        strParam = "SYMBOL=" + Symbol + "&VOLUME=" + str(Volume) + "&ACTIONTYPE=2" + "&OPTCOMB_CODE=" + str(CombinationType) + "&OPTCOMB_ID=" + CombID
        return self._generalquery(1, "OPTCOMB", strParam, 1, strAcctMask)

    def _generalquery(self, lIndex, strQueryName, strQueryParam, lContentEncodeType, strAcctMask):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.GeneralQuery(lIndex, strQueryName, strQueryParam, lContentEncodeType, strAcctMask)
            except COMError as e:
                print("CancelOrder错误:", e)

    def getaccoutlist(self, acctype, index):
        clsid = self.mod.ADIAccount._reg_clsid_
        accitemfac = self.mod.adiAccountItem
        accitem = self.createDispatch(clsid, accitemfac)
        if self._getaccountdata(acctype, index, "", accitem) == 1:
            return {
                "AccMask": accitem.BrokerID + "-" + accitem.Account,
                "Account": accitem.Account,
                "AccountName": accitem.AccountName,
                "AccountType": accitem.AccountType,
                "BrokerID": accitem.BrokerID,
                "BrokerName": accitem.BrokerName,
                "ItemType": accitem.ItemType,
                "LoginID": accitem.LoginID,
                "OrderExchange": accitem.OrderExchange,
                "Status": accitem.Status,
                "UserAddGroup": accitem.UserAddGroup,
                "UserName": accitem.UserName,
            }

    def getaccmargin(self, index, accmast):
        try:
            marginmuil = 1000000
            clsid = self.mod.ADIMargin._reg_clsid_
            marginitemfac = self.mod.adiMarginItem
            marginitem = self.createDispatch(clsid, marginitemfac)
            if self._getaccountdata(9, index, accmast, marginitem) == 1:
                return {
                    "BrokerID": marginitem.BrokerID,
                    "LoginID": marginitem.LoginID,
                    "UserName": marginitem.UserName,
                    "BrokerName": marginitem.BrokerName,
                    "Account": marginitem.Account,
                    "AccountName": marginitem.AccountName,
                    "TransactDate": marginitem.TransactDate,
                    "TransactTime": marginitem.TransactTime,
                    "BeginningBalance": iff(marginitem.BeginningBalance, marginmuil),
                    "Commissions": iff(marginitem.Commissions, marginmuil),
                    "FrozenCommission": iff(marginitem.FrozenCommission, marginmuil),
                    "ExchangeClearinigFee": iff(marginitem.ExchangeClearinigFee, marginmuil),
                    "BrokerageFee": iff(marginitem.BrokerageFee, marginmuil),
                    "GrossPL": iff(marginitem.GrossPL, marginmuil),
                    "OptionPremium": iff(marginitem.OptionPremium, marginmuil),
                    "CashIn": iff(marginitem.CashIn, marginmuil),
                    "NetPL": iff(marginitem.NetPL, marginmuil),
                    "Deposit": iff(marginitem.Deposit, marginmuil),
                    "Withdraw": iff(marginitem.Withdraw, marginmuil),
                    "CashActivity": iff(marginitem.CashActivity, marginmuil),
                    "ExcessEquity": iff(marginitem.ExcessEquity, marginmuil),
                    "WithdrawQuota": iff(marginitem.WithdrawQuota, marginmuil),
                    "EndingBalance": iff(marginitem.EndingBalance, marginmuil),
                    "OpenTradeEquity": iff(marginitem.OpenTradeEquity, marginmuil),
                    "TotalEquity": iff(marginitem.TotalEquity, marginmuil),
                    "OptionNetMarketValue": iff(marginitem.OptionNetMarketValue, marginmuil),
                    "AccountValueAtMarket": iff(marginitem.AccountValueAtMarket, marginmuil),
                    "InitialMarginRequirement": iff(marginitem.InitialMarginRequirement, marginmuil),
                    "MaintenanceMarginRequirement": iff(marginitem.MaintenanceMarginRequirement, marginmuil),
                    "CurrMargin": iff(marginitem.CurrMargin, marginmuil),
                    "ExchangeMargin": iff(marginitem.ExchangeMargin, marginmuil),
                    "MarginDeficit": iff(marginitem.MarginDeficit, marginmuil),
                    "FrozenMargin": iff(marginitem.FrozenMargin, marginmuil),
                    "FrozenCash": iff(marginitem.FrozenCash, marginmuil),
                    "ReserveBalance": iff(marginitem.ReserveBalance, marginmuil),
                    "Credit": iff(marginitem.Credit, marginmuil),
                    "Mortgage": iff(marginitem.Mortgage, marginmuil),
                    "PreMortgage": iff(marginitem.PreMortgage, marginmuil),
                    "PreCredit": iff(marginitem.PreCredit, marginmuil),
                    "PreDeposit": iff(marginitem.PreDeposit, marginmuil),
                    "PreMargin": iff(marginitem.PreMargin, marginmuil),
                    "DeliveryMargin": iff(marginitem.DeliveryMargin, marginmuil),
                    "ExchangeDeliveryMargin": iff(marginitem.ExchangeDeliveryMargin, marginmuil),
                    "CurrencyToSystem": marginitem.CurrencyToSystem,
                    "CurrencyConversionRate": iff(marginitem.CurrencyConversionRate, marginmuil),
                    "CurrencyToClient": marginitem.CurrencyToClient,
                    "ConvertedAccountValueAtMkt": iff(marginitem.ConvertedAccountValueAtMkt, marginmuil),
                    "ExerciseIncome": iff(marginitem.ExerciseIncome, marginmuil),
                    "IncomeBalance": iff(marginitem.IncomeBalance, marginmuil),
                    "InterestBase": iff(marginitem.InterestBase, marginmuil),
                    "Interest": iff(marginitem.Interest, marginmuil),
                    "MarginLevel": iff(marginitem.GetItemData("MarginLevel"), marginmuil),
                    "UPLForOptions": iff(marginitem.GetItemData("UPLForOptions"), marginmuil),
                    "LongOptionNetMarketValue": iff(marginitem.GetItemData("LongOptionNetMarketValue"), marginmuil),
                    "ShortOptionNetMarketValue": iff(marginitem.GetItemData("ShortOptionNetMarketValue"), marginmuil),
                    "FrozenpPremium": iff(marginitem.GetItemData("FrozenpPremium"), marginmuil),
                    "MarginExcess": iff(marginitem.GetItemData("MarginExcess"), marginmuil),
                    "AdjustedEquity": iff(marginitem.GetItemData("AdjustedEquity"), marginmuil),
                    "PreFundMortgageIn": iff(marginitem.GetItemData("PreFundMortgageIn"), marginmuil),
                    "PreFundMortgageOut": iff(marginitem.GetItemData("PreFundMortgageOut"), marginmuil),
                    "FundMortgageIn": iff(marginitem.GetItemData("FundMortgageIn"), marginmuil),
                    "FundMortgageOut": iff(marginitem.GetItemData("FundMortgageOut"), marginmuil),
                    "FundMortgageAvailable": iff(marginitem.GetItemData("FundMortgageAvailable"), marginmuil),
                    "MortgageableFund": iff(marginitem.GetItemData("MortgageableFund"), marginmuil),
                    "SpecProductMargin": iff(marginitem.GetItemData("SpecProductMargin"), marginmuil),
                    "SpecProductFrozenMargin": iff(marginitem.GetItemData("SpecProductFrozenMargin"), marginmuil),
                    "SpecProductCommission": iff(marginitem.GetItemData("SpecProductCommission"), marginmuil),
                    "SpecProductFrozenCommission": iff(marginitem.GetItemData("SpecProductFrozenCommission"), marginmuil),
                    "SpecProductPositionProfit": iff(marginitem.GetItemData("SpecProductPositionProfit"), marginmuil),
                    "SpecProductCloseProfit": iff(marginitem.GetItemData("SpecProductCloseProfit"), marginmuil),
                    "SpecProductPositionProfitByAlg": iff(marginitem.GetItemData("SpecProductPositionProfitByAlg"), marginmuil),
                    "SpecProductExchangeMargin": iff(marginitem.GetItemData("SpecProductExchangeMargin"), marginmuil),
                    "FloatProfitByDate": iff(marginitem.GetItemData("FloatProfitByDate"), marginmuil),
                    "FloatProfitByTrade": iff(marginitem.GetItemData("FloatProfitByTrade"), marginmuil),
                    "FutureProfitByDay": iff(marginitem.GetItemData("FutureProfitByDay"), marginmuil),
                    "ReferenceRiskRate": iff(marginitem.GetItemData("ReferenceRiskRate"), marginmuil),
                    "TryExcessEquity": iff(marginitem.GetItemData("TryExcessEquity"), marginmuil),
                    "DynamicEquity": iff(marginitem.GetItemData("DynamicEquity"), marginmuil),
                    "MarketPremium": iff(marginitem.GetItemData("MarketPremium"), marginmuil),
                    "OptionPremiumCoin": iff(marginitem.GetItemData("OptionPremiumCoin"), marginmuil),
                    "StockReferenceMarket": iff(marginitem.GetItemData("StockReferenceMarket"), marginmuil),
                    "RiskRate": iff(marginitem.GetItemData("RiskRate"), marginmuil),
                    "StockMarketValue": iff(marginitem.GetItemData("StockMarketValue"), marginmuil),
                    "TheoMktVal": iff(marginitem.GetItemData("TheoMktVal"), marginmuil),
                    "TheoMktValEquity": iff(marginitem.GetItemData("TheoMktValEquity"), marginmuil),
                    "DoUpdate": iff(marginitem.GetItemData("DoUpdate"), 1),
                }

        except COMError as e:
            print("gettradeingdays错误:", e)

    def getposition(self, index, acc):
        try:
            clsid = self.mod.ADIPosition._reg_clsid_
            positemfac = self.mod.adiPositionItem
            positem = self.createDispatch(clsid, positemfac)
            if self._getaccountdata(7, index, acc, positem) == 1:
                return {
                    "AbandonFrozen": positem.AbandonFrozen,
                    "Account": positem.Account,
                    "AccountName": positem.AccountName,
                    "AvgPrice": positem.AvgPrice / 10000000000,
                    "BrokerID": positem.BrokerID,
                    "BrokerName": positem.BrokerName,
                    "CallPut": positem.CallPut,
                    "CallPut2": positem.CallPut2,
                    "CloseProfit": iff(positem.CloseProfit, 10000000000),
                    "CloseProfitByDate": iff(positem.CloseProfitByDate, 10000000000),
                    "CloseProfitByTrade": iff(positem.CloseProfitByTrade, 10000000000),
                    "CloseVolume": positem.CloseVolume if positem.CloseVolume > -2147483648 else 0,
                    "CombLongFrozen": positem.CombLongFrozen,
                    "CombPosition": positem.CombPosition,
                    "CombShortFrozen": positem.CombShortFrozen,
                    "Commission": iff(positem.Commission, 10000000000),
                    "Covered": positem.Covered,
                    "CurrencyToSystem": positem.CurrencyToSystem,
                    "Exchange": positem.Exchange,
                    "FrozenCash": positem.FrozenCash,
                    "FrozenMargin": positem.FrozenMargin,
                    "ItemType": positem.ItemType,
                    "Lock_ExecFrozen": positem.Lock_ExecFrozen,
                    "LoginID": positem.LoginID,
                    "LongAvailable": positem.LongAvailable,
                    "LongAvgPrice": iff(positem.LongAvgPrice, 10000000000),
                    "LongFrozen": positem.LongFrozen,
                    "LongFrozenAmount": positem.LongFrozenAmount,
                    "MatchedPrice1": iff(positem.MatchedPrice1, 10000000000),
                    "MatchedPrice2": iff(positem.MatchedPrice2, 10000000000),
                    "Month": positem.Month,
                    "Month2": positem.Month2,
                    "OpenCost": iff(positem.OpenCost, 10000000000),
                    "OpenDate": positem.OpenDate,
                    "OpenPrice": positem.OpenPrice / 10000000000,
                    "OpenVolume": positem.OpenVolume if positem.OpenVolume > -2147483648 else 0,
                    "PositionCost": iff(positem.PositionCost, 10000000000),
                    "OptCombCode": iff(positem.GetItemData("OptCombCode"), 10000000000),
                    "LongOpenPrice": iff(int(positem.GetItemData("LongOpenPrice")), 10000000000),
                    "ShortOpenPrice": iff(int(positem.GetItemData("ShortOpenPrice")), 10000000000),
                    "TdBuyAvgPrice": iff(positem.GetItemData("TdBuyAvgPrice"), 10000000000),
                    "TdSellAvgPrice": iff(positem.GetItemData("TdSellAvgPrice"), 10000000000),
                    "TdNetAvgPrice": iff(positem.GetItemData("TdNetAvgPrice"), 10000000000),
                    "FloatProfitByDate": iff(positem.GetItemData("FloatProfitByDate"), 10000000000),
                    "FloatProfitByTrade": iff(positem.GetItemData("FloatProfitByTrade"), 10000000000),
                    "LongFloatProfitByDate": iff(positem.GetItemData("LongFloatProfitByDate"), 10000000000),
                    "ShortFloatProfitByDate": iff(positem.GetItemData("ShortFloatProfitByDate"), 10000000000),
                    "LongFloatProfitByTrade": iff(positem.GetItemData("LongFloatProfitByTrade"), 10000000000),
                    "ShortFloatProfitByTrade": iff(positem.GetItemData("ShortFloatProfitByTrade"), 10000000000),
                    "TodayProfit": iff(positem.GetItemData("TodayProfit"), 10000000000),
                    "MarketPrice": iff(positem.GetItemData("MarketPrice"), 1000000),
                    "ExchangeRate": iff(positem.GetItemData("ExchangeRate"), 10000000000),
                    "PosDelta": iff(positem.GetItemData("PosDelta"), 10000000000),
                    "$Delta": iff(positem.GetItemData("$Delta"), 10000000000),
                    "$Gamma": iff(positem.GetItemData("$Gamma"), 10000000000),
                    "$Theta": iff(positem.GetItemData("$Theta"), 10000000000),
                    "$Vega": iff(positem.GetItemData("$Vega"), 10000000000),
                    "$Rho": iff(positem.GetItemData("$Rho"), 10000000000),
                    "PN": iff(positem.GetItemData("PN"), 10000000000),
                    "TheoPN": iff(positem.GetItemData("TheoPN"), 10000000000),
                    "$Charm": iff(positem.GetItemData("$Charm"), 10000000000),
                    "$Vanna": iff(positem.GetItemData("$Vanna"), 10000000000),
                    "$Vomma": iff(positem.GetItemData("$Vomma"), 10000000000),
                    "$Speed": iff(positem.GetItemData("$Speed"), 10000000000),
                    "$Zomma": iff(positem.GetItemData("$Zomma"), 10000000000),
                    "TimeValue": iff(positem.GetItemData("TimeValue"), 10000000000),
                    "TheoMktVa": iff(positem.GetItemData("TheoMktVa"), 10000000000),
                    "1Pct$Vanna": iff(positem.GetItemData("1Pct$Vanna"), 10000000000),
                    "1Pct$Gamma": iff(positem.GetItemData("1Pct$Gamma"), 10000000000),
                    "1PctTd$Gamma": iff(positem.GetItemData("1PctTd$Gamma"), 10000000000),
                    "PreMargin": positem.PreMargin,
                    "PrevSettlementPrice": iff(positem.PrevSettlementPrice, 10000000000),
                    "Quantity": positem.Quantity,
                    "Security": positem.Security,
                    "Security2": positem.Security2,
                    "SecurityType": positem.SecurityType,
                    "SettlementPrice": iff(positem.SettlementPrice, 10000000000),
                    "ShortAvailable": positem.ShortAvailable,
                    "ShortAvgPrice": iff(positem.ShortAvgPrice, 10000000000),
                    "ShortFrozen": positem.ShortFrozen,
                    "ShortFrozenAmount": iff(positem.ShortFrozenAmount, 10000000000),
                    "Side": positem.Side,
                    "Side1": positem.Side1,
                    "Side2": positem.Side2,
                    "StrikeFrozen": positem.StrikeFrozen,
                    "StrikeFrozenAmount": positem.StrikeFrozenAmount,
                    "StrikePrice": iff(positem.StrikePrice, 10000000000),
                    "StrikePrice2": iff(positem.StrikePrice2, 10000000000),
                    "SumLongQty": positem.SumLongQty,
                    "SumShortQty": positem.SumShortQty,
                    "Symbol": positem.Symbol,
                    "SymbolA": positem.SymbolA,
                    "SymbolB": positem.SymbolB,
                    "TdBuyQty": positem.TdBuyQty,
                    "TdSellQty": positem.TdSellQty,
                    "TdTotalQty": positem.TdTotalQty,
                    "TodayLongQty": positem.TodayLongQty,
                    "TodayShortQty": positem.TodayShortQty,
                    "TransactDate": positem.TransactDate,
                    "UsedMargin": iff(positem.UsedMargin, 10000000000),
                    "UserName": positem.UserName,
                    "WorkingLong": positem.WorkingLong,
                    "WorkingShort": positem.WorkingShort,
                    "YdLongQty": positem.YdLongQty,
                    "YdShortQty": positem.YdShortQty,
                }
        except COMError as e:
            print("getposition错误:", e)

    def getcombposition(self, index, acc):
        try:
            marginmuil = 1000000
            clsid = self.mod.ADIPosition._reg_clsid_
            combpositemfac = self.mod.adiPositionItem
            combpositem = self.createDispatch(clsid, combpositemfac)
            if self._getaccountdata(11, index, acc, combpositem) == 1:
                if "^" in combpositem.Symbol:
                    return {
                        "LoginID": combpositem.LoginID,
                        "UserName": combpositem.UserName,
                        "BrokerID": combpositem.BrokerID,
                        "BrokerName": combpositem.BrokerName,
                        "Account": combpositem.Account,
                        "AccountName": combpositem.AccountName,
                        "SecurityType": combpositem.SecurityType,
                        "Symbol": combpositem.GetItemData("Symbol"), #combpositem.SymbolA + "&" + combpositem.SymbolB,  # combpositem.Symbol,
                        "SymbolA": combpositem.SymbolA,
                        "SymbolB": combpositem.SymbolB,
                        "CurrencyToSystem": combpositem.CurrencyToSystem,
                        "OptCombCode": combpositem.GetItemData("OptCombCode") if combpositem.GetItemData("OptCombCode") != "" else combpositem.GetItemData("GroupCode"),
                        "TransactDate": combpositem.TransactDate,
                        "TransactTime": combpositem.TransactTime,
                        "SpreadType": combpositem.GetItemData("SpreadType"),
                        "Side": combpositem.Side,
                        "Side1": combpositem.Side1,
                        "Side2": combpositem.Side2,
                        "Quantity": combpositem.Quantity,
                        "OptCombID": combpositem.GetItemData("OptCombID"),
                        "CombLongPosition": combpositem.GetItemData("CombLongPosition"),
                        "CombShortPosition": combpositem.GetItemData("CombShortPosition"),
                        "UsedMargin": iff(combpositem.UsedMargin, marginmuil),
                        "SplitMargin":iff(combpositem.GetItemVal("SplitMargin"), marginmuil),#组合拆分后保证金
                        "OptCombEnableAmount":combpositem.GetItemVal("OptCombEnableAmount"),
                        "LongSelfCloseVolume":combpositem.GetItemVal("LongSelfCloseVolume"),
                        "ShortSelfCloseVolume":combpositem.GetItemVal("ShortSelfCloseVolume")
                        # // 投机套保标志
                        # inpos.HedgeFlag = adiPosition.GetItemData("HedgeFlag");
                        # inpos.HedgeFlag2 = adiPosition.GetItemData("HedgeFlag2");
                    }
        except COMError as e:
            print("getcombposition错误:", e)

    def getcombinationorder(self, index, acc):
        try:
            clsid = self.mod.adiCombinationOrderItem._reg_clsid_
            comborderfac = self.mod.IadiCombinationOrderItem
            comborder = self.createDispatch(clsid, comborderfac)
            if self._getaccountdata(32, index, acc, comborder) == 1:
                return {
                    "Account": comborder.GetItemData("Account"),
                    "BrokerID": comborder.GetItemData("BrokerID"),
                    "OrderID": comborder.GetItemData("OrderID"),
                    "FilledID": comborder.GetItemData("FilledID"),
                    "Symbol": comborder.GetItemData("Symbol"),
                    # "Symbol": comborder.GetItemData("SymbolA") + "&" + comborder.GetItemData("SymbolB"),
                    "Quantity": comborder.GetItemData("Quantity"),
                    "Side": comborder.GetItemData("Side"),
                    "CombSide": comborder.GetItemData("CombSide"),
                    "ExecType": comborder.GetItemData("ExecType"),
                    "StatusMsg": comborder.GetItemData("StatusMsg"),
                    "insert_time": comborder.GetItemData("InsertTime"),
                    "filled_time": comborder.GetItemData("FilledTime"),
                    "OptCombCode": comborder.GetItemData("OptCombCode") if comborder.GetItemData("OptCombCode") != "" else comborder.GetItemData("GroupCode"),
                    "FilledQuantity": comborder.GetItemData("FilledQuantity"),
                    "SpreadType": comborder.GetItemData("SpreadType"),
                    "SpreadTypeString ": comborder.GetItemData("SpreadTypeString"),
                    "OptCombID": comborder.GetItemData("OptCombID"),
                }
        except COMError as e:
            print("getcombinationorder错误:", e)

    def qrycomborder(self,strAcctMask):
        return self._generalquery(1, "ReQueryOrder", "ACTIONTYPE=2", 1, strAcctMask)
    
    def _getaccountdata(self, nType, nIndex, AcctMask, idispatch):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.GetAccountData(nType, nIndex, AcctMask, idispatch)
            except COMError as e:
                print("_getaccountdata错误:", e)

    def queryaccountdata(self,ltype:int,brokerID:str,account:str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.QueryAccountData(ltype,brokerID,account)
            except COMError as e:
                print("QueryAccountData错误:", e)

    def getpositionmoniter(self):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                clsid = self.mod.adiPositionTracker._reg_clsid_
                outitemfac = self.mod.IadiPositionTracker
                outitem = self.createDispatch(clsid, outitemfac)
                self.ptrade.GetPositionTracker(outitem)
                result = []
                if ";" not in outitem.GetItemKeys():
                    return
                for itemkey in outitem.GetItemKeys().strip(";").split(";"):
                    for subkey in outitem.GetSubKeys(itemkey).strip(";").split(";"):
                        temp = {}
                        if ":" in itemkey:
                            itk = itemkey.split(":")
                            temp["Symbol"] = itk[1]
                            idx = itk[0].find("-")
                            if idx > 0:
                                temp["BrokerID"] = itk[0][0:idx]
                                temp["Account"] = itk[0][idx + 1:]
                            else:
                                temp["BrokerID"] = ""
                                temp["Account"] = itk[0]
                        else:
                            temp["Symbol"] = itemkey
                            temp["BrokerID"] = ""
                            temp["Account"] = ""
                        temp["SubKey"] = subkey
                        temp["$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Delta"), 10000000000)
                        temp["Td$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Delta"), 10000000000)
                        temp["$Gamma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Gamma"), 10000000000)
                        temp["Td$Gamma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Gamma"), 10000000000)
                        temp["Yd$Gamma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Yd$Gamma"), 10000000000)
                        temp["$Theta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Theta"), 10000000000)
                        temp["Td$Theta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Theta"), 10000000000)
                        temp["Yd$Theta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Yd$Theta"), 10000000000)
                        temp["$Vega"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Vega"), 10000000000)
                        temp["Td$Vega"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Vega"), 10000000000)
                        temp["Yd$Vega"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Yd$Vega"), 10000000000)
                        temp["TdSqrt$Vega"] = iff(outitem.GetSubItemValue(itemkey, subkey, "TdSqrt$Vega"), 10000000000)
                        temp["YdSqrt$Vega"] = iff(outitem.GetSubItemValue(itemkey, subkey, "YdSqrt$Vega"), 10000000000)
                        temp["$Rho"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Rho"), 10000000000)
                        temp["Td$Rho"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Rho"), 10000000000)
                        temp["Yd$Rho"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Yd$Rho"), 10000000000)
                        temp["$Charm"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Charm"), 10000000000)
                        temp["Td$Charm"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Charm"), 10000000000)
                        temp["$Vanna"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Vanna"), 10000000000)
                        temp["Td$Vanna"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Vanna"), 10000000000)
                        temp["$Vomma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Vomma"), 10000000000)
                        temp["Td$Vomma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Vomma"), 10000000000)
                        temp["$Speed"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Speed"), 10000000000)
                        temp["Td$Speed"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Speed"), 10000000000)
                        temp["$Zomma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Zomma"), 10000000000)
                        temp["Td$Zomma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Zomma"), 10000000000)
                        temp["TimeValue"] = iff(outitem.GetSubItemValue(itemkey, subkey, "TimeValue"), 10000000000)
                        temp["TdTimeValue"] = iff(outitem.GetSubItemValue(itemkey, subkey, "TdTimeValue"), 10000000000)
                        temp["YdTimeValue"] = iff(outitem.GetSubItemValue(itemkey, subkey, "YdTimeValue"), 10000000000)
                        temp["PnL"] = iff(outitem.GetSubItemValue(itemkey, subkey, "PnL"), 10000000000)
                        temp["TdPnL"] = iff(outitem.GetSubItemValue(itemkey, subkey, "TdPnL"), 10000000000)
                        temp["YdPnL"] = iff(outitem.GetSubItemValue(itemkey, subkey, "YdPnL"), 10000000000)
                        temp["TheoPnL"] = iff(outitem.GetSubItemValue(itemkey, subkey, "TheoPnL"), 10000000000)
                        temp["TdTheoPnL"] = iff(outitem.GetSubItemValue(itemkey, subkey, "TdTheoPnL"), 10000000000)
                        temp["YdTheoPnl"] = iff(outitem.GetSubItemValue(itemkey, subkey, "YdTheoPnl"), 10000000000)
                        temp["FloatPnL"] = iff(outitem.GetSubItemValue(itemkey, subkey, "FloatPnL"), 10000000000)
                        temp["ClosePnL"] = iff(outitem.GetSubItemValue(itemkey, subkey, "ClosePnL"), 10000000000)
                        temp["CallOI"] = outitem.GetSubItemValue(itemkey, subkey, "CallOI")
                        temp["TdCallOI"] = outitem.GetSubItemValue(itemkey, subkey, "TdCallOI")
                        temp["YdCallOI"] = outitem.GetSubItemValue(itemkey, subkey, "YdCallOI")
                        temp["PutOI"] = outitem.GetSubItemValue(itemkey, subkey, "PutOI")
                        temp["TdPutOI"] = outitem.GetSubItemValue(itemkey, subkey, "TdPutOI")
                        temp["YdPutOI"] = outitem.GetSubItemValue(itemkey, subkey, "YdPutOI")
                        temp["LongOI"] = outitem.GetSubItemValue(itemkey, subkey, "LongOI")
                        temp["ShortOI"] = outitem.GetSubItemValue(itemkey, subkey, "ShortOI")
                        temp["TdOpenQty"] = outitem.GetSubItemValue(itemkey, subkey, "TdOpenQty")
                        temp["TdCloseQty"] = outitem.GetSubItemValue(itemkey, subkey, "TdCloseQty")
                        temp["NetFill"] = iff(outitem.GetSubItemValue(itemkey, subkey, "BSFill"))
                        temp["PosFillRatio"] = iff(outitem.GetSubItemValue(itemkey, subkey, "PosFillRatio"), 10000000000)
                        temp["1%$Gamma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "1Pct$Gamma"), 10000000000)
                        temp["1%Td$Gamma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "1PctTd$Gamma"), 10000000000)
                        temp["1%Yd$Gamma"] = iff(outitem.GetSubItemValue(itemkey, subkey, "1PctYd$Gamma"), 10000000000)
                        temp["1%$Vanna"] = iff(outitem.GetSubItemValue(itemkey, subkey, "1Pct$Vanna"), 10000000000)
                        temp["1%Td$Vanna"] = iff(outitem.GetSubItemValue(itemkey, subkey, "1PctTd$Vanna"), 10000000000)
                        temp["TotalFill"] = iff(outitem.GetSubItemValue(itemkey, subkey, "BuyFill")) + iff(outitem.GetSubItemValue(itemkey, subkey, "SellFill"))
                        temp["TotalPosition"] = iff(outitem.GetSubItemValue(itemkey, subkey, "LongOI")) + iff(outitem.GetSubItemValue(itemkey, subkey, "ShortOI"))
                        temp["NetPosition"] = iff(outitem.GetSubItemValue(itemkey, subkey, "LongOI")) - iff(outitem.GetSubItemValue(itemkey, subkey, "ShortOI"))
                        temp["YdNetPosition"] = iff(outitem.GetSubItemValue(itemkey, subkey, "YdCallOI")) + iff(outitem.GetSubItemValue(itemkey, subkey, "YdPutOI"))
                        temp["1%$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "$Delta"), 1000000000000)
                        temp["1%Td$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Td$Delta"), 1000000000000)
                        temp["1%Yd$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Yd$Delta"), 1000000000000)
                        temp["OrderNumbers"] = outitem.GetSubItemValue(itemkey, subkey, "OrderNumbers")
                        temp["DealNumbers"] = outitem.GetSubItemValue(itemkey, subkey, "DealNumbers")
                        temp["DeleteNumbers"] = outitem.GetSubItemValue(itemkey, subkey, "DeleteNumbers")
                        temp["Underly$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "Underly$Delta"), 10000000000)
                        temp["UnderlyTd$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "UnderlyTd$Delta"), 10000000000)
                        temp["UnderlyYd$Delta"] = iff(outitem.GetSubItemValue(itemkey, subkey, "UnderlyYd$Delta"), 10000000000)
                        result.append(temp)
                return result  # outitem.GetItemKeys()
            except COMError as e:
                print("getpositiontracker错误:", e)

    def getproductcurrency(self, SymbolID):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.GetProductCurrency(SymbolID)
            except COMError as e:
                print("getproductcurrency错误:", e)

    def getactiveorder(self):
        try:
            activeorder = []
            clsid = self.mod.RPTReports._reg_clsid_
            ReportItemsfac = self.mod.rptReportItems
            ReportItems = self.createDispatch(clsid, ReportItemsfac)

            if self.__getreportdata(1, "", ReportItems) == 1:
                for i in range(ReportItems.Count):
                    activeorderdict = self.getreportbyid(ReportItems.GetReportID(i))
                    activeorder.append(activeorderdict)
                return activeorder
        except COMError as e:
            print("getactiveorder错误:", e)

    def getorderreport(self):
        try:
            report = []
            clsid = self.mod.RPTReports._reg_clsid_
            ReportItemsfac = self.mod.rptReportItems
            ReportItems = self.createDispatch(clsid, ReportItemsfac)
            if self.__getreportdata(3, "", ReportItems) == 1:
                for i in range(ReportItems.Count):
                    reportdict = self.getreportbyid(ReportItems.GetReportID(i))
                    report.append(reportdict)
                return report
        except COMError as e:
            print("getallorderreport错误:", e)

    def getdetailfilledreport(self):
        try:
            fillreport = []
            clsid = self.mod.RPTReports._reg_clsid_
            ReportItemsfac = self.mod.rptReportItems
            ReportItems = self.createDispatch(clsid, ReportItemsfac)
            if self.__getreportdata(2, "", ReportItems) == 1:
                for i in range(ReportItems.Count):
                    strReportID = ReportItems.GetReportID(i)
                    clsid = self.mod.RPTExecutionReport._reg_clsid_
                    ExecutionReportItemfac = self.mod.rptExecutionReportItem
                    ExecutionReportItem = self.createDispatch(clsid, ExecutionReportItemfac)
                    self.__getreportdata(0, strReportID, ExecutionReportItem)
                    for j in range(ExecutionReportItem.FilledOrdersCount):
                        fillreportdict = self.getfilledreportbyid(ExecutionReportItem.GetFilledOrderReportID(j))
                        fillreportdict["ReportID"] = strReportID
                        fillreport.append(fillreportdict)
                return fillreport
        except COMError as e:
            print("getfilledreport错误:", e)

    def getfilledreport(self):
        try:
            fillreport = []
            clsid = self.mod.RPTReports._reg_clsid_
            ReportItemsfac = self.mod.rptReportItems
            ReportItems = self.createDispatch(clsid, ReportItemsfac)
            if self.__getreportdata(2, "", ReportItems) == 1:
                for i in range(ReportItems.Count):
                    reportdict = self.getreportbyid(ReportItems.GetReportID(i))
                    fillreport.append(reportdict)
                return fillreport
        except COMError as e:
            print("getfilledreport错误:", e)

    def getfilledreportbyid(self, ReportID):
        try:
            clsid = self.mod.RptFilledOrder._reg_clsid_
            FilledOrderItemfac = self.mod.rptFilledOrderItem
            FilledOrderItem = self.createDispatch(clsid, FilledOrderItemfac)
            if self.__getreportdata(0, ReportID, FilledOrderItem) == 1:
                return {
                    "Account": FilledOrderItem.Account,
                    "BrokerID": FilledOrderItem.BrokerID,
                    "CallPut": FilledOrderItem.CallPut,
                    "CallPut2": FilledOrderItem.CallPut2,
                    "Exchange": FilledOrderItem.Exchange,
                    "MatchedPrice": iff(FilledOrderItem.MatchedPrice, 10000000000),
                    "MatchedPrice1": iff(FilledOrderItem.MatchedPrice1, 10000000000),
                    "MatchedPrice2": iff(FilledOrderItem.MatchedPrice2, 10000000000),
                    "MatchedQty": FilledOrderItem.MatchedQty,
                    "Month": FilledOrderItem.Month,
                    "Month2": FilledOrderItem.Month2,
                    "OrderID": FilledOrderItem.OrderID,
                    "PositionEffect": FilledOrderItem.PositionEffect,
                    "DetailReportID": FilledOrderItem.ReportID,
                    "Security": FilledOrderItem.Security,
                    "Security2": FilledOrderItem.Security2,
                    "SecurityType": FilledOrderItem.SecurityType,
                    "Side": FilledOrderItem.Side,
                    "Side1": FilledOrderItem.Side1,
                    "Side2": FilledOrderItem.Side2,
                    "Strategy": FilledOrderItem.Strategy,
                    "StrikePrice": iff(FilledOrderItem.StrikePrice, 10000000000),
                    "StrikePrice2": iff(FilledOrderItem.StrikePrice2, 10000000000),
                    "Symbol": FilledOrderItem.Symbol,
                    "SymbolA": FilledOrderItem.SymbolA,
                    "SymbolB": FilledOrderItem.SymbolB,
                    "TradeType": FilledOrderItem.TradeType,
                    "TransactDate": FilledOrderItem.TransactDate,
                    "TransactTime": FilledOrderItem.TransactTime,
                    "UserKey1": FilledOrderItem.UserKey1,
                    "UserKey2": FilledOrderItem.UserKey2,
                    "UserKey3": FilledOrderItem.UserKey3,
                }
        except COMError as e:
            print("getreportbyid错误:", e)

    def getreportbyid(self, ReportID):
        try:
            clsid = self.mod.RPTExecutionReport._reg_clsid_
            ExecutionReportItemfac = self.mod.rptExecutionReportItem
            ExecutionReportItem = self.createDispatch(clsid, ExecutionReportItemfac)
            if self.__getreportdata(0, ReportID, ExecutionReportItem) == 1:
                return {
                    "Account": ExecutionReportItem.Account,
                    "AvgPrice": iff(ExecutionReportItem.AvgPrice, 10000000000),
                    "BrokerID": ExecutionReportItem.BrokerID,
                    "CallPut": ExecutionReportItem.CallPut,
                    "CallPut2": ExecutionReportItem.CallPut2,
                    "CumQty": ExecutionReportItem.CumQty,
                    "RecFillQty": int(ExecutionReportItem.GetItemData("RecFillQty") if ExecutionReportItem.GetItemData("RecFillQty") else 0),
                    "HedgeFlag": ExecutionReportItem.GetItemData("HedgeFlag"),
                    "SetPRIADJ": ExecutionReportItem.GetItemData("SetPRIADJ"),
                    "DelayTransPosition": ExecutionReportItem.GetItemData("DelayTransPosition"),
                    "SlicedType": int(ExecutionReportItem.GetItemData("SlicedType") if ExecutionReportItem.GetItemData("SlicedType") else 0),
                    "SliceID": ExecutionReportItem.GetItemData("SliceID"),
                    "DayTrade": ExecutionReportItem.DayTrade,
                    "ErrorCode": ExecutionReportItem.ErrorCode,
                    "ExCode": ExecutionReportItem.ExCode,
                    "Exchange": ExecutionReportItem.Exchange,
                    "ExecHis": ExecutionReportItem.ExecHis,
                    "ExecType": ExecutionReportItem.ExecType,
                    "ExecTypeText": ExecutionReportItem.ExecTypeText,
                    "ExtraFields": ExecutionReportItem.ExtraFields,
                    "Group": ExecutionReportItem.Group,
                    "IsRestoreData": ExecutionReportItem.IsRestoreData,
                    "ItemType": ExecutionReportItem.ItemType,
                    "LeavesQty": ExecutionReportItem.LeavesQty,
                    "Month": ExecutionReportItem.Month,
                    "Month2": ExecutionReportItem.Month2,
                    "OrderID": ExecutionReportItem.OrderID,
                    "OrderQty": ExecutionReportItem.OrderQty,
                    "OrderResult": ExecutionReportItem.OrderResult,
                    "OrderStatusCount": ExecutionReportItem.OrderStatusCount,
                    "OrderType": ExecutionReportItem.OrderType,
                    "OrgSource": ExecutionReportItem.OrgSource,
                    "OriginalQty": ExecutionReportItem.OriginalQty,
                    "PositionEffect": ExecutionReportItem.PositionEffect,
                    "Price": iff(ExecutionReportItem.Price, 10000000000),
                    "ReportID": ExecutionReportItem.ReportID,
                    "Security": ExecutionReportItem.Security,
                    "Security2": ExecutionReportItem.Security2,
                    "SecurityType": ExecutionReportItem.SecurityType,
                    "Side": ExecutionReportItem.Side,
                    "Side1": ExecutionReportItem.Side1,
                    "Side2": ExecutionReportItem.Side2,
                    "StopPrice": iff(ExecutionReportItem.StopPrice, 10000000000),
                    "Strategy": ExecutionReportItem.Strategy,
                    "StrikePrice": iff(ExecutionReportItem.StrikePrice, 10000000000),
                    "StrikePrice2": iff(ExecutionReportItem.StrikePrice2, 10000000000),
                    "SubOrdersCount": ExecutionReportItem.SubOrdersCount,
                    "Symbol": ExecutionReportItem.Symbol,
                    "SymbolA": ExecutionReportItem.SymbolA,
                    "SymbolB": ExecutionReportItem.SymbolB,
                    "TimeInForce": ExecutionReportItem.TimeInForce,
                    "TouchCondition": ExecutionReportItem.TouchCondition,
                    "TradeDate": ExecutionReportItem.TradeDate,
                    "TradeType": ExecutionReportItem.TradeType,
                    "TrailingAmount": ExecutionReportItem.TrailingAmount,
                    "TransactDate": ExecutionReportItem.TransactDate,
                    "TransactTime": ExecutionReportItem.TransactTime,
                    "TriggeredPrice": iff(ExecutionReportItem.TriggeredPrice, 10000000000),
                    "UserKey1": ExecutionReportItem.UserKey1,
                    "UserKey2": ExecutionReportItem.UserKey2,
                    "UserKey3": ExecutionReportItem.UserKey3,
                }
        except COMError as e:
            print("getreportbyid错误:", e)

    def __getreportdata(self, ReportType, ReportID, ReportItems):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.GetReportData(ReportType, ReportID, ReportItems)
            except COMError as e:
                print("__getreportdata错误:", e)

    def neworder(self, ordarg: OrderStruct):
        if "TC.S" in ordarg.Symbol:
            ordkey, msg = self.newstockorder(ordarg)
        else:
            ordkey, msg = self.newfutoptorder(ordarg)
        return ordkey, msg
        # 获取委托单信息

    def getorderinfo(self, ordkey):
        orderinfo = []
        if ordkey in self.eventobj.orderinfo.keys():
            for ReportID in self.eventobj.orderinfo[ordkey]:
                orderinfo.append(self.getreportbyid(ReportID))
            return orderinfo
        else:
            return

    def newstockorder(self, stkordarg: OrderStruct):
        clsid = self.mod.NOPStock._reg_clsid_
        stkorditemfac = self.mod.nopStockItem
        stkorditem = self.createDispatch(clsid, stkorditemfac)
        ordid = str(uuid.uuid1())
        stkorditem.Account = stkordarg.Account
        stkorditem.BrokerID = stkordarg.BrokerID
        stkorditem.Symbol = stkordarg.Symbol
        stkorditem.ChasePrice = stkordarg.ChasePrice
        stkorditem.ContingentSymbol = stkordarg.ContingentSymbol
        stkorditem.DiscloseQty = stkordarg.DiscloseQty
        stkorditem.GroupID = stkordarg.GroupID
        stkorditem.GroupType = stkordarg.GroupType
        stkorditem.Interval = stkordarg.Interval
        stkorditem.LeftoverAction = stkordarg.LeftoverAction
        stkorditem.OrderQty = stkordarg.OrderQty
        stkorditem.OrderType = stkordarg.OrderType
        if isinstance(stkordarg.Price, str):
            stkorditem.Price = stkordarg.Price
        else:
            stkorditem.Price = "{:.0f}".format(stkordarg.Price * 10000000000)
        if isinstance(stkordarg.StopPrice, str):
            stkorditem.StopPrice = stkordarg.StopPrice
        else:
            stkorditem.StopPrice = "{:.0f}".format(stkordarg.StopPrice * 10000000000)
        stkorditem.Side = stkordarg.Side
        stkorditem.SlicedType = stkordarg.SlicedType
        stkorditem.Strategy = stkordarg.Strategy
        stkorditem.Synthetic = stkordarg.Synthetic
        stkorditem.TimeInForce = stkordarg.TimeInForce
        stkorditem.TouchCondition = stkordarg.TouchCondition
        stkorditem.TouchField = stkordarg.TouchField
        if isinstance(stkordarg.TouchPrice, str):
            stkorditem.TouchPrice = stkordarg.TouchPrice
        else:
            stkorditem.TouchPrice = "{:.0f}".format(stkordarg.TouchPrice * 10000000000)
        stkorditem.TrailingAmount = stkordarg.TrailingAmount
        stkorditem.TrailingField = stkordarg.TrailingField
        stkorditem.TrailingType = stkordarg.TrailingType
        stkorditem.UserKey1 = ordid
        stkorditem.UserKey2 = stkordarg.UserKey2
        # stkorditem.UserKey3="tcoreapi.py"
        stkorditem.Variance = stkordarg.Variance
        # 是否启用流控
        stkorditem.ExtCommands = stkordarg.ExtCommands + "FlowControl=" + str(stkordarg.FlowControl)
        # 是否启用自适应
        stkorditem.ExtCommands = stkorditem.ExtCommands + ",FitOrderFreq=" + str(stkordarg.FitOrderFreq)
        # 是否自成交锁定
        stkorditem.ExtCommands = stkorditem.ExtCommands + ",SelfTradePrevention=" + str(stkordarg.SelfTradePrevention)
        stkorditem.ExCode = stkordarg.ExCode
        stkorditem.Exchange = stkordarg.Exchange
        stkorditem.TradeType = stkordarg.TradeType
        stkorditem.MaxPriceLevels = stkordarg.MaxPriceLevels
        stkorditem.Security = stkordarg.Security
        stkorditem.Breakeven = stkordarg.Breakeven
        stkorditem.BreakevenOffset = stkordarg.BreakevenOffset

        ordresult = self._neworder(8, stkorditem)
        if ordresult >= 1:
            return ordid, "委托成功"
        else:
            errmsg = ""
            if str(ordresult) in self.ordererr.keys():
                errmsg = self.ordererr[str(ordresult)]
                print(self.ordererr[str(ordresult)])
            else:
                errmsg = str(ordresult)
            return None, errmsg

    def newfutoptorder(self, ordargs: OrderStruct):
        clsid = self.mod.NOPFutOpt._reg_clsid_
        futoptorditemfac = self.mod.nopFutOptItem
        futoptorditem = self.createDispatch(clsid, futoptorditemfac)

        ordid = str(uuid.uuid1())

        futoptorditem.Account = ordargs.Account
        futoptorditem.BrokerID = ordargs.BrokerID
        futoptorditem.Symbol = ordargs.Symbol
        futoptorditem.Side = ordargs.Side
        futoptorditem.OrderQty = ordargs.OrderQty
        futoptorditem.OrderType = ordargs.OrderType
        futoptorditem.TimeInForce = ordargs.TimeInForce
        futoptorditem.PositionEffect = ordargs.PositionEffect
        if isinstance(ordargs.Price, str):
            futoptorditem.Price = ordargs.Price
        else:
            futoptorditem.Price = "{:.0f}".format(ordargs.Price * 10000000000)
        if isinstance(ordargs.StopPrice, str):
            futoptorditem.StopPrice = ordargs.StopPrice
        else:
            futoptorditem.StopPrice = "{:.0f}".format(ordargs.StopPrice * 10000000000)
        futoptorditem.ContingentSymbol = ordargs.ContingentSymbol
        futoptorditem.GroupID = ordargs.GroupID
        futoptorditem.UserKey1 = ordid
        futoptorditem.UserKey2 = ordargs.UserKey2
        # futoptorditem.UserKey3=ordargs.UserKey3
        futoptorditem.Strategy = ordargs.Strategy
        futoptorditem.ChasePrice = ordargs.ChasePrice
        if isinstance(ordargs.TouchPrice, str):
            futoptorditem.TouchPrice = ordargs.TouchPrice
        else:
            futoptorditem.TouchPrice = "{:.0f}".format(ordargs.TouchPrice * 10000000000)
        futoptorditem.TouchField = ordargs.TouchField
        futoptorditem.TouchCondition = ordargs.TouchCondition
        futoptorditem.Exchange = ordargs.Exchange
        futoptorditem.Breakeven = ordargs.Breakeven
        futoptorditem.BreakevenOffset = ordargs.BreakevenOffset
        # 是否启用流控
        futoptorditem.ExtCommands = ordargs.ExtCommands + "FlowControl=" + str(ordargs.FlowControl)
        # 是否启用自适应
        futoptorditem.ExtCommands = futoptorditem.ExtCommands + ",FitOrderFreq=" + str(ordargs.FitOrderFreq)
        # 是否平仓反向延时
        futoptorditem.ExtCommands = futoptorditem.ExtCommands + ",DelayTransPosition=" + str(ordargs.DelayTransPosition)
        # 是否自成交锁定
        futoptorditem.ExtCommands = futoptorditem.ExtCommands + ",SelfTradePrevention=" + str(ordargs.SelfTradePrevention)
        futoptorditem.ExtCommands = ordargs.ExtCommands + ",SelfTradePrevention=" + str(ordargs.SelfTradePrevention)
        futoptorditem.GrpAcctOrdType = ordargs.GrpAcctOrdType
        futoptorditem.SpreadType = ordargs.SpreadType
        futoptorditem.Synthetic = ordargs.Synthetic
        futoptorditem.SymbolA = ordargs.SymbolA
        futoptorditem.SymbolB = ordargs.SymbolB
        futoptorditem.Security = ordargs.Security
        futoptorditem.Security2 = ordargs.Security2
        futoptorditem.Month = ordargs.Month
        futoptorditem.Month2 = ordargs.Month2
        futoptorditem.CallPut = ordargs.CallPut
        futoptorditem.CallPut2 = ordargs.CallPut2
        futoptorditem.Side1 = ordargs.Side1
        futoptorditem.Side2 = ordargs.Side2
        futoptorditem.TrailingField = ordargs.TrailingField
        futoptorditem.TrailingType = ordargs.TrailingType
        futoptorditem.TrailingAmount = ordargs.TrailingAmount
        futoptorditem.SlicedType = ordargs.SlicedType
        futoptorditem.SlicedPriceField = ordargs.SlicedPriceField
        futoptorditem.SlicedTicks = ordargs.SlicedTicks
        futoptorditem.DayTrade = ordargs.DayTrade
        futoptorditem.GroupType = ordargs.GroupType
        futoptorditem.DiscloseQty = ordargs.DiscloseQty
        futoptorditem.Variance = ordargs.Variance
        futoptorditem.Interval = ordargs.Interval
        futoptorditem.LeftoverAction = ordargs.LeftoverAction
        futoptorditem.Threshold = ordargs.Threshold
        futoptorditem.Consecutive = ordargs.Consecutive
        futoptorditem.NumberOfRetries = ordargs.NumberOfRetries
        futoptorditem.StrikePrice = int("{:.0f}".format(ordargs.StrikePrice * 10000000000))
        futoptorditem.StrikePrice2 == int("{:.0f}".format(ordargs.StrikePrice2 * 10000000000))
        ordresult = self._neworder(9, futoptorditem)
        if ordresult >= 1:
            # print("委托单产生成功")
            return ordid, "委托成功"
        else:
            errmsg = ""
            if str(ordresult) in self.ordererr.keys():
                errmsg = self.ordererr[str(ordresult)]
                print(self.ordererr[str(ordresult)])
            else:
                errmsg = str(ordresult)
            return None, errmsg

    def _neworder(self, SecurityType, NewOrderParameters):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                re = self.ptrade.NewOrder2(SecurityType, NewOrderParameters)
                if self.debuglevel and re <= 0:
                    self.writelog(
                        "python NewOrder2:{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}".format(
                            NewOrderParameters.Account,
                            NewOrderParameters.BrokerID,
                            NewOrderParameters.Symbol,
                            NewOrderParameters.Side,
                            NewOrderParameters.OrderQty,
                            NewOrderParameters.OrderType,
                            NewOrderParameters.TimeInForce,
                            NewOrderParameters.PositionEffect,
                            NewOrderParameters.Price,
                            NewOrderParameters.StopPrice,
                            re
                        )
                    )
                return re
            except COMError as e:
                print("neworder错误:", e)

    def newstrategyorder(self, strategyorder: dict):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                strategyorder["UserKey3"] = "8076c9867a372d2a9a814ae710c256e2|Python"
                strategyorder["ProcessID"] = os.getpid()
                args = str(strategyorder)
                return self.ptrade.NewStrategyOrder(args.replace("'", '"'))
            except COMError as e:
                print("newstrategyorder错误:", e)

    def replaceorder(self, reportid, orderqty, price, stopprice):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                clsid = self.mod.NOPReplaceOrder._reg_clsid_
                ReplaceOrderParametersfac = self.mod.nopReplaceOrderItem
                ReplaceOrderParameters = self.createDispatch(clsid, ReplaceOrderParametersfac)

                ReplaceOrderParameters.ReportID = reportid
                if orderqty and not price and not stopprice:
                    ReplaceOrderParameters.OrderQty = orderqty
                    ReplaceOrderParameters.ReplaceExecType = 1
                if not orderqty and (price or stopprice):
                    ReplaceOrderParameters.ReplaceExecType = 0
                if orderqty and (price or stopprice):
                    ReplaceOrderParameters.OrderQty = orderqty
                    ReplaceOrderParameters.ReplaceExecType = 2
                if price:
                    ReplaceOrderParameters.Price = int("{:.0f}".format(price * 10000000000))
                if stopprice:
                    ReplaceOrderParameters.StopPrice = int("{:.0f}".format(stopprice * 10000000000))
                    re = self.ptrade.ReplaceOrder(ReplaceOrderParameters)
                    if self.debuglevel and re <= 0:
                        self.writelog(
                            "python replaceorder,OrderQty:{0},Price:{1},StopPrice:{2},{3}".format(ReplaceOrderParameters.OrderQty, ReplaceOrderParameters.Price, ReplaceOrderParameters.StopPrice, re)
                        )
                return re
            except COMError as e:
                print("replaceorder错误:", e)
    
    #'NewSpreadOrder'
    def newspreadorder(self, orderstring: SpreadOrderStruct)-> str:
        try:
            orderstr=json.dumps(asdict(orderstring))
            re=self.ptrade.NewSpreadOrder(orderstr)
            self.writelog("python newspreadorder:"+orderstr)
            return re
        except COMError as e:
            print("getspreadposition错误:", e)

    #'CancelSpreadOrder
    def cancelspreadorder(self, bstrReportID):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                self.writelog("python cancelspreadorder:"+bstrReportID)
                return self.ptrade.CancelSpreadOrder("GRP-"+bstrReportID)
            except COMError as e:
                print("CancelOrder错误:", e)

    #'GetSpreadPosition'
    def getspreadposition(self, symbol):
        try:
            clsid = self.mod.ADISpreadPosition._reg_clsid_
            positemfac = self.mod.IADISpreadPosition
            positem = self.createDispatch(clsid, positemfac)
            if self.ptrade.GetSpreadPosition(symbol, positem) == 1:
                for i in range(positem.GetCount()):
                    print(positem.GetDataStr(0,0),positem.GetDataVal(0,0))
                return {}
        except COMError as e:
                print("getspreadposition错误:", e)

    def setaccountsubscriptionlevel(self, Level):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.SetAccountSubscriptionLevel(Level)
            except COMError as e:
                print("setaccountsubscriptionlevel错误:", e)

    def topicpublish(self, strTopic, lParam, strParam, pvParam):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.TopicPublish(strTopic, lParam, strParam, pvParam)
            except COMError as e:
                print("topicpublish错误:", e)

    def topicsub(self, strTopic):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.TopicSub(strTopic)
            except COMError as e:
                print("topicsub错误:", e)

    def topicunsub(self, strTopic):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.TopicUnsub(strTopic)
            except COMError as e:
                print("topicunsub错误:", e)

    def getgeneralservice(self, Key):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.GetGeneralService(Key)
            except COMError as e:
                print("getgeneralservice错误:", e)

    def writelog(self, strlog):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.ptrade.DoSomething(1, 0, strlog, None)
            except COMError as e:
                print("writelog:", e)

    def join(self):
        run()

    def optcombcheck(self, strAcctMask, SymbolA, SymbolB, Volume: int, CombinationType: int, CombID=""):
        symb1 = SymbolA.split(".")
        symb2 = SymbolB.split(".")
        strick1 = SymbolA.replace(symb1[0] + "." + symb1[1] + "." + symb1[2] + "." + symb1[3] + "." + symb1[4] + "." + symb1[5] + ".", "")
        strick2 = SymbolB.replace(symb2[0] + "." + symb2[1] + "." + symb2[2] + "." + symb2[3] + "." + symb2[4] + "." + symb2[5] + ".", "")
        # 认购牛市价差（DCE:BLS OTHER:BUL）
        if CombinationType == 1:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "C" and symb2[5] != "C":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) > float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
        # 认沽熊市价差（DCE:BLS OTHER:BER）
        if CombinationType == 2:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "P" and symb2[5] != "P":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) < float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
        # 认沽牛市价差（DCE:BES OTHER:BUL）
        if CombinationType == 3:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "P" and symb2[5] != "P":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) < float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
        # 认沽牛市价差（DCE:BES OTHER:BUL）
        if CombinationType == 4:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "P" and symb2[5] != "P":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) < float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
        # 认沽牛市价差（DCE:BES OTHER:BUL）
        if CombinationType == 5:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "P" and symb2[5] != "P":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) < float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
        # 认沽牛市价差（DCE:BES OTHER:BUL）
        if CombinationType == 6:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "P" and symb2[5] != "P":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) < float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
        # 认沽牛市价差（DCE:BES OTHER:BUL）
        if CombinationType == 3:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "P" and symb2[5] != "P":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) < float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
        # 认沽牛市价差（DCE:BES OTHER:BUL）
        if CombinationType == 3:
            if not symb1[0] == symb2[0] and symb1[1] == symb2[1] and symb1[2] == symb2[2] and symb1[3] == symb2[3] and symb1[4] == symb2[4]:
                print("组合发送失败，组合合约必须是期权同月份合约")
                return
            if symb1[5] != "P" and symb2[5] != "P":
                print("组合发送失败，组合合约必须是期权认购合约")
                return
            if float(strick1) < float(strick2):
                print("组合发送失败，合约A行权价必须低于合约B行权价")
                return
