import os
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import time
import pytz
from icetcore.constant import BarType
import math
from comtypes.messageloop import run
from comtypes.client import GetModule, dynamic, CreateObject,GetEvents
from comtypes import CoInitializeEx, COINIT_MULTITHREADED, GUID, CoUninitialize, COMError, automation
from comtypes.server import IClassFactory
from ctypes import windll, oledll, POINTER, byref
import json
import copy
from decimal import Decimal
import platform
import threading
def iff(itemvalue, tcsize=1):
    if itemvalue != -9223372036854775808:
        return itemvalue / tcsize
    else:
        return None


def wrap_outparam(punk):
    if not punk:
        return None
    return punk


class QuoteEventMeta(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._tcoreapi = None

    @abstractmethod
    def onconnected(self, apitype: str):
        pass

    @abstractmethod
    def ondisconnected(self, apitype: str):
        pass

    @abstractmethod
    def onsystemmessage(self, MsgType, MsgCode, MsgString):
        pass

    @abstractmethod
    def onATM(self, datatype, symbol, data: dict):
        pass

    @abstractmethod
    def ongreeksline(datatype, interval, symbol, data, isreal):
        pass

    @abstractmethod
    def ongreeksreal(self, datatype, symbol, data: dict):
        pass

    @abstractmethod
    def onquote(self, data):
        pass

    @abstractmethod
    def onbar(self, datatype, interval, symbol, data: list, isreal: bool):
        pass

    @abstractmethod
    def onservertime(self, serverdt):
        pass


class BaseEvents:
    def __init__(self):
        self.tz = pytz.timezone("Etc/GMT+8")
        self.quoteapi = None
        self.extendevent = None
        self.update_asinterval = {}
        self.barinterval = {}
        self.bardata = {}
        self.bardatatopic = []
        self.lineinterval = {}
        self.linedata = {}
        self.greekslinetopic = []
        self.linetemp = {}
        self.underlyingprice = {}

        self.win32event = windll.kernel32
        self.subquotetopic = set()
        self.temp = {}
        self.voltemp = 0
        self.cmsgevent = self.win32event.CreateEventW(None, 0, 0, None)
        self.symbolhistoryevent = self.win32event.CreateEventW(None, 0, 0, None)
        self.symbolhistory = {}
        self.quotehistoryevent = self.win32event.CreateEventW(None, 0, 0, None)
        self.quotehistory = {}
        self.greekshistoryevent = self.win32event.CreateEventW(None, 0, 0, None)
        self.greekshistory = {}
        self.atmevent = self.win32event.CreateEventW(None, 0, 0, None)
        self.atm = {}
        self.symbollistready = False
        self.hotmonthready = False
        self.symblookready = False
        self.symbinfoready = False
        self.greeksputcallvol = {}

        self.quotestatus=True
        self.dcorestatus=True

        self.voloievent=threading.Event()
    # @abstractmethod
    def onconnected(self, strapi):
        if self.extendevent:
            self.extendevent.onconnected(strapi)

    # @abstractmethod
    def ondisconnected(self, strapi):
        if self.extendevent:
            self.extendevent.ondisconnected(strapi)

    def onsystemmessage(self, MsgType, MsgCode, MsgString):
        if self.extendevent:
            self.extendevent.onsystemmessage(MsgType, MsgCode, MsgString)

    # @abstractmethod
    def onquote(self, data):
        if self.extendevent:
            self.extendevent.onquote(data)

    # @abstractmethod
    def onbar(self, datatype, interval, symbol, data: list, isreal: bool):
        if self.extendevent:
            self.extendevent.onbar(datatype, interval, symbol, data, isreal)

    # @abstractmethod
    def onATM(self, datatype, symbol, data: dict):
        if self.extendevent:
            self.extendevent.onATM(datatype, symbol, data)
        if symbol in self.atm.keys():
            self.atm[symbol] = data
            self.win32event.SetEvent(self.atmevent)

    # @abstractmethod
    def ongreeksline(self, datatype, interval, symbol, data: list, isreal: bool):
        if self.extendevent:
            self.extendevent.ongreeksline(datatype, interval, symbol, data, isreal)

    # @abstractmethod
    def onsymbolhistory(self, symboltype, symboldate, sym):
        self.symbolhistory[symboltype + "-" + str(symboldate)] = sym
        self.win32event.SetEvent(self.symbolhistoryevent)
        # self.extendevent.onsymbolhistory(symboltype,symboldate,sym)

    # @abstractmethod
    def ontimediff(self, TimeDiff):
        if self.extendevent:
            self.extendevent.onservertime(datetime.now().replace(tzinfo=self.tz) + timedelta(seconds=TimeDiff))

    def OnCommandMsg(self, MsgType, MsgCode, MsgString):
        if int(MsgType) == 2 and int(MsgCode) == 1:
            self.win32event.SetEvent(self.cmsgevent)
            self.onconnected("quote")
        elif int(MsgType) == 1 and int(MsgCode) == 1:
            self.ondisconnected("quote")
            self.win32event.SetEvent(self.cmsgevent)
            print("登入失败", MsgString)
        elif int(MsgType) == 2 and int(MsgCode) == 0:
            self.ondisconnected("quote")
        else:
            self.onsystemmessage(MsgType, MsgCode, MsgString)

    def dtfilter(self, symbol, dt):
        sess = [i.split("~") for i in self.quoteapi.getsymbol_session(symbol).split(";")]
        for i in sess:
            sessopen = datetime.strptime(str(dt.date()) + i[0], "%Y-%m-%d%H:%M").replace(tzinfo=self.tz) + timedelta(hours=8)
            sessclose = datetime.strptime(str(dt.date()) + i[1], "%Y-%m-%d%H:%M").replace(tzinfo=self.tz) + timedelta(hours=8)
            # dt=datetime.strptime(str(dt.date()) + str(dt.hour)+":"+str(dt.minute) ,'%Y-%m-%d%H:%M').replace(tzinfo=self.tz)
            if "SSE" in symbol or "SZSE" in symbol:
                if (sessopen - timedelta(minutes=15)) <= dt < sessopen:
                    return datetime.strptime(str(dt.date()) + i[0] + ":00", "%Y-%m-%d%H:%M:%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                if sessclose <= dt < (sessclose + timedelta(minutes=1)):
                    return datetime.strptime(str(dt.date()) + i[1] + ":59", "%Y-%m-%d%H:%M:%S").replace(tzinfo=self.tz) + timedelta(hours=8) - timedelta(minutes=1)
            else:
                if (sessopen - timedelta(minutes=1)) <= dt < sessopen:
                    return datetime.strptime(str(dt.date()) + i[0] + ":00", "%Y-%m-%d%H:%M:%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                if (sessopen - timedelta(days=1) - timedelta(minutes=1)) <= dt < sessopen - timedelta(days=1):
                    return datetime.strptime(str(dt.date()) + i[0] + ":00", "%Y-%m-%d%H:%M:%S").replace(tzinfo=self.tz) + timedelta(hours=8) - timedelta(days=1)
                if sessclose <= dt < (sessclose + timedelta(minutes=1)):
                    return datetime.strptime(str(dt.date()) + i[1] + ":59", "%Y-%m-%d%H:%M:%S").replace(tzinfo=self.tz) + timedelta(hours=8) - timedelta(minutes=1)
                if sessclose - timedelta(days=1) <= dt < (sessclose - timedelta(days=1) + timedelta(minutes=1)):
                    return datetime.strptime(str(dt.date()) + i[1] + ":59", "%Y-%m-%d%H:%M:%S").replace(tzinfo=self.tz) + timedelta(hours=8) - timedelta(minutes=1) - timedelta(days=1)
        return dt

    def isduringdt(self, symbol, dt):
        if ("CFFEX.I" in symbol and dt < datetime.strptime("2016-1-2 01:00", "%Y-%m-%d %H:%M").replace(tzinfo=self.tz) + timedelta(hours=8)) or (
            "CFFEX.T" in symbol and dt < datetime.strptime("2020-7-19 01:00", "%Y-%m-%d %H:%M").replace(tzinfo=self.tz) + timedelta(hours=8)
        ):
            sess = [["01:15", "3:30"], ["5:00", "7:15"]]
        else:
            sess = [i.split("~") for i in self.quoteapi.getsymbol_session(symbol).split(";")]
        sess2=[]    
        for i in sess:
            start_time = datetime.strptime(str(dt.date()) + i[0], "%Y-%m-%d%H:%M").replace(tzinfo=self.tz) + timedelta(hours=8)
            end_time = datetime.strptime(str(dt.date()) + i[1], "%Y-%m-%d%H:%M").replace(tzinfo=self.tz) + timedelta(hours=8)
            dt = datetime.strptime(str(dt.date()) + str(dt.hour) + ":" + str(dt.minute), "%Y-%m-%d%H:%M").replace(tzinfo=self.tz)
            if start_time > end_time:
                start_time = start_time - timedelta(days=1)
            if start_time <= dt <= end_time or start_time - timedelta(days=1) <= dt <= end_time - timedelta(days=1):
                return True, start_time
            sess2.append(start_time)
        sess2.append(dt)
        sess2.sort()
        start_time= sess2[sess2.index(dt)-1]
        return False, start_time


    def _Dispatch(self, punk):
        if not punk:  # NULL COM pointer
            return punk  # or should we return None?
        try:
            pdisp = punk.QueryInterface(automation.IDispatch)
        except COMError:
            return punk
        try:
            tinfo = pdisp.GetTypeInfo(0)
        except COMError:
            pdisp = dynamic.Dispatch(pdisp)
            return pdisp
        itf_name = tinfo.GetDocumentation(-1)[0]  # interface name
        # Python interface class
        interface = getattr(self.quoteapi.mod, itf_name)
        result = punk.QueryInterface(interface)
        return result

    def onbarupdate(self, datatype, interval, symbol, opentime, data: list, isreal: bool):
        if isreal:
            bararr = [i for i in self.bardata.keys() if symbol + "-" in i]
            isbarcout = 0
            for barkey in bararr:
                if self.bardata[barkey] is not None:
                    isbarcout = isbarcout + 1
            if isbarcout == len(bararr):
                for barkey in bararr:
                    bar = self.bardata[barkey]
                    bartypeinte = barkey.split("-")
                    bartype = int(bartypeinte[1])
                    interval = int(bartypeinte[2])
                    if symbol in self.temp.keys():
                        if self.temp[symbol]:
                            for te in self.temp[symbol]:
                                if bartype == BarType.DK:
                                    if len(bar) == 0 or (len(bar) > 0 and te["DateTime"].date() > bar[-1]["DateTime"].date()):
                                        ktemp = {}
                                        ktemp["DateTime"] = datetime.strptime(
                                            str(te["DateTime"].date()) + str(te["DateTime"].hour) + ":" + str(te["DateTime"].minute) + ":00", "%Y-%m-%d%H:%M:%S"
                                        ).replace(tzinfo=self.tz) + timedelta(days=interval - 1)
                                        ktemp["Symbol"] = symbol
                                        ktemp["Open"] = te["Open"]
                                        ktemp["High"] = te["High"]
                                        ktemp["Low"] = te["Low"]
                                        ktemp["Close"] = te["Close"]
                                        ktemp["Volume"] = te["Volume"]
                                        ktemp["OpenInterest"] = te["OpenInterest"]
                                        if len(bar) == 0 or (len(bar) > 0 and te["Close"] < bar[-1]["Close"]):
                                            ktemp["DownTick"] = 1
                                            ktemp["DownVolume"] = te["Quantity"]
                                            ktemp["UnchVolume"] = 0
                                            ktemp["UpTick"] = 0
                                            ktemp["UpVolume"] = 0
                                        else:
                                            ktemp["DownTick"] = 0
                                            ktemp["DownVolume"] = 0
                                            ktemp["UnchVolume"] = 0
                                            ktemp["UpTick"] = 1
                                            ktemp["UpVolume"] = te["Quantity"]
                                        bar.append(ktemp)
                                    else:
                                        if te["Close"] and bar[-1]["Close"]:
                                            if te["Close"] > bar[-1]["Close"]:
                                                bar[-1]["UpTick"] = bar[-1]["UpTick"] + 1
                                                bar[-1]["UpVolume"] = bar[-1]["UpVolume"] + te["Quantity"]
                                            else:
                                                bar[-1]["DownTick"] = bar[-1]["DownTick"] + 1
                                                bar[-1]["DownVolume"] = bar[-1]["DownVolume"] + te["Quantity"]
                                        if te["High"] and bar[-1]["High"]:
                                            if te["High"] > bar[-1]["High"]:
                                                bar[-1]["High"] = te["High"]
                                        if te["Low"] and bar[-1]["Low"]:
                                            if te["Low"] < bar[-1]["Low"]:
                                                bar[-1]["Low"] = te["Low"]
                                        bar[-1]["Close"] = te["Close"]
                                        bar[-1]["Volume"] = te["Volume"]
                                        bar[-1]["OpenInterest"] = te["OpenInterest"]
                                elif bartype == BarType.MINUTE:
                                    if len(bar) == 0 or (len(bar) > 0 and te["DateTime"] > bar[-1]["DateTime"]):
                                        ktemp = {}
                                        ktemp["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / (interval * 60)) * interval * 60)
                                        ktemp["Symbol"] = symbol
                                        ktemp["Open"] = te["Close"]
                                        ktemp["High"] = te["Close"]
                                        ktemp["Low"] = te["Close"]
                                        ktemp["Close"] = te["Close"]
                                        ktemp["Volume"] = te["Quantity"]
                                        ktemp["OpenInterest"] = te["OpenInterest"]
                                        if len(bar) == 0 or (len(bar) > 0 and te["Close"] < bar[-1]["Close"]):
                                            ktemp["DownTick"] = 1
                                            ktemp["DownVolume"] = te["Quantity"]
                                            ktemp["UnchVolume"] = 0
                                            ktemp["UpTick"] = 0
                                            ktemp["UpVolume"] = 0
                                        else:
                                            ktemp["DownTick"] = 0
                                            ktemp["DownVolume"] = 0
                                            ktemp["UnchVolume"] = 0
                                            ktemp["UpTick"] = 1
                                            ktemp["UpVolume"] = te["Quantity"]
                                        bar.append(ktemp)
                                    else:
                                        if te["Close"] and bar[-1]["Close"]:
                                            if te["Close"] > bar[-1]["Close"]:
                                                bar[-1]["UpTick"] = bar[-1]["UpTick"] + 1
                                                bar[-1]["UpVolume"] = bar[-1]["UpVolume"] + te["Quantity"]
                                            else:
                                                bar[-1]["DownTick"] = bar[-1]["DownTick"] + 1
                                                bar[-1]["DownVolume"] = bar[-1]["DownVolume"] + te["Quantity"]
                                        if te["Close"] and bar[-1]["High"]:
                                            if te["Close"] > bar[-1]["High"]:
                                                bar[-1]["High"] = te["Close"]
                                        if te["Close"] and bar[-1]["Low"]:
                                            if te["Close"] < bar[-1]["Low"]:
                                                bar[-1]["Low"] = te["Close"]
                                        bar[-1]["Close"] = te["Close"]
                                        bar[-1]["Volume"] = bar[-1]["Volume"] + te["Quantity"]
                                        bar[-1]["OpenInterest"] = te["OpenInterest"]
                                elif bartype == BarType.TICK:
                                    if interval == 1:
                                        if len(bar) == 0 or (len(bar) > 0 and te["DateTime"] >= bar[-1]["DateTime"] and te["Volume"] > bar[-1]["Volume"]):
                                            bar.append(
                                                {
                                                    "DateTime": te["DateTime"],
                                                    "Symbol": symbol,
                                                    "Ask": te["Ask"],
                                                    "Bid": te["Bid"],
                                                    "Last": te["Close"],
                                                    "Quantity": te["Quantity"],
                                                    "Volume": te["Volume"],
                                                    "OpenInterest": te["OpenInterest"],
                                                }
                                            )
                                    else:
                                        if len(bar) == 0 or (len(bar) > 0 and te["DateTime"] > bar[-1]["DateTime"]):
                                            ktemp = {}
                                            ktemp["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / interval) * interval)
                                            ktemp["Symbol"] = symbol
                                            ktemp["Open"] = te["Close"]
                                            ktemp["High"] = te["Close"]
                                            ktemp["Low"] = te["Close"]
                                            ktemp["Close"] = te["Close"]
                                            ktemp["Volume"] = te["Quantity"]
                                            ktemp["OpenInterest"] = te["OpenInterest"]
                                            if len(bar) == 0 or (len(bar) > 0 and te["Close"] < bar[-1]["Close"]):
                                                ktemp["DownTick"] = 1
                                                ktemp["DownVolume"] = te["Quantity"]
                                                ktemp["UnchVolume"] = 0
                                                ktemp["UpTick"] = 0
                                                ktemp["UpVolume"] = 0
                                            else:
                                                ktemp["DownTick"] = 0
                                                ktemp["DownVolume"] = 0
                                                ktemp["UnchVolume"] = 0
                                                ktemp["UpTick"] = 1
                                                ktemp["UpVolume"] = te["Quantity"]
                                            bar.append(ktemp)
                                        else:
                                            if te["Close"] and bar[-1]["Close"]:
                                                if te["Close"] > bar[-1]["Close"]:
                                                    bar[-1]["UpTick"] = bar[-1]["UpTick"] + 1
                                                    bar[-1]["UpVolume"] = bar[-1]["UpVolume"] + te["Quantity"]
                                                else:
                                                    bar[-1]["DownTick"] = bar[-1]["DownTick"] + 1
                                                    bar[-1]["DownVolume"] = bar[-1]["DownVolume"] + te["Quantity"]
                                            if te["Close"] and bar[-1]["High"]:
                                                if te["Close"] > bar[-1]["High"]:
                                                    bar[-1]["High"] = te["Close"]
                                            if te["Close"] and bar[-1]["Low"]:
                                                if te["Close"] < bar[-1]["Low"]:
                                                    bar[-1]["Low"] = te["Close"]
                                            bar[-1]["Close"] = te["Close"]
                                            bar[-1]["Volume"] = bar[-1]["Volume"] + te["Quantity"]
                                            bar[-1]["OpenInterest"] = te["OpenInterest"]
                            del self.temp[symbol]
                    else:
                        te = data[0]
                        if bartype == BarType.DK:
                            if len(bar) == 0 or (len(bar) > 0 and te["DateTime"].date() > bar[-1]["DateTime"].date()):
                                if self.update_asinterval[symbol + "-" + str(bartype) + "-" + str(interval)]:
                                    self.onbar(bartype, interval, symbol, bar, True)
                                ktemp = {}
                                ktemp["DateTime"] = datetime.strptime(str(te["DateTime"].date()) + str(te["DateTime"].hour) + ":" + str(te["DateTime"].minute) + ":00", "%Y-%m-%d%H:%M:%S").replace(
                                    tzinfo=self.tz
                                ) + timedelta(days=interval - 1)
                                ktemp["Symbol"] = symbol
                                ktemp["Open"] = te["Open"]
                                ktemp["High"] = te["High"]
                                ktemp["Low"] = te["Low"]
                                ktemp["Close"] = te["Close"]
                                ktemp["Volume"] = te["Volume"]
                                ktemp["OpenInterest"] = te["OpenInterest"]
                                if len(bar) == 0 or (len(bar) > 0 and te["Close"] < bar[-1]["Close"]):
                                    ktemp["DownTick"] = 1
                                    ktemp["DownVolume"] = te["Quantity"]
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 0
                                    ktemp["UpVolume"] = 0
                                else:
                                    ktemp["DownTick"] = 0
                                    ktemp["DownVolume"] = 0
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 1
                                    ktemp["UpVolume"] = te["Quantity"]
                                bar.append(ktemp)
                            else:
                                if te["Close"] and bar[-1]["Close"]:
                                    if te["Close"] > bar[-1]["Close"]:
                                        bar[-1]["UpTick"] = bar[-1]["UpTick"] + 1
                                        bar[-1]["UpVolume"] = bar[-1]["UpVolume"] + te["Quantity"]
                                    else:
                                        bar[-1]["DownTick"] = bar[-1]["DownTick"] + 1
                                        bar[-1]["DownVolume"] = bar[-1]["DownVolume"] + te["Quantity"]
                                if te["High"] and bar[-1]["High"]:
                                    if te["High"] > bar[-1]["High"]:
                                        bar[-1]["High"] = te["High"]
                                if te["Low"] and bar[-1]["Low"]:
                                    if te["Low"] < bar[-1]["Low"]:
                                        bar[-1]["Low"] = te["Low"]
                                bar[-1]["Close"] = te["Close"]
                                bar[-1]["Volume"] = bar[-1]["Volume"] + te["Quantity"]
                                bar[-1]["OpenInterest"] = te["OpenInterest"]

                        elif bartype == BarType.MINUTE:
                            if len(bar) == 0 or (len(bar) > 0 and te["DateTime"] > bar[-1]["DateTime"]):
                                if self.update_asinterval[symbol + "-" + str(bartype) + "-" + str(interval)]:
                                    self.onbar(bartype, interval, symbol, bar, True)
                                ktemp = {}
                                ktemp["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / (interval * 60)) * interval * 60)
                                ktemp["Symbol"] = symbol
                                ktemp["Open"] = te["Close"]
                                ktemp["High"] = te["Close"]
                                ktemp["Low"] = te["Close"]
                                ktemp["Close"] = te["Close"]
                                ktemp["Volume"] = te["Quantity"]
                                ktemp["OpenInterest"] = te["OpenInterest"]
                                if len(bar) == 0 or (len(bar) > 0 and te["Close"] < bar[-1]["Close"]):
                                    ktemp["DownTick"] = 1
                                    ktemp["DownVolume"] = te["Quantity"]
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 0
                                    ktemp["UpVolume"] = 0
                                else:
                                    ktemp["DownTick"] = 0
                                    ktemp["DownVolume"] = 0
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 1
                                    ktemp["UpVolume"] = te["Quantity"]
                                bar.append(ktemp)
                            else:
                                if te["Close"] and bar[-1]["Close"]:
                                    if te["Close"] > bar[-1]["Close"]:
                                        bar[-1]["UpTick"] = bar[-1]["UpTick"] + 1
                                        bar[-1]["UpVolume"] = bar[-1]["UpVolume"] + te["Quantity"]
                                    else:
                                        bar[-1]["DownTick"] = bar[-1]["DownTick"] + 1
                                        bar[-1]["DownVolume"] = bar[-1]["DownVolume"] + te["Quantity"]
                                if te["Close"] and bar[-1]["High"]:
                                    if te["Close"] > bar[-1]["High"]:
                                        bar[-1]["High"] = te["Close"]
                                if te["Close"] and bar[-1]["Low"]:
                                    if te["Close"] < bar[-1]["Low"]:
                                        bar[-1]["Low"] = te["Close"]
                                bar[-1]["Close"] = te["Close"]
                                bar[-1]["Volume"] = bar[-1]["Volume"] + te["Quantity"]
                                bar[-1]["OpenInterest"] = te["OpenInterest"]

                        elif bartype == BarType.TICK:
                            if interval == 1:
                                if len(bar) == 0 or (len(bar) > 0 and te["DateTime"] >= bar[-1]["DateTime"] or (te["Volume"] > bar[-1]["Volume"] and ".U_" not in symbol and".000000" not in symbol)):
                                    bar.append(
                                        {
                                            "DateTime": te["DateTime"],
                                            "Symbol": symbol,
                                            "Ask": te["Ask"],
                                            "Bid": te["Bid"],
                                            "Last": te["Close"],
                                            "Quantity": te["Quantity"],
                                            "Volume": te["Volume"],
                                            "OpenInterest": te["OpenInterest"],
                                        }
                                    )
                                    if self.update_asinterval[symbol + "-" + str(bartype) + "-" + str(interval)]:
                                        self.onbar(bartype, interval, symbol, bar, True)
                            else:
                                if len(bar) == 0 or (len(bar) > 0 and te["DateTime"] > bar[-1]["DateTime"]):
                                    if self.update_asinterval[symbol + "-" + str(bartype) + "-" + str(interval)]:
                                        self.onbar(bartype, interval, symbol, bar, True)
                                    ktemp = {}
                                    ktemp["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / interval) * interval)
                                    ktemp["Symbol"] = symbol
                                    ktemp["Open"] = te["Close"]
                                    ktemp["High"] = te["Close"]
                                    ktemp["Low"] = te["Close"]
                                    ktemp["Close"] = te["Close"]
                                    ktemp["Volume"] = te["Quantity"]
                                    ktemp["OpenInterest"] = te["OpenInterest"]
                                    if len(bar) == 0 or (len(bar) > 0 and te["Close"] < bar[-1]["Close"]):
                                        ktemp["DownTick"] = 1
                                        ktemp["DownVolume"] = te["Quantity"]
                                        ktemp["UnchVolume"] = 0
                                        ktemp["UpTick"] = 0
                                        ktemp["UpVolume"] = 0
                                    else:
                                        ktemp["DownTick"] = 0
                                        ktemp["DownVolume"] = 0
                                        ktemp["UnchVolume"] = 0
                                        ktemp["UpTick"] = 1
                                        ktemp["UpVolume"] = te["Quantity"]
                                    bar.append(ktemp)
                                else:
                                    if te["Close"] and bar[-1]["Close"]:
                                        if te["Close"] > bar[-1]["Close"]:
                                            bar[-1]["UpTick"] = bar[-1]["UpTick"] + 1
                                            bar[-1]["UpVolume"] = bar[-1]["UpVolume"] + te["Quantity"]
                                        else:
                                            bar[-1]["DownTick"] = bar[-1]["DownTick"] + 1
                                            bar[-1]["DownVolume"] = bar[-1]["DownVolume"] + te["Quantity"]
                                    if te["Close"] and bar[-1]["High"]:
                                        if te["Close"] > bar[-1]["High"]:
                                            bar[-1]["High"] = te["Close"]
                                    if te["Close"] and bar[-1]["Low"]:
                                        if te["Close"] < bar[-1]["Low"]:
                                            bar[-1]["Low"] = te["Close"]
                                    bar[-1]["Close"] = te["Close"]
                                    bar[-1]["Volume"] = bar[-1]["Volume"] + te["Quantity"]
                                    bar[-1]["OpenInterest"] = te["OpenInterest"]

                        if not self.update_asinterval[symbol + "-" + str(bartype) + "-" + str(interval)]:
                            self.onbar(bartype, interval, symbol, bar, True)
            else:
                if symbol in self.temp.keys():
                    self.temp[symbol].append(data[0])
                else:
                    self.temp[symbol] = data
        else:
            self.bardata[symbol + "-" + str(datatype) + "-" + str(interval)] = copy.deepcopy(data)
            self.onbar(datatype, interval, symbol, data, False)

    def onquotehistory(self, datatype, symbol, starttime, endtime, data: list):
        for interval in self.barinterval[symbol + "-" + str(datatype)]:
            if len(data) == 0:
                if symbol + "-" + str(datatype) + "-" + str(interval) in self.bardata.keys():
                    self.onbarupdate(datatype, interval, symbol, None, data, False)
                if symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime) in self.quotehistory.keys():
                    self.quotehistory[symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime)] = data
                    self.win32event.SetEvent(self.quotehistoryevent)
                return
            if interval == 1:
                if symbol + "-" + str(datatype) + "-" + str(interval) in self.bardata.keys():
                    self.onbarupdate(datatype, interval, symbol, None, data, False)
                if symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime) in self.quotehistory.keys():
                    self.quotehistory[symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime)] = data
                    self.win32event.SetEvent(self.quotehistoryevent)
            else:
                datatemp = []
                # if symbol+"-"+str(datatype)+"-"+str(interval) in self.bardata.keys() or symbol+"-"+str(datatype)+str(interval)+":"+str(starttime)+"~"+str(endtime) in self.quotehistory.keys():
                for basedata in data:
                    basedata["DateTime"] = self.dtfilter(symbol, basedata["DateTime"])
                    if datatemp:
                        if basedata["DateTime"] <= datatemp[-1]["DateTime"]:
                            if datatype == 2:
                                if basedata["Last"] > datatemp[-1]["Close"]:
                                    datatemp[-1]["UpTick"] = datatemp[-1]["UpTick"] + 1
                                    datatemp[-1]["UpVolume"] = datatemp[-1]["UpVolume"] + basedata["Quantity"]
                                else:
                                    datatemp[-1]["DownTick"] = datatemp[-1]["DownTick"] + 1
                                    datatemp[-1]["DownVolume"] = datatemp[-1]["DownVolume"] + basedata["Quantity"]
                                if basedata["Last"] > datatemp[-1]["High"]:
                                    datatemp[-1]["High"] = basedata["Last"]
                                if basedata["Last"] < datatemp[-1]["Low"]:
                                    datatemp[-1]["Low"] = basedata["Last"]
                                datatemp[-1]["Close"] = basedata["Last"]
                                datatemp[-1]["Volume"] = datatemp[-1]["Volume"] + basedata["Quantity"]
                                datatemp[-1]["OpenInterest"] = basedata["OpenInterest"]
                            else:
                                if basedata["Close"] > datatemp[-1]["Close"]:
                                    datatemp[-1]["UpTick"] = datatemp[-1]["UpTick"] + 1
                                    datatemp[-1]["UpVolume"] = datatemp[-1]["UpVolume"] + basedata["Volume"]
                                else:
                                    datatemp[-1]["DownTick"] = datatemp[-1]["DownTick"] + 1
                                    datatemp[-1]["DownVolume"] = datatemp[-1]["DownVolume"] + basedata["Volume"]
                                if basedata["Close"] > datatemp[-1]["High"]:
                                    datatemp[-1]["High"] = basedata["Close"]
                                if basedata["Close"] < datatemp[-1]["Low"]:
                                    datatemp[-1]["Low"] = basedata["Close"]
                                datatemp[-1]["Close"] = basedata["Close"]
                                datatemp[-1]["Volume"] = datatemp[-1]["Volume"] + basedata["Volume"]
                                datatemp[-1]["OpenInterest"] = basedata["OpenInterest"]
                        else:
                            ktemp = {}
                            if datatype == 2:
                                isduring, start = self.isduringdt(symbol, basedata["DateTime"])
                                # if isduring:
                                ktemp["DateTime"] = start + timedelta(seconds=math.ceil((basedata["DateTime"] - start).total_seconds() / interval) * interval)
                                # ktemp["DateTime"]=basedata["DateTime"]+timedelta(seconds=interval-1)
                                ktemp["Symbol"] = symbol
                                ktemp["Open"] = basedata["Last"]
                                ktemp["High"] = basedata["Last"]
                                ktemp["Low"] = basedata["Last"]
                                ktemp["Close"] = basedata["Last"]
                                ktemp["Volume"] = basedata["Quantity"]
                                ktemp["OpenInterest"] = basedata["OpenInterest"]
                                if basedata["Last"] > datatemp[-1]["Close"]:
                                    ktemp["DownTick"] = 0
                                    ktemp["DownVolume"] = 0
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 1
                                    ktemp["UpVolume"] = basedata["Quantity"]
                                else:
                                    ktemp["DownTick"] = 1
                                    ktemp["DownVolume"] = basedata["Quantity"]
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 0
                                    ktemp["UpVolume"] = 0
                            else:
                                if datatype == 4:
                                    isduring, start = self.isduringdt(symbol, basedata["DateTime"])
                                    # if isduring:
                                    ktemp["DateTime"] = start + timedelta(seconds=math.ceil((basedata["DateTime"] - start).total_seconds() / (interval * 60)) * interval * 60)
                                if datatype == 5:
                                    ktemp["DateTime"] = datetime.strptime(
                                        str(basedata["DateTime"].date()) + str(basedata["DateTime"].hour) + ":" + str(basedata["DateTime"].minute) + ":00", "%Y-%m-%d%H:%M:%S"
                                    ).replace(tzinfo=self.tz) + timedelta(days=interval - 1)
                                ktemp["Symbol"] = symbol
                                ktemp["Open"] = basedata["Open"]
                                ktemp["High"] = basedata["High"]
                                ktemp["Low"] = basedata["Low"]
                                ktemp["Close"] = basedata["Close"]
                                ktemp["Volume"] = basedata["Volume"]
                                ktemp["OpenInterest"] = basedata["OpenInterest"]
                                if basedata["Close"] > datatemp[-1]["Close"]:
                                    ktemp["DownTick"] = 0
                                    ktemp["DownVolume"] = 0
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 1
                                    ktemp["UpVolume"] = basedata["Volume"]
                                else:
                                    ktemp["DownTick"] = 1
                                    ktemp["DownVolume"] = basedata["Volume"]
                                    ktemp["UnchVolume"] = 0
                                    ktemp["UpTick"] = 0
                                    ktemp["UpVolume"] = 0
                            datatemp.append(ktemp)
                    else:
                        if datatype == 2:
                            isduring, start = self.isduringdt(symbol, basedata["DateTime"])
                            # if isduring:
                            basedata["DateTime"] = start + timedelta(seconds=math.ceil((basedata["DateTime"] - start).total_seconds() / interval) * interval)
                            # basedata['DateTime']+timedelta(seconds=interval)
                            basedata["Symbol"] = basedata["Symbol"]
                            basedata["Open"] = basedata["Last"]
                            basedata["High"] = basedata["Last"]
                            basedata["Low"] = basedata["Last"]
                            basedata["Close"] = basedata["Last"]
                            basedata["Volume"] = basedata["Quantity"]
                            basedata["OpenInterest"] = basedata["OpenInterest"]
                            basedata["DownTick"] = 0
                            basedata["DownVolume"] = 0
                            basedata["UnchVolume"] = 0
                            basedata["UpTick"] = 1
                            basedata["UpVolume"] = basedata["Quantity"]
                            basedata.pop("Ask", None)
                            basedata.pop("Bid", None)
                            basedata.pop("Last", None)
                            basedata.pop("Quantity", None)
                        if datatype == 4:
                            isduring, start = self.isduringdt(symbol, basedata["DateTime"])
                            # if isduring:
                            basedata["DateTime"] = start + timedelta(seconds=math.ceil((basedata["DateTime"] - start).total_seconds() / (interval * 60)) * interval * 60)
                        if datatype == 5:
                            basedata["DateTime"] = basedata["DateTime"] + timedelta(days=interval - 1)
                        datatemp.append(basedata)
                if symbol + "-" + str(datatype) + "-" + str(interval) in self.bardata.keys():
                    self.onbarupdate(datatype, interval, symbol, None, datatemp, False)
                if symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime) in self.quotehistory.keys():
                    self.quotehistory[symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime)] = datatemp
                    self.win32event.SetEvent(self.quotehistoryevent)
                del datatemp

    def onquotereal(self, datatype, symbol, data: dict):
        q = 0
        if data["Quantity"] == 0:
            if self.voltemp > 0:
                q = data["Volume"] - self.voltemp
        else:
            q = data["Quantity"]
        data["Quantity"] = q
        self.onquote(data)
        self.voltemp = data["Volume"]
        isduring, start = self.isduringdt(symbol, data["DateTime"])
        if isduring and symbol in self.bardatatopic and data["Last"]:
            realbar = {
                "DateTime": self.dtfilter(symbol, data["DateTime"]),
                "Symbol": data["Symbol"],
                "Ask": data["Ask"],
                "Bid": data["Bid"],
                "Open": data["Open"],
                "High": data["High"],
                "Low": data["Low"],
                "Close": data["Last"],
                "Quantity": q,  # data["Quantity"]
                "Volume": data["Volume"],
            }
            if "TC.F" in symbol or "TC.O" in symbol:
                realbar["OpenInterest"] = data["OpenInterest"]
            else:
                realbar["OpenInterest"] = 0
            self.onbarupdate(datatype, None, symbol, start, [realbar], True)
        # arrsymb=symbol.split(".")
        if isduring:  # and arrsymb[3] in str(self.linedata):
            self.underlyingprice[symbol] = data

    def ongreeklineupdate(self, datatype, interval, symbol, opentime, data: list, isreal: bool):
        if isreal:
            linearr = [i for i in self.linedata.keys() if symbol + "-" in i]
            islinecout = 0
            for linekey in linearr:
                if self.linedata[linekey] is not None:
                    islinecout = islinecout + 1
            if islinecout == len(linearr):
                for linekey in linearr:
                    line = self.linedata[linekey]
                    linetypeinte = linekey.split("-")
                    linetype = int(linetypeinte[1])
                    interval = int(linetypeinte[2])
                    if symbol in self.linetemp.keys():
                        if self.linetemp[symbol]:
                            for te in self.linetemp[symbol]:
                                if len(line) > 0 and te["DateTime"] <= line[-1]["DateTime"]:
                                    for key, _ in line[-1].items():
                                        if key != "DateTime":
                                            line[-1][key] = te[key]
                                else:
                                    temp = {}
                                    if linetype == 9 or linetype == 820:
                                        te["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / (interval * 60)) * interval * 60)
                                    if linetype == 10 or linetype == 800:
                                        te["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / interval) * interval)
                                    if linetype == 19:
                                        if (len(line) > 0 and (te["DateTime"] - line[-1]["DateTime"]).days > interval) or len(line) == 0:
                                            te["DateTime"] = te["DateTime"] + timedelta(days=interval - 1)
                                        else:
                                            te["DateTime"] = line[-1]["DateTime"] + timedelta(days=interval)
                                    itemkeys = []
                                    if "TC.O" in symbol and ".mix" not in symbol:
                                        if linetype == 800 or linetype == 820:
                                            itemkeys = [
                                                "DateTime",
                                                "Symbol",
                                                "AnnualTradeday",
                                                "TheoVal",
                                                "IntVal",
                                                "ATV",
                                                "ExtVal",
                                                "TV",
                                                "IV",
                                                "MIV",
                                                "CPIV",
                                                "AIV",
                                                "BIV",
                                                "Delta",
                                                "Gamma",
                                                "Vega",
                                                "Theta",
                                                "Rho",
                                                "LR",
                                                "RealLR",
                                                "OPR",
                                                "ROI",
                                                "BER",
                                                "Charm",
                                                "Vanna",
                                                "Vomma",
                                                "Speed",
                                                "Zomma",
                                                "Last",
                                                "UnderlyingPrice",
                                                "Volume",
                                                "OI",
                                                "Bid",
                                                "Bid1",
                                                "Bid2",
                                                "Bid3",
                                                "Bid4",
                                                "Bid5",
                                                "Bid6",
                                                "Bid7",
                                                "Bid8",
                                                "Bid9",
                                                "BidVolume",
                                                "BidVolume1",
                                                "BidVolume2",
                                                "BidVolume3",
                                                "BidVolume4",
                                                "BidVolume5",
                                                "BidVolume6",
                                                "BidVolume7",
                                                "BidVolume8",
                                                "BidVolume9",
                                                "Bid_UpdateDatetime",
                                                "Bid1_UpdateDatetime",
                                                "Bid2_UpdateDatetime",
                                                "Bid3_UpdateDatetime",
                                                "Bid4_UpdateDatetime",
                                                "Ask",
                                                "Ask1",
                                                "Ask2",
                                                "Ask3",
                                                "Ask4",
                                                "Ask5",
                                                "Ask6",
                                                "Ask7",
                                                "Ask8",
                                                "Ask9",
                                                "AskVolume",
                                                "AskVolume1",
                                                "AskVolume2",
                                                "AskVolume3",
                                                "AskVolume4",
                                                "AskVolume5",
                                                "AskVolume6",
                                                "AskVolume7",
                                                "AskVolume8",
                                                "AskVolume9",
                                                "Ask_UpdateDatetime",
                                                "Ask1_UpdateDatetime",
                                                "Ask2_UpdateDatetime",
                                                "Ask3_UpdateDatetime",
                                                "Ask4_UpdateDatetime",
                                                "us",
                                                "us_datetime",
                                                "us_p",
                                                "us_bp1",
                                                "us_sp1",
                                                "uf",
                                                "uf_datetime",
                                                "uf_p",
                                                "uf_bp1",
                                                "uf_sp1",
                                                "usf",
                                                "usf_datetime",
                                                "usf_p",
                                            ]
                                        if linetype == 9 or linetype == 10 or linetype == 19:
                                            itemkeys = ["DateTime", "Symbol", "Delta", "Gamma", "Rho", "Theta", "Vega","EvaVol", "TV", "ATV", "IV", "CPIV"]
                                    else:
                                        if linetype == 800 or linetype == 820:
                                            if "TC.F" in symbol:
                                                itemkeys = [
                                                    "DateTime",
                                                    "Symbol",
                                                    "AnnualTradeday",
                                                    "ATV",
                                                    "ExtVal",
                                                    "TV",
                                                    "IV",
                                                    "Last",
                                                    "CSkew",
                                                    "PSkew",
                                                    "CIV25D",
                                                    "PIV25D",
                                                    "CIV10D",
                                                    "PIV10D",
                                                    "CallPutOIratio",
                                                    "CallPutVolratio",
                                                    "CallOI",
                                                    "PutOI",
                                                    "CallVol",
                                                    "PutVol",
                                                    "CKUpCnt",
                                                    "CKUpVol",
                                                    "CKDnCnt",
                                                    "CKDnVol",
                                                    "PKUpCnt",
                                                    "PKUpVol",
                                                    "PKDnCnt",
                                                    "PKDnVol",
                                                ]
                                            else:
                                                itemkeys = [
                                                    "DateTime",
                                                    "Symbol",
                                                    "IV",
                                                    "Last",
                                                    "CallPutOIratio",
                                                    "CallPutVolratio",
                                                    "CallOI",
                                                    "PutOI",
                                                    "CallVol",
                                                    "PutVol",
                                                    "CKUpCnt",
                                                    "CKUpVol",
                                                    "CKDnCnt",
                                                    "CKDnVol",
                                                    "PKUpCnt",
                                                    "PKUpVol",
                                                    "PKDnCnt",
                                                    "PKDnVol",
                                                ]
                                        if linetype == 9 or linetype == 10 or linetype == 19:
                                            if "TC.F" in symbol or ".mix" in symbol:
                                                itemkeys = [
                                                    "DateTime",
                                                    "Symbol",
                                                    "IVOut",
                                                    "CTR",
                                                    "PTR",
                                                    "RCTR",
                                                    "RPTR",
                                                    "FCIV25",
                                                    "FPIV25",
                                                    "EvaVol",
                                                    "TV",
                                                    "ATV",
                                                    "HV_W4",
                                                    "HV_W8",
                                                    "HV_W13",
                                                    "HV_W26",
                                                    "HV_W52",
                                                    "PutD",
                                                    "CallD",
                                                    "D25CStraddle",
                                                    "D25PStraddle",
                                                    "D25CTV",
                                                    "D25PTV",
                                                    "FIV",
                                                    "IV",
                                                    "Straddle",
                                                    "StraddleStrike",
                                                    "StraddleWeight",
                                                    "CIV25D",
                                                    "PIV25D",
                                                    "CIV10D",
                                                    "PIV10D",
                                                    "CallOI",
                                                    "PutOI",
                                                    "CallVol",
                                                    "PutVol",
                                                    "CKUpCnt",
                                                    "CKUpVol",
                                                    "CKDnCnt",
                                                    "CKDnVol",
                                                    "PKUpCnt",
                                                    "PKUpVol",
                                                    "PKDnCnt",
                                                    "PKDnVol",
                                                    "CallPutOIratio",
                                                    "CallPutVolratio",
                                                    "CSkew",
                                                    "PSkew",
                                                    "VIX",
                                                ]
                                            else:
                                                itemkeys = [
                                                    "DateTime",
                                                    "Symbol",
                                                    "IV",
                                                    "VIX",
                                                    "CallPutOIratio",
                                                    "CallPutVolratio",
                                                    "CallOI",
                                                    "PutOI",
                                                    "CallVol",
                                                    "PutVol",
                                                    "CKUpCnt",
                                                    "CKUpVol",
                                                    "CKDnCnt",
                                                    "CKDnVol",
                                                    "PKUpCnt",
                                                    "PKUpVol",
                                                    "PKDnCnt",
                                                    "PKDnVol",
                                                ]

                                    for key in itemkeys:
                                        temp[key] = te[key]
                                    line.append(temp)
                        del self.linetemp[symbol]
                    else:
                        te = data[0]
                        if len(line) > 0 and te["DateTime"] <= line[-1]["DateTime"]:
                            for key, _ in line[-1].items():
                                if key != "DateTime":
                                    line[-1][key] = te[key]
                        else:
                            if self.update_asinterval[symbol + "-" + str(linetype) + "-" + str(interval)]:
                                self.ongreeksline(linetype, interval, symbol, line, True)
                            temp = {}
                            if linetype == 9 or linetype == 820:
                                te["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / (interval * 60)) * interval * 60)
                            if linetype == 10 or linetype == 800:
                                te["DateTime"] = opentime + timedelta(seconds=math.ceil((te["DateTime"] - opentime).total_seconds() / interval) * interval)
                            if linetype == 19:
                                if (len(line) > 0 and (te["DateTime"] - line[-1]["DateTime"]).days > interval) or len(line) == 0:
                                    te["DateTime"] = te["DateTime"] + timedelta(days=interval - 1)
                                else:
                                    te["DateTime"] = line[-1]["DateTime"] + timedelta(days=interval)
                            itemkeys = []
                            if "TC.O" in symbol and ".mix" not in symbol:
                                if linetype == 800 or linetype == 820:
                                    itemkeys = [
                                        "DateTime",
                                        "Symbol",
                                        "AnnualTradeday",
                                        "TheoVal",
                                        "IntVal",
                                        "ATV",
                                        "ExtVal",
                                        "TV",
                                        "IV",
                                        "MIV",
                                        "CPIV",
                                        "AIV",
                                        "BIV",
                                        "Delta",
                                        "Gamma",
                                        "Vega",
                                        "Theta",
                                        "Rho",
                                        "LR",
                                        "RealLR",
                                        "OPR",
                                        "ROI",
                                        "BER",
                                        "Charm",
                                        "Vanna",
                                        "Vomma",
                                        "Speed",
                                        "Zomma",
                                        "Last",
                                        "UnderlyingPrice",
                                        "Volume",
                                        "OI",
                                        "Bid",
                                        "Bid1",
                                        "Bid2",
                                        "Bid3",
                                        "Bid4",
                                        "Bid5",
                                        "Bid6",
                                        "Bid7",
                                        "Bid8",
                                        "Bid9",
                                        "BidVolume",
                                        "BidVolume1",
                                        "BidVolume2",
                                        "BidVolume3",
                                        "BidVolume4",
                                        "BidVolume5",
                                        "BidVolume6",
                                        "BidVolume7",
                                        "BidVolume8",
                                        "BidVolume9",
                                        "Bid_UpdateDatetime",
                                        "Bid1_UpdateDatetime",
                                        "Bid2_UpdateDatetime",
                                        "Bid3_UpdateDatetime",
                                        "Bid4_UpdateDatetime",
                                        "Ask",
                                        "Ask1",
                                        "Ask2",
                                        "Ask3",
                                        "Ask4",
                                        "Ask5",
                                        "Ask6",
                                        "Ask7",
                                        "Ask8",
                                        "Ask9",
                                        "AskVolume",
                                        "AskVolume1",
                                        "AskVolume2",
                                        "AskVolume3",
                                        "AskVolume4",
                                        "AskVolume5",
                                        "AskVolume6",
                                        "AskVolume7",
                                        "AskVolume8",
                                        "AskVolume9",
                                        "Ask_UpdateDatetime",
                                        "Ask1_UpdateDatetime",
                                        "Ask2_UpdateDatetime",
                                        "Ask3_UpdateDatetime",
                                        "Ask4_UpdateDatetime",
                                        "us",
                                        "us_datetime",
                                        "us_p",
                                        "us_bp1",
                                        "us_sp1",
                                        "uf",
                                        "uf_datetime",
                                        "uf_p",
                                        "uf_bp1",
                                        "uf_sp1",
                                        "usf",
                                        "usf_datetime",
                                        "usf_p",
                                    ]
                                if linetype == 9 or linetype == 10 or linetype == 19:
                                    itemkeys = ["DateTime", "Symbol", "Delta", "Gamma", "Rho", "Theta", "Vega", "EvaVol","TV", "ATV", "IV", "CPIV"]
                            else:
                                if linetype == 800 or linetype == 820:
                                    if "TC.F" in symbol:
                                        itemkeys = [
                                            "DateTime",
                                            "Symbol",
                                            "AnnualTradeday",
                                            "ATV",
                                            "ExtVal",
                                            "TV",
                                            "IV",
                                            "Last",
                                            "CSkew",
                                            "PSkew",
                                            "CIV25D",
                                            "PIV25D",
                                            "CIV10D",
                                            "PIV10D",
                                            "CallPutOIratio",
                                            "CallPutVolratio",
                                            "CallOI",
                                            "PutOI",
                                            "CallVol",
                                            "PutVol",
                                            "CKUpCnt",
                                            "CKUpVol",
                                            "CKDnCnt",
                                            "CKDnVol",
                                            "PKUpCnt",
                                            "PKUpVol",
                                            "PKDnCnt",
                                            "PKDnVol",
                                        ]
                                    else:
                                        itemkeys = [
                                            "DateTime",
                                            "Symbol",
                                            "IV",
                                            "Last",
                                            "CallPutOIratio",
                                            "CallPutVolratio",
                                            "CallOI",
                                            "PutOI",
                                            "CallVol",
                                            "PutVol",
                                            "CKUpCnt",
                                            "CKUpVol",
                                            "CKDnCnt",
                                            "CKDnVol",
                                            "PKUpCnt",
                                            "PKUpVol",
                                            "PKDnCnt",
                                            "PKDnVol",
                                        ]
                                if linetype == 9 or linetype == 10 or linetype == 19:
                                    if "TC.F" in symbol or ".mix" in symbol:
                                        itemkeys = [
                                            "DateTime",
                                            "Symbol",
                                            "IVOut",
                                            "CTR",
                                            "PTR",
                                            "RCTR",
                                            "RPTR",
                                            "FCIV25",
                                            "FPIV25",
                                            "EvaVol",
                                            "TV",
                                            "ATV",
                                            "HV_W4",
                                            "HV_W8",
                                            "HV_W13",
                                            "HV_W26",
                                            "HV_W52",
                                            "PutD",
                                            "CallD",
                                            "D25CStraddle",
                                            "D25PStraddle",
                                            "D25CTV",
                                            "D25PTV",
                                            "FIV",
                                            "IV",
                                            "Straddle",
                                            "StraddleStrike",
                                            "StraddleWeight",
                                            "CIV25D",
                                            "PIV25D",
                                            "CIV10D",
                                            "PIV10D",
                                            "CallOI",
                                            "PutOI",
                                            "CallVol",
                                            "PutVol",
                                            "CKUpCnt",
                                            "CKUpVol",
                                            "CKDnCnt",
                                            "CKDnVol",
                                            "PKUpCnt",
                                            "PKUpVol",
                                            "PKDnCnt",
                                            "PKDnVol",
                                            "CallPutOIratio",
                                            "CallPutVolratio",
                                            "CSkew",
                                            "PSkew",
                                            "VIX",
                                        ]
                                    else:
                                        itemkeys = [
                                            "DateTime",
                                            "Symbol",
                                            "IV",
                                            "VIX",
                                            "CallPutOIratio",
                                            "CallPutVolratio",
                                            "CallOI",
                                            "PutOI",
                                            "CallVol",
                                            "PutVol",
                                            "CKUpCnt",
                                            "CKUpVol",
                                            "CKDnCnt",
                                            "CKDnVol",
                                            "PKUpCnt",
                                            "PKUpVol",
                                            "PKDnCnt",
                                            "PKDnVol",
                                        ]
                            for key in itemkeys:
                                temp[key] = te[key]
                            line.append(temp)
                        if not self.update_asinterval[symbol + "-" + str(linetype) + "-" + str(interval)]:
                            self.ongreeksline(linetype, interval, symbol, line, True)
            else:
                if symbol in self.linetemp.keys():
                    self.linetemp[symbol].append(data[0])
                else:
                    self.linetemp[symbol] = data
        else:
            self.linedata[symbol + "-" + str(datatype) + "-" + str(interval)] = copy.deepcopy(data)
            self.ongreeksline(datatype, interval, symbol, data, False)

    def ongreekshistory(self, datatype, symbol, starttime, endtime, data: list):
        for interval in self.lineinterval[symbol + "-" + str(datatype)]:
            datatemp = []
            if len(data) == 0:
                if symbol + "-" + str(datatype) + "-" + str(interval) in self.linedata.keys():
                    self.ongreeklineupdate(datatype, interval, symbol, None, data, False)
                if symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime) in self.greekshistory.keys():
                    self.greekshistory[symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime)] = data
                    self.win32event.SetEvent(self.greekshistoryevent)
                return
            if interval == 1:
                if symbol + "-" + str(datatype) + "-" + str(interval) in self.linedata.keys():
                    self.ongreeklineupdate(datatype, interval, symbol, None, data, False)
                if symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime) in self.greekshistory.keys():
                    self.greekshistory[symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime)] = data
                    self.win32event.SetEvent(self.greekshistoryevent)
            else:
                if (
                    symbol + "-" + str(datatype) + "-" + str(interval) in self.linedata.keys()
                    or symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime) in self.greekshistory.keys()
                ):
                    for basedata in data:
                        basedata["DateTime"] = self.dtfilter(symbol, basedata["DateTime"])
                        if datatemp:
                            if basedata["DateTime"] <= datatemp[-1]["DateTime"]:
                                for key, _ in datatemp[-1].items():
                                    if key != "DateTime":
                                        datatemp[-1][key] = basedata[key]
                            else:
                                if datatype == 9 or datatype == 820:
                                    isduring, start = self.isduringdt(symbol, basedata["DateTime"])
                                    if isduring:
                                        basedata["DateTime"] = start + timedelta(seconds=math.ceil((basedata["DateTime"] - start).total_seconds() / (interval * 60)) * interval * 60)
                                    # if (basedata['DateTime']-datatemp[-1]['DateTime']).seconds>interval*60:
                                    #     basedata['DateTime']=basedata['DateTime']+timedelta(minutes=interval-1)
                                    # else:
                                    #     basedata['DateTime']=datatemp[-1]['DateTime']+timedelta(minutes=interval)
                                if datatype == 10 or datatype == 800:
                                    isduring, start = self.isduringdt(symbol, basedata["DateTime"])
                                    if isduring:
                                        basedata["DateTime"] = start + timedelta(seconds=math.ceil((basedata["DateTime"] - start).total_seconds() / interval) * interval)
                                    # if (basedata['DateTime']-datatemp[-1]['DateTime']).seconds>interval:
                                    #     basedata['DateTime']=basedata['DateTime']+timedelta(seconds=interval-1)
                                    # else:
                                    #     basedata['DateTime']=datatemp[-1]['DateTime']+timedelta(seconds=interval)
                                if datatype == 19:
                                    if (basedata["DateTime"] - datatemp[-1]["DateTime"]).days > interval:
                                        basedata["DateTime"] = basedata["DateTime"] + timedelta(days=interval - 1)
                                    else:
                                        basedata["DateTime"] = datatemp[-1]["DateTime"] + timedelta(days=interval)
                                datatemp.append(basedata)
                        else:
                            if datatype == 9 or datatype == 820:
                                basedata["DateTime"] = basedata["DateTime"] + timedelta(minutes=interval - 1)
                            if datatype == 10 or datatype == 800:
                                basedata["DateTime"] = basedata["DateTime"] + timedelta(seconds=interval)
                            if datatype == 19:
                                basedata["DateTime"] = basedata["DateTime"] + timedelta(days=interval - 1)
                            datatemp.append(basedata)

                if symbol + "-" + str(datatype) + "-" + str(interval) in self.linedata.keys():
                    self.ongreeklineupdate(datatype, interval, symbol, None, datatemp, False)
                if symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime) in self.greekshistory.keys():
                    self.greekshistory[symbol + "-" + str(datatype) + str(interval) + ":" + str(starttime) + "~" + str(endtime)] = datatemp
                    self.win32event.SetEvent(self.greekshistoryevent)

    def ongreeksreal(self, datatype, symbol, data: dict):
        if self.extendevent:
            self.extendevent.ongreeksreal(datatype, symbol, data)
        isduring, start = self.isduringdt(symbol, data["DateTime"])
        arrsymb=symbol.split(".")

        if isduring and symbol in self.greekslinetopic and arrsymb[3] in str(self.underlyingprice.keys()):
            realline = data
            if "TC.F" in symbol or "TC.S" in symbol or ".mix" in symbol:
                if "SSE" in symbol or "SZSE" in symbol:
                    usymbol = "TC.S." + arrsymb[2] + "." + arrsymb[3].strip("A")
                    ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3].strip("A") + "." + arrsymb[4]
                elif "IO" in symbol:
                    usymbol = "TC.S.SSE.000300"
                    ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                elif "HO" in symbol:
                    usymbol = "TC.S.SSE.000016"
                    ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                elif "MO" in symbol:
                    usymbol = "TC.S.SSE.000852"
                    ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                else:
                    usymbol = "TC.F." + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                    ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                realline["Last"] = self.underlyingprice[ufsymbol]["Last"] if ufsymbol in self.underlyingprice.keys() else None
            if "TC.O" in symbol and ".mix" not in symbol:
                arrsymb = symbol.split(".")
                greekonly = {}
                if "SSE" in symbol or "SZSE" in symbol or "CFFEX" in symbol:
                    if "IO" in symbol:
                        usymbol = "TC.S.SSE.000300"
                        ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                    elif "HO" in symbol:
                        usymbol = "TC.S.SSE.000016"
                        ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                    elif "MO" in symbol:
                        usymbol = "TC.S.SSE.000852"
                        ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                    else:
                        usymbol = "TC.S." + arrsymb[2] + "." + arrsymb[3].strip("A")
                        ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3].strip("A") + "." + arrsymb[4]

                    greekonly = {
                        "us": usymbol,
                        "us_datetime": self.underlyingprice[usymbol]["DateTime"] if usymbol in self.underlyingprice.keys() else None,
                        "us_p": self.underlyingprice[usymbol]["Last"] if usymbol in self.underlyingprice.keys() else None,
                        "us_bp1": self.underlyingprice[usymbol]["Bid"] if usymbol in self.underlyingprice.keys() else None,
                        "us_sp1": self.underlyingprice[usymbol]["Ask"] if usymbol in self.underlyingprice.keys() else None,
                        "uf": "",
                        "uf_datetime": None,
                        "uf_p": None,
                        "uf_bp1": None,
                        "uf_sp1": None,
                        "usf": ufsymbol,
                        "usf_datetime": self.underlyingprice[ufsymbol]["DateTime"] if ufsymbol in self.underlyingprice.keys() else None,
                        "usf_p": self.underlyingprice[ufsymbol]["Last"] if ufsymbol in self.underlyingprice.keys() else None,
                    }
                else:
                    usymbol = "TC.F." + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                    ufsymbol = "TC.F.U_" + arrsymb[2] + "." + arrsymb[3] + "." + arrsymb[4]
                    greekonly = {
                        "us": "",
                        "us_datetime": None,
                        "us_p": None,
                        "us_bp1": None,
                        "us_sp1": None,
                        "uf": usymbol,
                        "uf_datetime": self.underlyingprice[usymbol]["DateTime"] if usymbol in self.underlyingprice.keys() else None,
                        "uf_p": self.underlyingprice[usymbol]["Last"] if usymbol in self.underlyingprice.keys() else None,
                        "uf_bp1": self.underlyingprice[usymbol]["Bid"] if usymbol in self.underlyingprice.keys() else None,
                        "uf_sp1": self.underlyingprice[usymbol]["Ask"] if usymbol in self.underlyingprice.keys() else None,
                        "usf": ufsymbol,
                        "usf_datetime": self.underlyingprice[ufsymbol]["DateTime"] if ufsymbol in self.underlyingprice.keys() else None,
                        "usf_p": self.underlyingprice[ufsymbol]["Last"] if ufsymbol in self.underlyingprice.keys() else None,
                    }

                realline["DateTime"] = self.dtfilter(symbol, data["DateTime"])

                realline.update(
                    {
                        "Last": self.underlyingprice[symbol]["Last"] if symbol in self.underlyingprice.keys() else None,
                        "UnderlyingPrice": self.underlyingprice[usymbol]["Last"] if usymbol in self.underlyingprice.keys() else None,
                        "Volume": self.underlyingprice[symbol]["Volume"],
                        "OI": self.underlyingprice[symbol]["OpenInterest"],
                        "Bid": self.underlyingprice[symbol]["Bid"],
                        "Bid1": self.underlyingprice[symbol]["Bid1"],
                        "Bid2": self.underlyingprice[symbol]["Bid2"],
                        "Bid3": self.underlyingprice[symbol]["Bid3"],
                        "Bid4": self.underlyingprice[symbol]["Bid4"],
                        "Bid5": self.underlyingprice[symbol]["Bid5"],
                        "Bid6": self.underlyingprice[symbol]["Bid6"],
                        "Bid7": self.underlyingprice[symbol]["Bid7"],
                        "Bid8": self.underlyingprice[symbol]["Bid8"],
                        "Bid9": self.underlyingprice[symbol]["Bid9"],
                        "BidVolume": self.underlyingprice[symbol]["BidVolume"],
                        "BidVolume1": self.underlyingprice[symbol]["BidVolume1"],
                        "BidVolume2": self.underlyingprice[symbol]["BidVolume2"],
                        "BidVolume3": self.underlyingprice[symbol]["BidVolume3"],
                        "BidVolume4": self.underlyingprice[symbol]["BidVolume4"],
                        "BidVolume5": self.underlyingprice[symbol]["BidVolume5"],
                        "BidVolume6": self.underlyingprice[symbol]["BidVolume6"],
                        "BidVolume7": self.underlyingprice[symbol]["BidVolume7"],
                        "BidVolume8": self.underlyingprice[symbol]["BidVolume8"],
                        "BidVolume9": self.underlyingprice[symbol]["BidVolume9"],
                        "Bid_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Bid1_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Bid2_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Bid3_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Bid4_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Ask": self.underlyingprice[symbol]["Ask"],
                        "Ask1": self.underlyingprice[symbol]["Ask1"],
                        "Ask2": self.underlyingprice[symbol]["Ask2"],
                        "Ask3": self.underlyingprice[symbol]["Ask3"],
                        "Ask4": self.underlyingprice[symbol]["Ask4"],
                        "Ask5": self.underlyingprice[symbol]["Ask5"],
                        "Ask6": self.underlyingprice[symbol]["Ask6"],
                        "Ask7": self.underlyingprice[symbol]["Ask7"],
                        "Ask8": self.underlyingprice[symbol]["Ask8"],
                        "Ask9": self.underlyingprice[symbol]["Ask9"],
                        "AskVolume": self.underlyingprice[symbol]["AskVolume"],
                        "AskVolume1": self.underlyingprice[symbol]["AskVolume1"],
                        "AskVolume2": self.underlyingprice[symbol]["AskVolume2"],
                        "AskVolume3": self.underlyingprice[symbol]["AskVolume3"],
                        "AskVolume4": self.underlyingprice[symbol]["AskVolume4"],
                        "AskVolume5": self.underlyingprice[symbol]["AskVolume5"],
                        "AskVolume6": self.underlyingprice[symbol]["AskVolume6"],
                        "AskVolume7": self.underlyingprice[symbol]["AskVolume7"],
                        "AskVolume8": self.underlyingprice[symbol]["AskVolume8"],
                        "AskVolume9": self.underlyingprice[symbol]["AskVolume9"],
                        "Ask_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Ask1_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Ask2_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Ask3_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                        "Ask4_UpdateDatetime": self.underlyingprice[symbol]["DateTime"],
                    }
                )
                realline.update(greekonly)
            self.ongreeklineupdate(datatype, None, symbol, start, [realline], True)

    def OnQuoteData(self, SymbolType, DataType, QuoteData):
        quote = self._Dispatch(QuoteData)
        if DataType == 820 or DataType == 800:
            dogshis = []
            oivol = None
            symbol = quote.GetStringData("Symbol")
            if quote.GetItemValue(-1, 1) == 2:
                self.greeksputcallvol[symbol + "-" + str(DataType)] = {}
            for i in range(quote.GetValueData("Count")):
                if "TC.O" in symbol:
                    date = quote.GetItemValue(i, 0)
                    if date < 0 or date > 20381230:
                        return
                    BidDatetime = "{:0>6d}".format((quote.GetItemValue(i, 76) if quote.GetItemValue(i, 76) > 0 and quote.GetItemValue(i, 76) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Bid1Datetime = "{:0>6d}".format((quote.GetItemValue(i, 77) if quote.GetItemValue(i, 77) > 0 and quote.GetItemValue(i, 77) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Bid2Datetime = "{:0>6d}".format((quote.GetItemValue(i, 78) if quote.GetItemValue(i, 78) > 0 and quote.GetItemValue(i, 78) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Bid3Datetime = "{:0>6d}".format((quote.GetItemValue(i, 79) if quote.GetItemValue(i, 79) > 0 and quote.GetItemValue(i, 79) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Bid4Datetime = "{:0>6d}".format((quote.GetItemValue(i, 80) if quote.GetItemValue(i, 80) > 0 and quote.GetItemValue(i, 80) < 240000000 else quote.GetItemValue(i, 1)) // 1000)

                    AskDatetime = "{:0>6d}".format((quote.GetItemValue(i, 106) if quote.GetItemValue(i, 106) > 0 and quote.GetItemValue(i, 106) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Ask1Datetime = "{:0>6d}".format((quote.GetItemValue(i, 107) if quote.GetItemValue(i, 107) > 0 and quote.GetItemValue(i, 107) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Ask2Datetime = "{:0>6d}".format((quote.GetItemValue(i, 108) if quote.GetItemValue(i, 108) > 0 and quote.GetItemValue(i, 108) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Ask3Datetime = "{:0>6d}".format((quote.GetItemValue(i, 109) if quote.GetItemValue(i, 109) > 0 and quote.GetItemValue(i, 109) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    Ask4Datetime = "{:0>6d}".format((quote.GetItemValue(i, 110) if quote.GetItemValue(i, 110) > 0 and quote.GetItemValue(i, 110) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    usdatetime = (
                        str(quote.GetItemValue(i, 123))
                        + " "
                        + "{:0>6d}".format((quote.GetItemValue(i, 124) if quote.GetItemValue(i, 124) > 0 and quote.GetItemValue(i, 124) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    )
                    ufdatetime = (
                        str(quote.GetItemValue(i, 140))
                        + " "
                        + "{:0>6d}".format((quote.GetItemValue(i, 141) if quote.GetItemValue(i, 141) > 0 and quote.GetItemValue(i, 141) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    )
                    usfdatetime = (
                        str(quote.GetItemValue(i, 157))
                        + " "
                        + "{:0>6d}".format((quote.GetItemValue(i, 158) if quote.GetItemValue(i, 158) > 0 and quote.GetItemValue(i, 158) < 240000000 else quote.GetItemValue(i, 1)) // 1000)
                    )

                    dogshis.append(
                        {
                            "DateTime": datetime.strptime(str(date) + " " + "{:0>6d}".format(quote.GetItemValue(i, 1) // 1000), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Symbol": symbol,
                            "AnnualTradeday": iff(quote.GetItemValue(i, 2), 10000000000),
                            "TheoVal": iff(quote.GetItemValue(i, 3), 10000000000),
                            "IntVal": iff(quote.GetItemValue(i, 4), 10000000000),
                            "ATV": iff(quote.GetItemValue(i, 5), 10000000000),
                            "ExtVal": iff(quote.GetItemValue(i, 6), 10000000000),
                            "TV": iff(quote.GetItemValue(i, 7), 10000000000),
                            "IV": iff(quote.GetItemValue(i, 8), 10000000000),
                            "MIV": iff(quote.GetItemValue(i, 9), 10000000000),
                            "CPIV": iff(quote.GetItemValue(i, 10), 10000000000),
                            "AIV": iff(quote.GetItemValue(i, 11), 10000000000),
                            "BIV": iff(quote.GetItemValue(i, 12), 10000000000),
                            "Delta": iff(quote.GetItemValue(i, 13), 10000000000),
                            "Gamma": iff(quote.GetItemValue(i, 14), 10000000000),
                            "Vega": iff(quote.GetItemValue(i, 15), 10000000000),
                            "Theta": iff(quote.GetItemValue(i, 16), 10000000000),
                            "Rho": iff(quote.GetItemValue(i, 17), 10000000000),
                            "LR": iff(quote.GetItemValue(i, 18), 10000000000),
                            "RealLR": iff(quote.GetItemValue(i, 19), 10000000000),
                            "OPR": iff(quote.GetItemValue(i, 20), 10000000000),
                            "ROI": iff(quote.GetItemValue(i, 21), 10000000000),
                            "BER": iff(quote.GetItemValue(i, 22), 10000000000),
                            "Charm": iff(quote.GetItemValue(i, 23), 10000000000),
                            "Vanna": iff(quote.GetItemValue(i, 24), 10000000000),
                            "Vomma": iff(quote.GetItemValue(i, 25), 100000000),
                            "Speed": iff(quote.GetItemValue(i, 26), 10000000000),
                            "Zomma": iff(quote.GetItemValue(i, 27), 10000000000),
                            "Last": iff(quote.GetItemValue(i, 28), 10000000000),
                            "UnderlyingPrice": iff(quote.GetItemValue(i, 29), 10000000000),
                            "Volume": quote.GetItemValue(i, 30) if quote.GetItemValue(i, 30) != -9223372036854775808 else 0,
                            "OI": quote.GetItemValue(i, 31) if quote.GetItemValue(i, 31) != -9223372036854775808 else 0,
                            # 'sta':iff(quote.GetItemValue(i,32) ,
                            "Bid": iff(quote.GetItemValue(i, 51), 10000000000),
                            "Bid1": iff(quote.GetItemValue(i, 52), 10000000000),
                            "Bid2": iff(quote.GetItemValue(i, 53), 10000000000),
                            "Bid3": iff(quote.GetItemValue(i, 54), 10000000000),
                            "Bid4": iff(quote.GetItemValue(i, 55), 10000000000),
                            "Bid5": iff(quote.GetItemValue(i, 56), 10000000000),
                            "Bid6": iff(quote.GetItemValue(i, 57), 10000000000),
                            "Bid7": iff(quote.GetItemValue(i, 58), 10000000000),
                            "Bid8": iff(quote.GetItemValue(i, 59), 10000000000),
                            "Bid9": iff(quote.GetItemValue(i, 60), 10000000000),
                            "BidVolume": iff(quote.GetItemValue(i, 61)),
                            "BidVolume1": iff(quote.GetItemValue(i, 62)),
                            "BidVolume2": iff(quote.GetItemValue(i, 63)),
                            "BidVolume3": iff(quote.GetItemValue(i, 64)),
                            "BidVolume4": iff(quote.GetItemValue(i, 65)),
                            "BidVolume5": iff(quote.GetItemValue(i, 66)),
                            "BidVolume6": iff(quote.GetItemValue(i, 67)),
                            "BidVolume7": iff(quote.GetItemValue(i, 68)),
                            "BidVolume8": iff(quote.GetItemValue(i, 69)),
                            "BidVolume9": iff(quote.GetItemValue(i, 70)),
                            "Bid_UpdateDatetime": datetime.strptime(str(date) + " " + BidDatetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Bid1_UpdateDatetime": datetime.strptime(str(date) + " " + Bid1Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Bid2_UpdateDatetime": datetime.strptime(str(date) + " " + Bid2Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Bid3_UpdateDatetime": datetime.strptime(str(date) + " " + Bid3Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Bid4_UpdateDatetime": datetime.strptime(str(date) + " " + Bid4Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Ask": iff(quote.GetItemValue(i, 81), 10000000000),
                            "Ask1": iff(quote.GetItemValue(i, 82), 10000000000),
                            "Ask2": iff(quote.GetItemValue(i, 83), 10000000000),
                            "Ask3": iff(quote.GetItemValue(i, 84), 10000000000),
                            "Ask4": iff(quote.GetItemValue(i, 85), 10000000000),
                            "Ask5": iff(quote.GetItemValue(i, 86), 10000000000),
                            "Ask6": iff(quote.GetItemValue(i, 87), 10000000000),
                            "Ask7": iff(quote.GetItemValue(i, 88), 10000000000),
                            "Ask8": iff(quote.GetItemValue(i, 89), 10000000000),
                            "Ask9": iff(quote.GetItemValue(i, 90), 10000000000),
                            "AskVolume": iff(quote.GetItemValue(i, 91)),
                            "AskVolume1": iff(quote.GetItemValue(i, 92)),
                            "AskVolume2": iff(quote.GetItemValue(i, 93)),
                            "AskVolume3": iff(quote.GetItemValue(i, 94)),
                            "AskVolume4": iff(quote.GetItemValue(i, 95)),
                            "AskVolume5": iff(quote.GetItemValue(i, 96)),
                            "AskVolume6": iff(quote.GetItemValue(i, 97)),
                            "AskVolume7": iff(quote.GetItemValue(i, 98)),
                            "AskVolume8": iff(quote.GetItemValue(i, 99)),
                            "AskVolume9": iff(quote.GetItemValue(i, 100)),
                            "Ask_UpdateDatetime": datetime.strptime(str(date) + " " + AskDatetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Ask1_UpdateDatetime": datetime.strptime(str(date) + " " + Ask1Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Ask2_UpdateDatetime": datetime.strptime(str(date) + " " + Ask2Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Ask3_UpdateDatetime": datetime.strptime(str(date) + " " + Ask3Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Ask4_UpdateDatetime": datetime.strptime(str(date) + " " + Ask4Datetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "us": quote.GetItemString(i, 111),
                            "us_datetime": datetime.strptime(usdatetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "us_p": iff(quote.GetItemValue(i, 125), 10000000000),
                            "us_bp1": iff(quote.GetItemValue(i, 126), 10000000000),
                            "us_sp1": iff(quote.GetItemValue(i, 127), 10000000000),
                            "uf": quote.GetItemString(i, 128),
                            "uf_datetime": datetime.strptime(ufdatetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "uf_p": iff(quote.GetItemValue(i, 142), 10000000000),
                            "uf_bp1": iff(quote.GetItemValue(i, 143), 10000000000),
                            "uf_sp1": iff(quote.GetItemValue(i, 144), 10000000000),
                            "usf": quote.GetItemString(i, 145),
                            "usf_datetime": datetime.strptime(usfdatetime, "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "usf_p": iff(quote.GetItemValue(i, 159), 10000000000),
                        }
                    )
                else:
                    if quote.GetItemValue(-1, 1) == 2:
                        self.greeksputcallvol[symbol + "-" + str(DataType)][
                            datetime.strptime(str(quote.GetItemValue(i, 0)) + " " + "{:0>6d}".format(quote.GetItemValue(i, 1) // 1000), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                        ] = {
                            "CallVol": iff(quote.GetItemValue(i, 39)),
                            "PutVol": iff(quote.GetItemValue(i, 40)),
                            "CallOI": iff(quote.GetItemValue(i, 41)),
                            "PutOI": iff(quote.GetItemValue(i, 42)),
                            "CKUpCnt": iff(quote.GetItemValue(i, 43)),
                            "CKUpVol": iff(quote.GetItemValue(i, 44)),
                            "CKDnCnt": iff(quote.GetItemValue(i, 45)),
                            "CKDnVol": iff(quote.GetItemValue(i, 46)),
                            "PKUpCnt": iff(quote.GetItemValue(i, 47)),
                            "PKUpVol": iff(quote.GetItemValue(i, 48)),
                            "PKDnCnt": iff(quote.GetItemValue(i, 49)),
                            "PKDnVol": iff(quote.GetItemValue(i, 50)),
                        }
                    else:
                        if symbol + "-" + str(DataType) in self.greeksputcallvol:
                            if (
                                datetime.strptime(str(quote.GetItemValue(i, 0)) + " " + "{:0>6d}".format(quote.GetItemValue(i, 1) // 1000), "%Y%m%d %H%M%S").replace(tzinfo=self.tz)
                                + timedelta(hours=8)
                                in self.greeksputcallvol[symbol + "-" + str(DataType)]
                            ):
                                oivol = self.greeksputcallvol[symbol + "-" + str(DataType)][
                                    datetime.strptime(str(quote.GetItemValue(i, 0)) + " " + "{:0>6d}".format(quote.GetItemValue(i, 1) // 1000), "%Y%m%d %H%M%S").replace(tzinfo=self.tz)
                                    + timedelta(hours=8)
                                ]
                        if "TC.F" in symbol:
                            dogshis.append(
                                {
                                    "DateTime": datetime.strptime(str(quote.GetItemValue(i, 0)) + " " + "{:0>6d}".format(quote.GetItemValue(i, 1) // 1000), "%Y%m%d %H%M%S").replace(tzinfo=self.tz)
                                    + timedelta(hours=8),
                                    "Symbol": symbol,
                                    "AnnualTradeday": iff(quote.GetItemValue(i, 2), 10000000000),
                                    # 'TheoVal':iff(quote.GetItemValue(i,3),10000000000),
                                    # 'IntVal':iff(quote.GetItemValue(i,160),10000000000),
                                    "ATV": iff(quote.GetItemValue(i, 5), 10000000000),
                                    "ExtVal": iff(quote.GetItemValue(i, 6), 10000000000),
                                    "TV": iff(quote.GetItemValue(i, 7), 10000000000),
                                    "IV": iff(quote.GetItemValue(i, 8), 10000000000),
                                    "Last": iff(quote.GetItemValue(i, 28), 10000000000),
                                    "CSkew": iff(quote.GetItemValue(i, 33), 1000000),
                                    "PSkew": iff(quote.GetItemValue(i, 34), 1000000),
                                    "CIV25D": iff(quote.GetItemValue(i, 35), 100000000),
                                    "PIV25D": iff(quote.GetItemValue(i, 36), 100000000),
                                    "CIV10D": iff(quote.GetItemValue(i, 37), 100000000),
                                    "PIV10D": iff(quote.GetItemValue(i, 38), 100000000),
                                    "CallPutOIratio": oivol["CallOI"] / oivol["PutOI"] if oivol and oivol["CallOI"] != 0 and oivol["PutOI"] != 0 else None,
                                    "CallPutVolratio": oivol["CallVol"] / oivol["PutVol"] if oivol and oivol["CallVol"] != 0 and oivol["PutVol"] != 0 else None,
                                    "CallOI": oivol["CallOI"] if oivol else None,
                                    "PutOI": oivol["PutOI"] if oivol else None,
                                    "CallVol": oivol["CallVol"] if oivol else None,
                                    "PutVol": oivol["PutVol"] if oivol else None,
                                    "CKUpCnt": oivol["CKUpCnt"] if oivol else None,
                                    "CKUpVol": oivol["CKUpVol"] if oivol else None,
                                    "CKDnCnt": oivol["CKDnCnt"] if oivol else None,
                                    "CKDnVol": oivol["CKDnVol"] if oivol else None,
                                    "PKUpCnt": oivol["PKUpCnt"] if oivol else None,
                                    "PKUpVol": oivol["PKUpVol"] if oivol else None,
                                    "PKDnCnt": oivol["PKDnCnt"] if oivol else None,
                                    "PKDnVol": oivol["PKDnVol"] if oivol else None,
                                }
                            )
                        else:
                            dogshis.append(
                                {
                                    "DateTime": datetime.strptime(str(quote.GetItemValue(i, 0)) + " " + "{:0>6d}".format(quote.GetItemValue(i, 1) // 1000), "%Y%m%d %H%M%S").replace(tzinfo=self.tz)
                                    + timedelta(hours=8),
                                    "Symbol": symbol,
                                    "IV": iff(quote.GetItemValue(i, 8), 10000000000),
                                    "Last": iff(quote.GetItemValue(i, 28), 10000000000),
                                    "CallPutOIratio": oivol["CallOI"] / oivol["PutOI"] if oivol and oivol["CallOI"] != 0 and oivol["PutOI"] != 0 else None,
                                    "CallPutVolratio": oivol["CallVol"] / oivol["PutVol"] if oivol and oivol["CallVol"] != 0 and oivol["PutVol"] != 0 else None,
                                    "CallOI": oivol["CallOI"] if oivol else None,
                                    "PutOI": oivol["PutOI"] if oivol else None,
                                    "CallVol": oivol["CallVol"] if oivol else None,
                                    "PutVol": oivol["PutVol"] if oivol else None,
                                    "CKUpCnt": oivol["CKUpCnt"] if oivol else None,
                                    "CKUpVol": oivol["CKUpVol"] if oivol else None,
                                    "CKDnCnt": oivol["CKDnCnt"] if oivol else None,
                                    "CKDnVol": oivol["CKDnVol"] if oivol else None,
                                    "PKUpCnt": oivol["PKUpCnt"] if oivol else None,
                                    "PKUpVol": oivol["PKUpVol"] if oivol else None,
                                    "PKDnCnt": oivol["PKDnCnt"] if oivol else None,
                                    "PKDnVol": oivol["PKDnVol"] if oivol else None,
                                }
                            )
            if quote.GetItemValue(-1, 1) != 2:
                self.ongreekshistory(DataType, symbol, quote.GetValueData("StartTime"), quote.GetValueData("EndTime"), dogshis)
                if symbol + "-" + str(DataType) in self.greeksputcallvol:
                    del self.greeksputcallvol[symbol + "-" + str(DataType)]
            self.quoteapi.unsubquote(DataType, symbol, quote.GetValueData("StartTime"), quote.GetValueData("EndTime"), str(quote.GetItemValue(-1, 1)))
        elif DataType == 2:
            his = []
            datacout = quote.ItemCount
            clsid = self.quoteapi.mod.TimeAndSalesItem._reg_clsid_
            subquotefac = self.quoteapi.mod.qdiTimeAndSalesItem
            item = self.quoteapi.createDispatch(clsid, subquotefac)
            for i in range(datacout):
                if quote.GetItem(i, item):
                    his.append(
                        {
                            "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.FilledTime), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Symbol": quote.Symbol,
                            "Ask": iff(item.Ask, 10000000000),
                            "Bid": iff(item.Bid, 10000000000),
                            "Last": iff(item.TradingPrice, 10000000000),
                            "Quantity": iff(item.TradeQuantity),
                            "Volume": iff(item.TradeVolume),
                            "OpenInterest": iff(item.GetItemValue("OI")),
                        }
                    )
            self.onquotehistory(DataType, quote.Symbol, quote.StartTime, quote.EndTime, his)
            self.quoteapi.unsubquote(DataType, quote.Symbol, quote.StartTime, quote.EndTime)
        elif DataType == 4 or DataType == 5:
            his = []
            datacout = quote.ItemCount
            clsid = self.quoteapi.mod.TechanicalAnalysisItem._reg_clsid_
            subquotefac = self.quoteapi.mod.qdiTechanicalAnalysisItem
            item = self.quoteapi.createDispatch(clsid, subquotefac)
            for i in range(datacout):
                if quote.GetItem(i, item):
                    his.append(
                        {
                            "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.Time), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                            "Symbol": quote.Symbol,
                            "Open": iff(item.Open, 10000000000),
                            "High": iff(item.High, 10000000000),
                            "Low": iff(item.Low, 10000000000),
                            "Close": iff(item.Close, 10000000000),
                            "Volume": iff(item.Volume),
                            "OpenInterest": item.GetOptValue("OI") if item.GetOptValue("OI") > 0 else item.UnchVolume,
                            "DownTick": item.DownTick,
                            "DownVolume": item.DownVolume,
                            "UnchVolume": 0,
                            "UpTick": item.UpTick,
                            "UpVolume": item.UpVolume,
                        }
                    )
            self.onquotehistory(DataType, quote.Symbol, quote.StartTime, quote.EndTime, his)
            self.quoteapi.unsubquote(DataType, quote.Symbol, quote.StartTime, quote.EndTime)
        elif DataType == 9 or DataType == 19:  # GREEKS 1K:9 DK:19
            greekshis = []
            oivol = None
            datacout = quote.ItemCount
            clsid = self.quoteapi.mod.TechanicalAnalysisItem._reg_clsid_
            subquotefac = self.quoteapi.mod.qdiTechanicalAnalysisItem
            item = self.quoteapi.createDispatch(clsid, subquotefac)
            if quote.GetItemData(-1, 2) == "2":
                self.greeksputcallvol[quote.Symbol + "-" + str(DataType)] = {}
            for i in range(datacout):
                if quote.GetItem(i, item):
                    if "TC.O" in quote.Symbol and ".mix" not in quote.Symbol:
                        greekshis.append(
                            {
                                "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.Time), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                                "Symbol": quote.Symbol,
                                "Delta": iff(item.GetOptValue("Delta"), 10000000000),
                                "Gamma": iff(item.GetOptValue("Gamma"), 10000000000),
                                "Rho": iff(item.GetOptValue("Rho"), 10000000000),
                                "Theta": iff(item.GetOptValue("Theta"), 10000000000),
                                "Vega": iff(item.GetOptValue("Vega"), 10000000000),
                                "EvaVol": iff(item.GetOptValue("EvaVol"),10000000000),
                                # "SkewDelta": iff(item.GetOptValue("SkewDelta"), 1000000000000),
                                "TV": iff(item.GetOptValue("TV"), 10000000000),
                                "ATV": iff(item.GetOptValue("ATV"), 10000000000),
                                "IV": iff(item.GetOptValue("Volatility"), 10000000000),
                                "CPIV": iff(item.GetOptValue("CPIV"), 10000000000),
                            }
                        )
                    else:
                        if quote.GetItemData(-1, 2) == "2":
                            self.greeksputcallvol[quote.Symbol + "-" + str(DataType)][
                                datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.Time), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                            ] = {
                                "CallOI": iff(item.GetOptValue("CallOI")),
                                "PutOI": iff(item.GetOptValue("PutOI")),
                                "CallVol": iff(item.GetOptValue("CallVol")),
                                "PutVol": iff(item.GetOptValue("PutVol")),
                                "CKUpCnt": iff(item.GetOptValue("CKUpCnt")),
                                "CKUpVol": iff(item.GetOptValue("CKUpVol")),
                                "CKDnCnt": iff(item.GetOptValue("CKDnCnt")),
                                "CKDnVol": iff(item.GetOptValue("CKDnVol")),
                                "PKUpCnt": iff(item.GetOptValue("PKUpCnt")),
                                "PKUpVol": iff(item.GetOptValue("PKUpVol")),
                                "PKDnCnt": iff(item.GetOptValue("PKDnCnt")),
                                "PKDnVol": iff(item.GetOptValue("PKDnVol")),
                            }
                            self.voloievent.set()
                        else:
                            if quote.Symbol + "-" + str(DataType) in self.greeksputcallvol:
                                if (
                                    datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.Time), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                                    in self.greeksputcallvol[quote.Symbol + "-" + str(DataType)]
                                ):
                                    oivol = self.greeksputcallvol[quote.Symbol + "-" + str(DataType)][
                                        datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.Time), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                                    ]
                            if "TC.F" in quote.Symbol or ".mix" in quote.Symbol:
                                greekshis.append(
                                    {
                                        "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.Time), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                                        "Symbol": quote.Symbol,
                                        "IVOut": iff(item.GetOptValue("IVOut")),
                                        "CTR": iff(item.GetOptValue("CTR"), 10000000000),
                                        "PTR": iff(item.GetOptValue("PTR"), 10000000000),
                                        "RCTR": iff(item.GetOptValue("RCTR"), 10000000000),
                                        "RPTR": iff(item.GetOptValue("RPTR"), 10000000000),
                                        "FCIV25": iff(item.GetOptValue("25FCIV"), 100000000),
                                        "FPIV25": iff(item.GetOptValue("25FPIV"), 100000000),
                                        "EvaVol": iff(item.GetOptValue("EvaVol"),100000000),
                                        # "ExtVal": iff(item.GetOptValue("ExtVal"),10000000000),
                                        "TV": iff(item.GetOptValue("TV"), 10000000000),
                                        "ATV": iff(item.GetOptValue("ATV"), 10000000000),
                                        "HV_W4": iff(item.GetOptValue("HV_W4"), 10000000000),
                                        "HV_W8": iff(item.GetOptValue("HV_W8"), 10000000000),
                                        "HV_W13": iff(item.GetOptValue("HV_W13"), 10000000000),
                                        "HV_W26": iff(item.GetOptValue("HV_W26"), 10000000000),
                                        "HV_W52": iff(item.GetOptValue("HV_W52"), 10000000000),
                                        "PutD": iff(item.GetOptValue("Putd"), 10000000000),
                                        "CallD": iff(item.GetOptValue("Calld"), 10000000000),
                                        "D25CStraddle": iff(item.GetOptValue("25DCStraddle"), 10000000000),
                                        "D25PStraddle": iff(item.GetOptValue("25DPStraddle"), 10000000000),
                                        "D25CTV": iff(item.GetOptValue("25DCTV"), 10000000000),
                                        "D25PTV": iff(item.GetOptValue("25DPTV"), 10000000000),
                                        "FIV": iff(item.GetOptValue("FIV"), 100000000),
                                        "IV": iff(item.GetOptValue("Volatility"), 100000000),
                                        "Straddle": iff(item.GetOptValue("Straddle"), 10000000000),
                                        "StraddleStrike": iff(item.GetOptValue("StraddleStrike"), 10000000000),
                                        "StraddleWeight": iff(item.GetOptValue("StraddleWeight"), 10000000000),
                                        "CIV25D": iff(item.GetOptValue("25DCIV"), 100000000),
                                        "PIV25D": iff(item.GetOptValue("25DPIV"), 100000000),
                                        "CIV10D": iff(item.GetOptValue("10DCIV"), 100000000),
                                        "PIV10D": iff(item.GetOptValue("10DPIV"), 100000000),
                                        "CallOI": oivol["CallOI"] if oivol else None,
                                        "PutOI": oivol["PutOI"] if oivol else None,
                                        "CallVol": oivol["CallVol"] if oivol else None,
                                        "PutVol": oivol["PutVol"] if oivol else None,
                                        "CKUpCnt": oivol["CKUpCnt"] if oivol else None,
                                        "CKUpVol": oivol["CKUpVol"] if oivol else None,
                                        "CKDnCnt": oivol["CKDnCnt"] if oivol else None,
                                        "CKDnVol": oivol["CKDnVol"] if oivol else None,
                                        "PKUpCnt": oivol["PKUpCnt"] if oivol else None,
                                        "PKUpVol": oivol["PKUpVol"] if oivol else None,
                                        "PKDnCnt": oivol["PKDnCnt"] if oivol else None,
                                        "PKDnVol": oivol["PKDnVol"] if oivol else None,
                                        "CallPutOIratio": oivol["CallOI"] / oivol["PutOI"] if oivol and oivol["CallOI"] and oivol["CallOI"] != 0 and oivol["PutOI"] and oivol["PutOI"] != 0 else None,
                                        "CallPutVolratio": oivol["CallVol"] / oivol["PutVol"] if oivol and oivol["CallVol"] and oivol["CallVol"] != 0 and oivol["PutVol"] and oivol["PutVol"] != 0 else None,
                                        "CSkew":iff(item.GetOptValue("CSkew"), 100000000),
                                        "PSkew":iff(item.GetOptValue("PSkew"), 100000000),
                                        # "CSkew": (
                                        #     item.GetOptValue("Calld") / item.GetOptValue("Volatility") * 100
                                        #     if item.GetOptValue("Calld") > -9999999999999999 and item.GetOptValue("Volatility") > -9999999999999999 and item.GetOptValue("Volatility") != 0
                                        #     else None
                                        # ),
                                        # "PSkew": (
                                        #     item.GetOptValue("Putd") / item.GetOptValue("Volatility") * 100
                                        #     if item.GetOptValue("Putd") > -9999999999999999 and item.GetOptValue("Volatility") > -9999999999999999 and item.GetOptValue("Volatility") != 0
                                        #     else None
                                        # ),
                                        "VIX": iff(item.GetOptValue("VIX"), 100000000),
                                        "CallDownPrice": iff(item.GetOptValue("CDP"), 10000000000),
                                        "CallDownMidPrice": iff(item.GetOptValue("CDMP"), 10000000000),
                                        "CallUpPrice": iff(item.GetOptValue("CUP"), 10000000000),
                                        "CallUpMidPrice": iff(item.GetOptValue("CUMP"), 10000000000),
                                        "PutDownPrice": iff(item.GetOptValue("PDP"), 10000000000),
                                        "PutDownMidPrice": iff(item.GetOptValue("PDMP"), 10000000000),
                                        "PutUpPrice": iff(item.GetOptValue("PUP"), 10000000000),
                                        "PutUpMidPrice": iff(item.GetOptValue("PUMP"), 10000000000),
                                    }
                                )
                            else:
                                greekshis.append(
                                    {
                                        "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.Time), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                                        "Symbol": quote.Symbol,
                                        "IV": iff(item.GetOptValue("Volatility"), 100000000),
                                        "VIX": iff(item.GetOptValue("VIX"), 100000000),
                                        "CallPutOIratio": oivol["CallOI"] / oivol["PutOI"] if oivol and oivol["CallOI"] != 0 and oivol["PutOI"] != 0 else None,
                                        "CallPutVolratio": oivol["CallVol"] / oivol["PutVol"] if oivol and oivol["CallVol"] != 0 and oivol["PutVol"] != 0 else None,
                                        "CallOI": oivol["CallOI"] if oivol else None,
                                        "PutOI": oivol["PutOI"] if oivol else None,
                                        "CallVol": oivol["CallVol"] if oivol else None,
                                        "PutVol": oivol["PutVol"] if oivol else None,
                                        "CKUpCnt": oivol["CKUpCnt"] if oivol else None,
                                        "CKUpVol": oivol["CKUpVol"] if oivol else None,
                                        "CKDnCnt": oivol["CKDnCnt"] if oivol else None,
                                        "CKDnVol": oivol["CKDnVol"] if oivol else None,
                                        "PKUpCnt": oivol["PKUpCnt"] if oivol else None,
                                        "PKUpVol": oivol["PKUpVol"] if oivol else None,
                                        "PKDnCnt": oivol["PKDnCnt"] if oivol else None,
                                        "PKDnVol": oivol["PKDnVol"] if oivol else None,
                                    }
                                )

            if quote.GetItemData(-1, 2) != "2":
                self.ongreekshistory(DataType, quote.Symbol, quote.StartTime, quote.EndTime, greekshis)
                if quote.Symbol + "-" + str(DataType) in self.greeksputcallvol:
                    del self.greeksputcallvol[quote.Symbol + "-" + str(DataType)]
            self.quoteapi.unsubquote(DataType, quote.Symbol, quote.StartTime, quote.EndTime, quote.GetItemData(-1, 2))
        elif DataType == 10:  # GREEKS TICKS:10
            greekshis = []
            oivol = None
            datacout = quote.ItemCount
            clsid = self.quoteapi.mod.TimeAndSalesItem._reg_clsid_
            subquotefac = self.quoteapi.mod.qdiTimeAndSalesItem
            item = self.quoteapi.createDispatch(clsid, subquotefac)
            if quote.GetItemData(-1, 2) == "2":
                self.greeksputcallvol[quote.Symbol] = {}
            for i in range(datacout):
                if quote.GetItem(i, item):
                    if "TC.O" in quote.Symbol and ".mix" not in quote.Symbol:
                        greekshis.append(
                            {
                                "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.GetItemValue("TradingHours")), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                                "Symbol": quote.Symbol,
                                "Delta": iff(item.GetItemValue("Delta"), 10000000000),
                                "Gamma": iff(item.GetItemValue("Gamma"), 10000000000),
                                "Rho": iff(item.GetItemValue("Rho"), 10000000000),
                                "Theta": iff(item.GetItemValue("Theta"), 10000000000),
                                "Vega": iff(item.GetItemValue("Vega"), 10000000000),
                                "TV": iff(item.GetItemValue("TV"), 10000000000),
                                "ATV": iff(item.GetItemValue("ATV"), 10000000000),
                                "EvaVol": iff(item.GetItemValue("EvaVol"),100000000),
                                "IV": iff(item.GetItemValue("Volatility"), 100000000),
                                "CPIV": iff(item.GetItemValue("CPIV"), 100000000),
                            }
                        )
                    else:
                        if quote.GetItemData(-1, 2) == "2":
                            self.greeksputcallvol[quote.Symbol][
                                datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.GetItemValue("TradingHours")), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                            ] = {
                                "CallOI": iff(item.GetItemValue("CallOI")),
                                "PutOI": iff(item.GetItemValue("PutOI")),
                                "CallVol": iff(item.GetItemValue("CallVol")),
                                "PutVol": iff(item.GetItemValue("PutVol")),
                                "CKUpCnt": iff(item.GetItemValue("CKUpCnt")),
                                "CKUpVol": iff(item.GetItemValue("CKUpVol")),
                                "CKDnCnt": iff(item.GetItemValue("CKDnCnt")),
                                "CKDnVol": iff(item.GetItemValue("CKDnVol")),
                                "PKUpCnt": iff(item.GetItemValue("PKUpCnt")),
                                "PKUpVol": iff(item.GetItemValue("PKUpVol")),
                                "PKDnCnt": iff(item.GetItemValue("PKDnCnt")),
                                "PKDnVol": iff(item.GetItemValue("PKDnVol")),
                            }
                            self.voloievent.set()
                        else:
                            if quote.Symbol in self.greeksputcallvol:
                                if (
                                    datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.GetItemValue("TradingHours")), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                                    in self.greeksputcallvol[quote.Symbol]
                                ):
                                    oivol = self.greeksputcallvol[quote.Symbol][
                                        datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.GetItemValue("TradingHours")), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)
                                    ]
                            if "TC.F" in quote.Symbol  or ".mix" in quote.Symbol:
                                greekshis.append(
                                    {
                                        "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.GetItemValue("TradingHours")), "%Y%m%d %H%M%S").replace(tzinfo=self.tz)
                                        + timedelta(hours=8),
                                        "Symbol": quote.Symbol,
                                        "IVOut": iff(item.GetItemValue("IVOut")),
                                        "CTR": iff(item.GetItemValue("CTR"), 10000000000),
                                        "PTR": iff(item.GetItemValue("PTR"), 10000000000),
                                        "RCTR": iff(item.GetItemValue("RCTR"), 10000000000),
                                        "RPTR": iff(item.GetItemValue("RPTR"), 10000000000),
                                        "FCIV25": iff(item.GetItemValue("25FCIV"), 100000000),
                                        "FPIV25": iff(item.GetItemValue("25FPIV"), 100000000),
                                        "EvaVol": iff(item.GetItemValue("EvaVol"),100000000),
                                        # "ExtVal": iff(item.GetItemValue("ExtVal"),10000000000),
                                        "TV": iff(item.GetItemValue("TV"), 10000000000),
                                        "ATV": iff(item.GetItemValue("ATV"), 10000000000),
                                        "HV_W4": iff(item.GetItemValue("HV_W4"), 10000000000),
                                        "HV_W8": iff(item.GetItemValue("HV_W8"), 10000000000),
                                        "HV_W13": iff(item.GetItemValue("HV_W13"), 10000000000),
                                        "HV_W26": iff(item.GetItemValue("HV_W26"), 10000000000),
                                        "HV_W52": iff(item.GetItemValue("HV_W52"), 10000000000),
                                        "PutD": iff(item.GetItemValue("Putd"), 10000000000),
                                        "CallD": iff(item.GetItemValue("Calld"), 10000000000),
                                        "D25CStraddle": iff(item.GetItemValue("25DCStraddle"), 10000000000),
                                        "D25PStraddle": iff(item.GetItemValue("25DPStraddle"), 10000000000),
                                        "D25CTV": iff(item.GetItemValue("25DCTV"), 10000000000),
                                        "D25PTV": iff(item.GetItemValue("25DPTV"), 10000000000),
                                        "FIV": iff(item.GetItemValue("FIV"), 100000000),
                                        "IV": iff(item.GetItemValue("Volatility"), 100000000),
                                        "Straddle": iff(item.GetItemValue("Straddle"), 10000000000),
                                        "StraddleStrike": iff(item.GetItemValue("StraddleStrike"), 10000000000),
                                        "StraddleWeight": iff(item.GetItemValue("StraddleWeight"), 10000000000),
                                        "CIV25D": iff(item.GetItemValue("25DCIV"), 100000000),
                                        "PIV25D": iff(item.GetItemValue("25DPIV"), 100000000),
                                        "CIV10D": iff(item.GetItemValue("10DCIV"), 100000000),
                                        "PIV10D": iff(item.GetItemValue("10DPIV"), 100000000),
                                        "CallOI": oivol["CallOI"] if oivol else None,
                                        "PutOI": oivol["PutOI"] if oivol else None,
                                        "CallVol": oivol["CallVol"] if oivol else None,
                                        "PutVol": oivol["PutVol"] if oivol else None,
                                        "CKUpCnt": oivol["CKUpCnt"] if oivol else None,
                                        "CKUpVol": oivol["CKUpVol"] if oivol else None,
                                        "CKDnCnt": oivol["CKDnCnt"] if oivol else None,
                                        "CKDnVol": oivol["CKDnVol"] if oivol else None,
                                        "PKUpCnt": oivol["PKUpCnt"] if oivol else None,
                                        "PKUpVol": oivol["PKUpVol"] if oivol else None,
                                        "PKDnCnt": oivol["PKDnCnt"] if oivol else None,
                                        "PKDnVol": oivol["PKDnVol"] if oivol else None,
                                        "CallPutOIratio": oivol["CallOI"] / oivol["PutOI"] if oivol and oivol["CallOI"] and oivol["CallOI"] != 0 and oivol["PutOI"] and oivol["PutOI"] != 0 else None,
                                        "CallPutVolratio": oivol["CallVol"] / oivol["PutVol"] if oivol and oivol["CallVol"] and oivol["CallVol"] != 0 and oivol["PutVol"] and oivol["PutVol"] != 0 else None,
                                        "CSkew":iff(item.GetItemValue("CSkew"), 100000000),
                                        "PSkew":iff(item.GetItemValue("PSkew"), 100000000),
                                        # "CSkew": (
                                        #     item.GetItemValue("Calld") / item.GetItemValue("Volatility") * 100
                                        #     if item.GetItemValue("Calld") > -9999999999999999 and item.GetItemValue("Volatility") > -9999999999999999 and item.GetItemValue("Volatility") != 0
                                        #     else None
                                        # ),
                                        # "PSkew": (
                                        #     item.GetItemValue("Putd") / item.GetItemValue("Volatility") * 100
                                        #     if item.GetItemValue("Putd") > -9999999999999999 and item.GetItemValue("Volatility") > -9999999999999999 and item.GetItemValue("Volatility") != 0
                                        #     else None
                                        # ),
                                        "VIX": iff(item.GetItemValue("VIX"), 100000000),
                                        "CallDownPrice": iff(item.GetItemValue("CDP"), 10000000000),
                                        "CallDownMidPrice": iff(item.GetItemValue("CDMP"), 10000000000),
                                        "CallUpPrice": iff(item.GetItemValue("CUP"), 10000000000),
                                        "CallUpMidPrice": iff(item.GetItemValue("CUMP"), 10000000000),
                                        "PutDownPrice": iff(item.GetItemValue("PDP"), 10000000000),
                                        "PutDownMidPrice": iff(item.GetItemValue("PDMP"), 10000000000),
                                        "PutUpPrice": iff(item.GetItemValue("PUP"), 10000000000),
                                        "PutUpMidPrice": iff(item.GetItemValue("PUMP"), 10000000000),
                                    }
                                )
                            else:
                                greekshis.append(
                                    {
                                        "DateTime": datetime.strptime(str(item.Date) + " " + "{:0>6d}".format(item.GetItemValue("TradingHours")), "%Y%m%d %H%M%S").replace(tzinfo=self.tz)
                                        + timedelta(hours=8),
                                        "Symbol": quote.Symbol,
                                        "IV": iff(item.GetItemValue("Volatility"), 100000000),
                                        "VIX": iff(item.GetItemValue("VIX"), 100000000),
                                        "CallPutOIratio": oivol["CallOI"] / oivol["PutOI"] if oivol and oivol["CallOI"] != 0 and oivol["PutOI"] != 0 else None,
                                        "CallPutVolratio": oivol["CallVol"] / oivol["PutVol"] if oivol and oivol["CallVol"] != 0 and oivol["PutVol"] != 0 else None,
                                        "CallOI": oivol["CallOI"] if oivol else None,
                                        "PutOI": oivol["PutOI"] if oivol else None,
                                        "CallVol": oivol["CallVol"] if oivol else None,
                                        "PutVol": oivol["PutVol"] if oivol else None,
                                        "CKUpCnt": oivol["CKUpCnt"] if oivol else None,
                                        "CKUpVol": oivol["CKUpVol"] if oivol else None,
                                        "CKDnCnt": oivol["CKDnCnt"] if oivol else None,
                                        "CKDnVol": oivol["CKDnVol"] if oivol else None,
                                        "PKUpCnt": oivol["PKUpCnt"] if oivol else None,
                                        "PKUpVol": oivol["PKUpVol"] if oivol else None,
                                        "PKDnCnt": oivol["PKDnCnt"] if oivol else None,
                                        "PKDnVol": oivol["PKDnVol"] if oivol else None,
                                    }
                                )

            if quote.GetItemData(-1, 2) != "2":
                if quote.Symbol in self.greeksputcallvol:
                    del self.greeksputcallvol[quote.Symbol]
                self.ongreekshistory(DataType, quote.Symbol, quote.StartTime, quote.EndTime, greekshis)
            self.quoteapi.unsubquote(DataType, quote.Symbol, quote.StartTime, quote.EndTime, quote.GetItemData(-1, 2))

    def OnQuoteDataSyn(self, SymbolType, DataType, QuoteData, bstrModifiedFields):
        quote = self._Dispatch(QuoteData)
        if DataType == 1 and SymbolType != 8:  # 实时
            temp = {
                "DateTime": datetime.strptime(str(quote.TradeDate) + " " + "{:0>6d}".format(quote.FilledTime), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                "TradeDate": quote.GetValueFromIndex(101),
                "Time": quote.FilledTime,
                "Symbol": quote.Symbol,
                "Open": iff(quote.OpeningPrice, 10000000000),
                "High": iff(quote.HighPrice, 10000000000),
                "Low": iff(quote.LowPrice, 10000000000),
                "Last": iff(quote.TradingPrice, 10000000000),
                "LowerLimit": iff(quote.LowerLimitPrice, 10000000000),
                "UpperLimit": iff(quote.UpperLimitPrice, 10000000000),
                "Quantity": quote.TradeQuantity if quote.TradeQuantity != -9223372036854775808 else 0,
                "Volume": quote.TradeVolume if quote.TradeVolume != -9223372036854775808 else 0,
                "Turnover": iff(quote.GetValueFromIndex(7)),
                "Ask": iff(quote.Ask, 10000000000),
                "Ask1": iff(quote.Ask1, 10000000000),
                "Ask2": iff(quote.Ask2, 10000000000),
                "Ask3": iff(quote.Ask3, 10000000000),
                "Ask4": iff(quote.Ask4, 10000000000),
                "Ask5": iff(quote.Ask5, 10000000000),
                "Ask6": iff(quote.Ask6, 10000000000),
                "Ask7": iff(quote.Ask7, 10000000000),
                "Ask8": iff(quote.Ask8, 10000000000),
                "Ask9": iff(quote.Ask9, 10000000000),
                "AskVolume": iff(quote.AskVolume),
                "AskVolume1": iff(quote.AskVolume1),
                "AskVolume2": iff(quote.AskVolume2),
                "AskVolume3": iff(quote.AskVolume3),
                "AskVolume4": iff(quote.AskVolume4),
                "AskVolume5": iff(quote.AskVolume5),
                "AskVolume6": iff(quote.AskVolume6),
                "AskVolume7": iff(quote.AskVolume7),
                "AskVolume8": iff(quote.AskVolume8),
                "AskVolume9": iff(quote.AskVolume9),
                "Bid": iff(quote.Bid, 10000000000),
                "Bid1": iff(quote.Bid1, 10000000000),
                "Bid2": iff(quote.Bid2, 10000000000),
                "Bid3": iff(quote.Bid3, 10000000000),
                "Bid4": iff(quote.Bid4, 10000000000),
                "Bid5": iff(quote.Bid5, 10000000000),
                "Bid6": iff(quote.Bid6, 10000000000),
                "Bid7": iff(quote.Bid7, 10000000000),
                "Bid8": iff(quote.Bid8, 10000000000),
                "Bid9": iff(quote.Bid9, 10000000000),
                "BidVolume": iff(quote.BidVolume),
                "BidVolume1": iff(quote.BidVolume1),
                "BidVolume2": iff(quote.BidVolume2),
                "BidVolume3": iff(quote.BidVolume3),
                "BidVolume4": iff(quote.BidVolume4),
                "BidVolume5": iff(quote.BidVolume5),
                "BidVolume6": iff(quote.BidVolume6),
                "BidVolume7": iff(quote.BidVolume7),
                "BidVolume8": iff(quote.BidVolume8),
                "BidVolume9": iff(quote.BidVolume9),
                "Change": iff(quote.Change, 10000000000),
                "OpenTime": quote.OpenTime,
                "CloseTime": quote.CloseTime,
                "Exchange": quote.Exchange,
                "ExchangeName": quote.ExchangeName,
                # "PreciseTime":quote.PreciseTime,
                "ReferencePrice": iff(quote.ReferencePrice, 10000000000),
                "Security": quote.Security,
                "SecurityName": quote.SecurityName,
                "TotalAskCount": quote.TotalAskCount,
                "TotalAskVolume": quote.TotalAskVolume,
                "TotalBidCount": quote.TotalBidCount,
                "TotalBidVolume": quote.TotalBidVolume,
                "YClosedPrice": iff(quote.YClosedPrice, 10000000000),
                "YTradeVolume": iff(quote.YTradeVolume),
                "InstrumentStatus": quote.GetValueFromIndex(121),
            }  # 开市：0  闭市：4  集合竞价：5   非交易时段：9
            temp["adjust"] = quote.GetValueFromIndex(250) / 10000000000 if quote.GetValueFromIndex(250) > 0 else None
            if SymbolType == 1:  # 证
                temp["SimMatchPrice"] = iff(quote.GetValueFromIndex(122), 10000000000)
                temp["SimMatchvol"] = iff(quote.GetValueFromIndex(123))
                temp["SimMatchchg"] = iff(quote.GetValueFromIndex(124), 10000000000)
                temp["BreakRefPrice"] = iff(quote.GetValueFromIndex(145), 10000000000)
                temp["BreakCountdown"] = iff(quote.GetValueFromIndex(252))
            elif SymbolType == 2:  # 期货
                temp["OpenInterest"] = quote.OpenInterest if quote.OpenInterest != -9223372036854775808 else 0
                temp["YOpenInterest"] = quote.YOpenInterest if quote.YOpenInterest != -9223372036854775808 else 0
                temp["OpenDate"] = iff(quote.BeginDate)
                temp["ExpireDate"] = iff(quote.EndDate)
                temp["ExpiryDays"] = iff(quote.ExpiryDate)
                temp["Month"] = quote.Month
                temp["SellCount"] = quote.SellCount
                temp["Settlement"] = iff(quote.SettlementPrice, 10000000000)
                temp["ClosingPrice"] = iff(quote.ClosingPrice, 10000000000)
                temp["FlagOfBuySell"] = quote.FlagOfBuySell
                temp["SellVolume"] = quote.GetValueFromIndex(116)
                temp["BuyVolume"] = quote.GetValueFromIndex(117)
                temp["SellQuantity"] = quote.GetValueFromIndex(107)
                temp["BuyQuantity"] = quote.GetValueFromIndex(108)
            elif SymbolType == 3:  # 期权
                temp["OpenInterest"] = quote.OpenInterest if quote.OpenInterest != -9223372036854775808 else 0
                temp["YOpenInterest"] = quote.YOpenInterest if quote.YOpenInterest != -9223372036854775808 else 0
                temp["OpenDate"] = iff(quote.BeginDate)
                temp["ExpireDate"] = iff(quote.EndDate)
                temp["Month"] = quote.Month
                temp["SellCount"] = quote.SellCount
                temp["Settlement"] = iff(quote.SettlementPrice, 10000000000)
                temp["ClosingPrice"] = iff(quote.ClosingPrice)
                temp["CallPut"] = quote.CallPut
                temp["Future"] = quote.Future
                temp["StrikePrice"] = iff(quote.StrikePrice, 10000000000)
                temp["TradeSymbol"] = quote.TradeSymbol
                temp["Underlying"] = quote.Underlying
                temp["SimMatchPrice"] = iff(quote.GetValueFromIndex(122), 10000000000)
                temp["SimMatchvol"] = iff(quote.GetValueFromIndex(123))
                temp["SimMatchchg"] = iff(quote.GetValueFromIndex(124), 10000000000)
                temp["BreakRefPrice"] = iff(quote.GetValueFromIndex(145), 10000000000)
                temp["BreakCountDown"] = iff(quote.GetValueFromIndex(252))

            if quote.Symbol in self.subquotetopic:
                self.onquotereal(DataType, quote.Symbol, temp)
            if quote.Symbol + "/Q" in self.subquotetopic:
                temp["Symbol"] = quote.Symbol + "/Q"
                self.onquotereal(DataType, quote.Symbol + "/Q", temp)
            if quote.Symbol + "/H" in self.subquotetopic:
                if temp["adjust"] is None:
                    return
                temp["Symbol"] = quote.Symbol + "/H"
                temp["Ask"] = float(Decimal(temp["Ask"] * temp["adjust"]).quantize(Decimal(str(temp["Ask"]))))
                temp["Bid"] = float(Decimal(temp["Bid"] * temp["adjust"]).quantize(Decimal(str(temp["Bid"]))))
                temp["Open"] = float(Decimal(temp["Open"] * temp["adjust"]).quantize(Decimal(str(temp["Open"]))))
                temp["High"] = float(Decimal(temp["High"] * temp["adjust"]).quantize(Decimal(str(temp["High"]))))
                temp["Low"] = float(Decimal(temp["Low"] * temp["adjust"]).quantize(Decimal(str(temp["Low"]))))
                temp["Last"] = float(Decimal(temp["Last"] * temp["adjust"]).quantize(Decimal(str(temp["Last"]))))
                self.onquotereal(DataType, quote.Symbol + "/H", temp)

        elif DataType == 1 and SymbolType == 8:  # ATM symbol
            atm_0 = quote.GetStringData("ATM0_STK")
            atm_1C = quote.GetStringData("ATM+1C_Symbol")
            atm_1P = quote.GetStringData("ATM-1P_Symbol")
            optlist = quote.GetStringData("STKLIST")
            if self.quoteapi.debuglevel and (not atm_0 or not atm_1C or not atm_1P or not optlist):
                self.quoteapi.writelog("subquote:{0},{1},{2},{3}".format(atm_0, atm_1C, atm_1P, optlist))
            if atm_1C and atm_1P and optlist:
                self.onATM(
                    DataType, quote.GetStringData("Symbol"), {"Symbol": quote.GetStringData("Symbol"), "ATM": atm_0, "OTM-1C": atm_1C, "OTM-1P": atm_1P, "OPTLIST": (optlist.strip("|").split("|"))}
                )
        elif DataType == 6:  # 实时Greeks
            if "TC.F" in quote.Symbol or ".mix" in quote.Symbol:
                self.ongreeksreal(
                    DataType,
                    quote.Symbol,
                    {
                        "DateTime": datetime.strptime(str(quote.TradingDay) + " " + "{:0>6d}".format(quote.TradingHours), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                        "Time": quote.TradingHours,
                        "Symbol": quote.Symbol,
                        "IVOut": iff(quote.GetGreeksValue("IVOut")),
                        "CalendarDays": iff(quote.GetGreeksValue("CalendarDays")),
                        "TradingDays": iff(quote.GetGreeksValue("TDate")),
                        "AnnualTradeday": iff(quote.GetGreeksValue("TDTime"), 10000000000),
                        "AnnualCalendarDay": iff(quote.GetGreeksValue("DTime"), 10000000000),
                        "CTR": iff(quote.GetGreeksValue("CTR"), 10000000000),
                        "YCTR": iff(quote.GetGreeksValue("YCTR"), 10000000000),
                        "PTR": iff(quote.GetGreeksValue("PTR"), 10000000000),
                        "YPTR": iff(quote.GetGreeksValue("YPTR"), 10000000000),
                        "RCTR": iff(quote.GetGreeksValue("RCTR"), 10000000000),
                        "RPTR": iff(quote.GetGreeksValue("RPTR"), 10000000000),
                        "YRCTR": iff(quote.GetGreeksValue("YRCTR"), 10000000000),
                        "YRPTR": iff(quote.GetGreeksValue("YRPTR"), 10000000000),
                        "FCIV25": iff(quote.GetGreeksValue("25FCIV"), 100000000),
                        "FPIV25": iff(quote.GetGreeksValue("25FPIV"), 100000000),
                        "YFCIV25": iff(quote.GetGreeksValue("25FYdCIV"), 100000000),
                        "YFPIV25": iff(quote.GetGreeksValue("25FYdPIV"), 100000000),
                        "ExtVal": iff(quote.ExtVal, 10000000000),
                        "TheoVal": iff(quote.GetGreeksValue("TheoVal"), 10000000000),
                        "IntVal": iff(quote.GetGreeksValue("IntVal"), 10000000000),
                        "TV": iff(quote.GetGreeksValue("TV"), 10000000000),
                        "ATV": iff(quote.GetGreeksValue("ATV"), 10000000000),
                        "YTV": iff(quote.GetGreeksValue("YTV"), 10000000000),
                        "YATV": iff(quote.GetGreeksValue("YATV"), 10000000000),
                        "HV_W4": iff(quote.HV_W4, 10000000000),
                        "HV_W8": iff(quote.HV_W8, 10000000000),
                        "HV_W13": iff(quote.HV_W13, 10000000000),
                        "HV_W26": iff(quote.HV_W26, 10000000000),
                        "HV_W52": iff(quote.HV_W52, 10000000000),
                        "PutD": iff(quote.GetGreeksValue("Putd"), 10000000000),
                        "CallD": iff(quote.GetGreeksValue("Calld"), 10000000000),
                        "D25CStraddle": iff(quote.GetGreeksValue("25DCStraddle"), 10000000000),
                        "D25PStraddle": iff(quote.GetGreeksValue("25DPStraddle"), 10000000000),
                        "D25CTV": iff(quote.GetGreeksValue("25DCTV"), 10000000000),
                        "D25PTV": iff(quote.GetGreeksValue("25DPTV"), 10000000000),
                        "YPutD": iff(quote.GetGreeksValue("YPutd"), 10000000000),
                        "YCallD": iff(quote.GetGreeksValue("YCalld"), 10000000000),
                        "FIV": iff(quote.GetGreeksValue("FIV"), 100000000),
                        "YFIV": iff(quote.GetGreeksValue("YFIV"), 100000000),
                        "EvaVol": iff(quote.GetGreeksValue("EvaVol"), 10000000000),
                        "IV": iff(quote.GetGreeksValue("Volatility"), 100000000),
                        "PreIV": iff(quote.PreImpVol, 100000000),
                        "Straddle": iff(quote.GetGreeksValue("Straddle"), 10000000000),
                        "YStraddle": iff(quote.GetGreeksValue("YStraddle"), 10000000000),
                        "StraddleStrike": iff(quote.GetGreeksValue("StraddleStrike"), 10000000000),
                        "StraddleWeight": iff(quote.GetGreeksValue("StraddleWeight")),
                        "CIV25D": iff(quote.GetGreeksValue("25DCIV"), 100000000),
                        "PIV25D": iff(quote.GetGreeksValue("25DPIV"), 100000000),
                        "CIV10D": iff(quote.GetGreeksValue("10DCIV"), 100000000),
                        "PIV10D": iff(quote.GetGreeksValue("10DPIV"), 100000000),
                        "YCIV25D": iff(quote.GetGreeksValue("25DYdCIV"), 100000000),
                        "YPIV25D": iff(quote.GetGreeksValue("25DYdPIV"), 100000000),
                        "YCIV10D": iff(quote.GetGreeksValue("10DYdCIV"), 100000000),
                        "YPIV10D": iff(quote.GetGreeksValue("10DYdPIV"), 100000000),
                        "VIX": iff(quote.VIX, 10000000000),
                        "CallPutOIratio": (
                            quote.GetGreeksValue("CallOI") / quote.GetGreeksValue("PutOI")
                            if quote.GetGreeksValue("CallOI") and quote.GetGreeksValue("PutOI") and quote.GetGreeksValue("CallOI") != 0 and quote.GetGreeksValue("PutOI") != 0
                            else None
                        ),
                        "CallPutVolratio": (
                            quote.GetGreeksValue("CallVol") / quote.GetGreeksValue("PutVol")
                            if quote.GetGreeksValue("CallVol") and quote.GetGreeksValue("PutVol") and quote.GetGreeksValue("CallVol") != 0 and quote.GetGreeksValue("PutVol") != 0
                            else None
                        ),
                        "CallOI": iff(quote.GetGreeksValue("CallOI")),
                        "YCallOI": iff(quote.GetGreeksValue("YCallOI")),
                        "CallVol": iff(quote.GetGreeksValue("CallVol")),
                        "YCallVol": iff(quote.GetGreeksValue("YCallVol")),
                        "PutOI": iff(quote.GetGreeksValue("PutOI")),
                        "YPutOI": iff(quote.GetGreeksValue("YPutOI")),
                        "PutVol": iff(quote.GetGreeksValue("PutVol")),
                        "YPutVol": iff(quote.GetGreeksValue("YPutVol")),
                        "CKUpCnt": iff(quote.GetGreeksValue("CKUpCnt")),
                        "CKUpVol": iff(quote.GetGreeksValue("CKUpVol")),
                        "CKDnCnt": iff(quote.GetGreeksValue("CKDnCnt")),
                        "CKDnVol": iff(quote.GetGreeksValue("CKDnVol")),
                        "PKUpCnt": iff(quote.GetGreeksValue("PKUpCnt")),
                        "PKUpVol": iff(quote.GetGreeksValue("PKUpVol")),
                        "PKDnCnt": iff(quote.GetGreeksValue("PKDnCnt")),
                        "PKDnVol": iff(quote.GetGreeksValue("PKDnVol")),
                        "CSkew": (
                            quote.GetGreeksValue("Calld") / quote.GetGreeksValue("Volatility") * 100
                            if quote.GetGreeksValue("Calld") > -9999999999999999 and quote.GetGreeksValue("Volatility") > -9999999999999999 and quote.GetGreeksValue("Volatility") != 0
                            else None
                        ),
                        "PSkew": (
                            quote.GetGreeksValue("Putd") / quote.GetGreeksValue("Volatility") * 100
                            if quote.GetGreeksValue("Putd") > -9999999999999999 and quote.GetGreeksValue("Volatility") > -9999999999999999 and quote.GetGreeksValue("Volatility") != 0
                            else None
                        ),
                    },
                )
            elif "TC.S" in quote.Symbol:
                self.ongreeksreal(
                    DataType,
                    quote.Symbol,
                    {
                        "DateTime": datetime.strptime(str(quote.TradingDay) + " " + "{:0>6d}".format(quote.TradingHours), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                        "Time": quote.GetGreeksValue("TradingHours"),
                        "Symbol": quote.Symbol,
                        "IV": iff(quote.GetGreeksValue("Volatility"), 100000000),
                        "PreIV": iff(quote.PreImpVol, 10000000000),
                        "VIX": iff(quote.PreImpVol, 100000000),
                        "CallPutOIratio": (
                            quote.GetGreeksValue("CallOI") / quote.GetGreeksValue("PutOI")
                            if quote.GetGreeksValue("CallOI") and quote.GetGreeksValue("PutOI") and quote.GetGreeksValue("CallOI") != 0 and quote.GetGreeksValue("PutOI") != 0
                            else None
                        ),
                        "CallPutVolratio": (
                            quote.GetGreeksValue("CallVol") / quote.GetGreeksValue("PutVol")
                            if quote.GetGreeksValue("CallVol") and quote.GetGreeksValue("PutVol") and quote.GetGreeksValue("CallVol") != 0 and quote.GetGreeksValue("PutVol") != 0
                            else None
                        ),
                        "CallOI": iff(quote.GetGreeksValue("CallOI")),
                        "YCallOI": iff(quote.GetGreeksValue("YCallOI")),
                        "CallVol": iff(quote.GetGreeksValue("CallVol")),
                        "YCallVol": iff(quote.GetGreeksValue("YCallVol")),
                        "PutOI": iff(quote.GetGreeksValue("PutOI")),
                        "YPutOI": iff(quote.GetGreeksValue("YPutOI")),
                        "PutVol": iff(quote.GetGreeksValue("PutVol")),
                        "YPutVol": iff(quote.GetGreeksValue("YPutVol")),
                        "CKUpCnt": iff(quote.GetGreeksValue("CKUpCnt")),
                        "CKUpVol": iff(quote.GetGreeksValue("CKUpVol")),
                        "CKDnCnt": iff(quote.GetGreeksValue("CKDnCnt")),
                        "CKDnVol": iff(quote.GetGreeksValue("CKDnVol")),
                        "PKUpCnt": iff(quote.GetGreeksValue("PKUpCnt")),
                        "PKUpVol": iff(quote.GetGreeksValue("PKUpVol")),
                        "PKDnCnt": iff(quote.GetGreeksValue("PKDnCnt")),
                        "PKDnVol": iff(quote.GetGreeksValue("PKDnVol")),
                    },
                )
            else:
                self.ongreeksreal(
                    DataType,
                    quote.Symbol,
                    {
                        "DateTime": datetime.strptime(str(quote.TradingDay) + " " + "{:0>6d}".format(quote.TradingHours), "%Y%m%d %H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8),
                        "Time": quote.GetGreeksValue("TradingHours"),
                        "Symbol": quote.Symbol,
                        "CalendarDays": quote.GetGreeksValue("CalendarDays"),
                        "TradingDays": quote.GetGreeksValue("TDate"),
                        "AnnualTradeday": iff(quote.GetGreeksValue("TDTime"), 10000000000),
                        "AnnualCalendarDay": iff(quote.GetGreeksValue("DTime"), 10000000000),
                        "Ask": iff(quote.Ask, 10000000000),
                        "Bid": iff(quote.Bid, 10000000000),
                        "Mid": iff(quote.GetGreeksValue("Mid"), 10000000000),
                        "MIV": iff(quote.GetGreeksValue("MIV"), 10000000000),
                        "Delta": iff(quote.GetGreeksValue("Delta"), 1000000000000),
                        "ExtVal": iff(quote.GetGreeksValue("ExtVal"), 10000000000),
                        "TV": iff(quote.GetGreeksValue("TV"), 10000000000),
                        "ATV": iff(quote.GetGreeksValue("ATV"), 10000000000),
                        "YTV": iff(quote.GetGreeksValue("YTV"), 10000000000),
                        "YATV": iff(quote.GetGreeksValue("YATV"), 10000000000),
                        "BTV": iff(quote.GetGreeksValue("BidTV"), 10000000000),
                        "STV": iff(quote.GetGreeksValue("AskTV"), 10000000000),
                        "Gamma": iff(quote.GetGreeksValue("Gamma"), 10000000000),
                        "EvaVol": iff(quote.GetGreeksValue("EvaVol"), 10000000000),
                        "SkewDelta": iff(quote.GetGreeksValue("SkewDelta"), 1000000000000),
                        "IV": iff(quote.GetGreeksValue("ImpVol"), 10000000000),
                        "PreIV": iff(quote.GetGreeksValue("PreImpVol"), 10000000000),
                        "IntVal": iff(quote.GetGreeksValue("IntVal"), 10000000000),
                        "Rho": iff(quote.GetGreeksValue("Rho"), 10000000000),
                        "BIV": iff(quote.BIV, 10000000000),
                        "BIV2": iff(quote.GetGreeksValue("BIV2"), 10000000000),
                        "BIV3": iff(quote.GetGreeksValue("BIV3"), 10000000000),
                        "BIV4": iff(quote.GetGreeksValue("BIV4"), 10000000000),
                        "BIV5": iff(quote.GetGreeksValue("BIV5"), 10000000000),
                        "AIV": iff(quote.SIV, 10000000000),
                        "AIV2": iff(quote.GetGreeksValue("SIV2"), 10000000000),
                        "AIV3": iff(quote.GetGreeksValue("SIV3"), 10000000000),
                        "AIV4": iff(quote.GetGreeksValue("SIV4"), 10000000000),
                        "AIV5": iff(quote.GetGreeksValue("SIV5"), 10000000000),
                        "TheoVal": iff(quote.GetGreeksValue("TheoVal"), 10000000000),
                        "Theta": iff(quote.GetGreeksValue("Theta"), 10000000000),
                        "Vega": iff(quote.GetGreeksValue("Vega"), 10000000000),
                        "CPIV": iff(quote.GetGreeksValue("CPIV"), 10000000000),
                        "LR": iff(quote.GetGreeksValue("LR"), 10000000000),
                        "RealLR": iff(quote.GetGreeksValue("RealLR"), 10000000000),
                        "OPR": iff(quote.GetGreeksValue("OPR"), 10000000000),
                        "ROI": iff(quote.GetGreeksValue("ROI"), 10000000000),
                        "BER": iff(quote.GetGreeksValue("BER"), 10000000000),
                        "Charm": iff(quote.GetGreeksValue("Charm"), 10000000000),
                        "Vanna": iff(quote.GetGreeksValue("Vanna"), 10000000000),
                        "Vomma": iff(quote.GetGreeksValue("Vomma"), 100000000),
                        "Speed": iff(quote.GetGreeksValue("Speed"), 10000000000),
                        "Zomma": iff(quote.GetGreeksValue("Zomma"), 10000000000),
                    },
                )

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
                                            syblist["InstrumentID"].append(self.quoteapi.getsymbol_id(symb))
                                            syblist["ExpirationDate"].append(self.quoteapi.getexpirationdate(symb))
                                            syblist["TradeingDays"].append(self.quoteapi.gettradeingdays(symb))
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
                                        optlist["InstrumentID"].append(self.quoteapi.getsymbol_id(symb))
                                        optlist["ExpirationDate"].append(self.quoteapi.getexpirationdate(symb))
        self.onsymbolhistory(strParam.replace("History-", ""), lParam, sym)
        self.quoteapi.topicunsub("ICECREAM.RETURN")

    def OnServerTimeDiff(self, TimeDiff):
        self.ontimediff(TimeDiff)

    def OnSymbolClassificationsUpdate(self):
        self.symbollistready = True

    def OnHotMonthUpdate(self):
        self.hotmonthready = True

    def OnSymbolLookupUpdate(self):
        self.symblookready = True

    def OnInstrumentInfoUpdate(self):
        self.symbinfoready = True
    def OnStatusInfoUpdate(self,bstrType,Status):
        if bstrType=="Quote":
            if Status==1:
                self.quotestatus=True
            else:
                self.quotestatus=False
        if bstrType=="DCORE":
            if Status==1:
                self.dcorestatus=True
            else:
                self.dcorestatus=False

class QuoteClass:
    def __init__(self, extendevent, dllpath, debugmode=None):
        POINTER(automation.IDispatch).__ctypes_from_outparam__ = wrap_outparam  # type: ignore
        self.connresult=None
        self.extendclass = extendevent
        self.apppath = dllpath
        apidll = ""

        if platform.architecture()[0] == "64bit":
            apidll = dllpath + "/TCoreRelease/Components/TCQuoteWrapperAPI64.dll"
        else:
            apidll = dllpath + "/TCoreRelease/Components/TCQuoteWrapperAPI.dll"
        self.mod = GetModule(apidll)
        self.dll = oledll.LoadLibrary(apidll)
        self.eventobj = BaseEvents()
        self.interface = self.mod._ITCQuoteAPIExEvents
        clsid = self.mod.TCQuoteAPIEx._reg_clsid_
        pquotefac = self.mod.ITCQuoteAPIEx
        self.pquote = self.createDispatch(clsid, pquotefac)
        self.tz = pytz.timezone("Etc/GMT+8")
        self.debuglevel = debugmode

    def get_fileversion(self, filename):
        parser = CreateObject("Scripting.FileSystemObject")
        version = parser.GetFileVersion(filename)
        return version

    def createDispatch(self, clsid, modulefactpry):
        interface = POINTER(IClassFactory)()
        self.dll.DllGetClassObject(byref(clsid), byref(GUID("{00000001-0000-0000-C000-000000000046}")), byref(interface))
        disp = interface.CreateInstance(POINTER(modulefactpry)(), modulefactpry)
        return disp

    # 注册事件
    def connect(self, appid: str, servicekey: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            self.eventobj.quoteapi = self
            self.eventobj.extendevent = self.extendclass
            self.connresult=GetEvents(self.pquote,self.eventobj,self.interface)
            self.pquote.Connect(".", appid, servicekey, 1)
            self.setsubscriptionlevel(1)

    def setsubscriptionlevel(self, Level):
        try:
            return self.pquote.SetSubscriptionLevel(Level)
        except COMError as e:
            print("setsubscriptionlevel:", e)
            if self.debuglevel:
                self.writelog("setsubscriptionlevel:{0}".format(Level))

    def disconnect(self):
        try:
            self.pquote.Disconnect()
            CoUninitialize()
        except COMError as e:
            print("连接错误:", e)

    def subquote(self, datatype: int, symbol: str, startime: int, endtime: int):  # "-1" :超過上限 "-10" 無報價權限
        if "TC.O" in symbol:
            greeksType = "REAL"
        else:
            greeksType = "Volatility"
        if datatype != 6:
            greeksType = ""
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                clsid = self.mod.DataParameters._reg_clsid_
                subquotefac = self.mod.pDataParameters
                arg = self.createDispatch(clsid, subquotefac)
                arg.Symbol = symbol
                arg.SecurityType = 9
                arg.StartTime = startime
                arg.EndTime = endtime
                arg.GreeksType = greeksType
                if (datatype == 9 or datatype == 10 or datatype == 19 or datatype == 820 or datatype == 800) and ("TC.F" in symbol or "TC.S" in symbol or ".mix" in symbol):
                    arg.ExtParam = "ExtendGreeks=2;"
                    re = self.pquote.SubQuote(datatype, arg)
                    if re and re.find("-") == 0 and self.debuglevel:
                        self.writelog("subquote:{0},{1},{2},{3},{4}".format(datatype, symbol, startime, endtime, re))
                    if self.eventobj.voloievent.is_set():
                        self.eventobj.voloievent.clear()
                    self.eventobj.voloievent.wait(5)
                arg.ExtParam = "ExtendGreeks=0;"
                re = self.pquote.SubQuote(datatype, arg)
                if re and re.find("-") == 0 and self.debuglevel:
                    self.writelog("subquote:{0},{1},{2},{3},{4}".format(datatype, symbol, startime, endtime, re))
                if re == "-1":
                    print("订阅超过上限", symbol)
                elif re == "-10":
                    print("无报价权限", symbol)
                return re
            except COMError as e:
                if self.debuglevel:
                    self.writelog("subquote:{0},{1},{2},{3},{4}".format(datatype, symbol, startime, endtime, e.details))
                print("订阅错误：", e)

    def unsubquote(self, datatype: int, symbol: str, startime: int, endtime: int, ExtendGreeks="0"):
        if "TC.O" in symbol:
            greeksType = "REAL"
        else:
            greeksType = "Volatility"
        if datatype != 6:
            greeksType = ""
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                clsid = self.mod.DataParameters._reg_clsid_
                subquotefac = self.mod.pDataParameters
                arg = self.createDispatch(clsid, subquotefac)
                arg.Symbol = symbol
                arg.SecurityType = 9
                arg.StartTime = startime
                arg.EndTime = endtime
                arg.GreeksType = greeksType
                arg.ExtParam = "ExtendGreeks=" + ExtendGreeks + ";"
                return self.pquote.UnsubQuote(datatype, arg)
            except COMError as e:
                print("订阅错误：", e)

    def getexpirationdate(self, symbol: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                expirationdate = self.pquote.GetExpirationDate(symbol)
                if self.debuglevel and not expirationdate:
                    self.writelog("getexpirationdate为空:{0}".format(symbol))
                return expirationdate
            except Exception as e:
                if self.debuglevel:
                    self.writelog("getexpirationdate:{0},{1}".format(symbol, e))
                print("getexpirationDate错误:", e)
    def getexpirationex(self,ltype,symbol, strdate="", strtime=""):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                expirationdate = self.pquote.GetExpireDateTimeSpan(ltype,symbol,strdate, strtime)
                if self.debuglevel and not expirationdate:
                    self.writelog("getexpirationex为空:{0}".format(symbol))
                return expirationdate
            except Exception as e:
                if self.debuglevel:
                    self.writelog("getexpirationex:{0},{1}".format(symbol, e))
                print("getexpirationex错误:", e)
    # 获取剩余交易日
    def gettradeingdays(self, symbol: str):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                lEndDate = self.getexpirationdate(symbol)
                if lEndDate:
                    return self.pquote.GetTradeingDays(symbol, int(lEndDate))
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
                tradingdate = self.pquote.GetTradeingDate(symbol, int(startDate), int(endDate))
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
                    strhot = self.pquote.GetHotMonthByDateTime(symbol, str(strdate), str(strtime))
                    if self.debuglevel and not strhot:
                        self.writelog("gethotmonth为空:{0},{1},{2}".format(symbol, strdate, strtime))
                    hot = strhot.split("~")[0].split(":")
                    temp[datetime.strptime(str(hot[1]), "%Y%m%d%H%M%S").replace(tzinfo=self.tz) + timedelta(hours=8)] = hot[0]
                    return temp
                else:
                    self.pquote.GetHotMonthByDateTime(symbol, str(strdate), str(strtime))
                    symbsplit=symbol.split(".")
                    with open("C:\\ProgramData\\TCore\\HotChange\\" + symbol + ".txt", "r+") as symblist:
                        for count, line in enumerate(symblist):
                            if count != 0:
                                linedata = line.split("->")
                                temp[
                                    datetime.strptime(linedata[0] + " " + self.getsymbol_session(symbol).split(";")[-1].split("~")[-1], "%Y%m%d %H:%M").replace(tzinfo=self.tz)
                                    + timedelta(hours=8)
                                    + timedelta(seconds=1)
                                ] = symbol.replace(symbsplit[4], str(linedata[1].strip("\n")))
                                # symbsplit[0]+"."+symbsplit[1]+"."+symbsplit[2]+"."+symbsplit[3]+"."+str(linedata[1].strip("\n"))
                    return temp
            except COMError as e:
                if self.debuglevel:
                    self.writelog("gethotmonth:{0},{1},{2},{3}".format(symbol, strdate, strtime, e.details))
                print("gethotmonth错误:", e)

    def getsymbol_ticksize(self, symbol: str):
        return self._getsymbolInfo("2", symbol)

    def getsymbol_session(self, symbol: str):
        return self._getsymbolInfo("3", symbol)

    def getsymbolvolume_multiple(self, symbol: str):
        return self._getsymbolInfo("6", symbol)
    
    def getlistingdate(self, symbol: str):
        return self._getsymbolInfo("ListedDate", symbol)
    
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
                return self.pquote.GetInstrumentInfo(strType, symbol)
            except Exception as e:
                if self.debuglevel:
                    self.writelog("GetInstrumentInfo:{0},{1},{2}".format(strType, symbol, e))
                print("getsymbolInfo错误:", e)

    def getsymbolname(self, Keyword):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.GetSymbolName(Keyword)
            except COMError as e:
                if self.debuglevel:
                    self.writelog("getsymbolname:{0},{1}".format(Keyword, e.details))
                print("getsymbolName错误:", e)

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

    def subsymbolhistory(self, symboltype: str, dt: str):
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

    def __getsymbollist(self, Classify, Exchange, Symbol, Month, CallPut):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                re = self.pquote.GetSymbolClassifications(Classify, Exchange, Symbol, Month, CallPut)
                if self.debuglevel and not re:
                    self.writelog("GetSymbolClassifications为空:{0},{1},{2},{3},{4}".format(Classify, Exchange, Symbol, Month, CallPut))
                return re
            except COMError as e:
                print("getsymbol错误:", e)

    def symbollookup(self, SymbolType, Keyword):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                re = self.pquote.SymbolLookup(SymbolType, Keyword)
                if self.debuglevel and not re:
                    self.writelog("symbollookup为空:{0},{1}".format(SymbolType, Keyword))
                return re
            except COMError as e:
                print("symbollookup错误:", e)

    def isholiday(self, bstrDate, bstrSymbol):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.isHoliday(bstrDate, bstrSymbol)
            except COMError as e:
                print("isholiday错误:", e)

    def isunderlying(self, bstrSymbol):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.isUnderlying(bstrSymbol)
            except COMError as e:
                print("isunderlying错误:", e)

    def topicpublish(self, strTopic, lParam, strParam, pvParam):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.TopicPublish(strTopic, lParam, strParam, pvParam)
            except COMError as e:
                print("topicpublish错误:", e)

    def topicsub(self, strTopic):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.TopicSub(strTopic)
            except COMError as e:
                print("topicsub错误:", e)

    def topicunsub(self, strTopic):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.TopicUnsub(strTopic)
            except COMError as e:
                print("topicunsub错误:", e)

    def getgeneralservice(self, Key):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.GetGeneralService(Key)
            except COMError as e:
                print("getgeneralservice错误:", e)

    def writelog(self, strlog):
        try:
            CoInitializeEx(COINIT_MULTITHREADED)
        finally:
            try:
                return self.pquote.DoSomething(1, 0, strlog, None)
            except COMError as e:
                print("writelog:", e)

    def join(self):
        run()

    #     pythoncom.PumpMessages()
