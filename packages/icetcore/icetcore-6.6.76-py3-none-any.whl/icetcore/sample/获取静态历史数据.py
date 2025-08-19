import time
from icetcore import TCoreAPI, BarType, GreeksType
import pandas as pd


api = TCoreAPI(apppath="C:/AlgoMaster2/APPs64")  #
re = api.connect()  # (appid="AlgoMaster")
time.sleep(1)

# 获取greeks line历史数据
print(pd.DataFrame(api.getgreekshistory(GreeksType.DOGSK, 1, "TC.F.U_SSE.510050.202302", "2023013101", "2023013107")))

# 获取bar历史数据
print(pd.DataFrame(api.getquotehistory(BarType.MINUTE, 5, "TC.F.CFFEX.T.HOT", "2022120101", "2023013107")))
print(pd.DataFrame(api.getquotehistory(BarType.MINUTE, 5, "TC.F.SHFE.rb.HOT", "2022120101", "2023013107")))
