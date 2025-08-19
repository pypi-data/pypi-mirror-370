2025/08/19 icetcore 6.6.76
	修正订阅mix合约时期权总成交量和总持仓量历史数据存在异常时抛出错误问题
2025/08/05 icetcore 6.6.75
	修正gethotmonth获取次热门时合约代码错误
	新增字段CallDownPrice等相关栏位
	新增可获取历史合约的到日期方法getexpirationex
2025/07/25 icetcore 6.6.72
	移除历史数据合成大周期中的交易时段过滤
2025/07/10 icetcore 6.6.71
	新增实时skewdelta,历史数据增加拟合IV（EvaVol）
	移除即将废弃的包
2025/05/06 icetcore 6.6.70
	新增IVout
2025/04/28 icetcore 6.6.69
	调整依赖包版本
2025/04/23 icetcore 6.6.68
	调整TICK成交量0的滤除规则
2025/04/23 icetcore 6.6.67
	移除bar合成中的成交量过滤规则
2025/04/17 icetcore 6.6.66
	修复动态数据和静态数据接口无法同时使用的问题
2025/02/20 icetcore 6.6.65
	新增传入自定义数据接口sendcustomIndicator
2025/02/19 icetcore 6.6.64
	修复subATM和getATM无法获取分红后的期权合约问题
2025/01/02 icetcore 6.6.63
	实时合约列表新增HOT和复权合约代码
2025/01/02 icetcore 6.6.61
	实时合约列表新增HOT和复权合约代码
2024/12/27 icetcore 6.6.60
	修改历史合约获取提示问题
2024/12/25 icetcore 6.6.59
	修正greeksline动态数据没有CSkew/PSkew的问题
	修改期权组合/拆分问题
2024/11/07 icetcore 6.6.58
	修正事件中同步获取数据时另开线程，避免阻塞事件
2024/11/07 icetcore 6.6.57
	修正持仓查询，组合持仓查询，组合回报相关
2024/11/07 icetcore 6.6.56
	修正获取组合回报为空的问题
2024/09/24 icetcore 6.6.55
    新增getsymbol_listingdate获取合约上市日期（TCore v24.09.23）
2024/09/02 icetcore 6.6.54
    修正getATM取值问题
2024/08/07 icetcore 6.6.53
    简化其中部分代码
2024/08/07 icetcore 6.6.52
    新增价差接口newspreadorder
2024/08/05 icetcore 6.6.51
    新增解订动态数据
2024/07/25 icetcore 6.6.50
    格式化代码，修正部分代码写法问题，后续再做模块拆分优化
2024/07/01 icetcore 6.6.49
    修正6.6.48产生的错误
2024/06/25 icetcore 6.6.48
    getallsymbol新增一个可选参数月份
2024/06/24 icetcore 6.6.47
    滤除ATM回调信息中无效的回调
2024/06/21 icetcore 6.6.46
    增加log，初始化参数增加mode，getATM时判断是否需要取消订阅
2024/06/14 icetcore 6.6.45
    修正6.6.45修改不完善产生异常问题
2024/06/14 icetcore 6.6.44
    新增对获取历史合约列表获取方式
2024/05/55 icetcore 6.6.43
    新增实时行情BTV和ATV（对手价TV）
2024/04/15 icetcore 6.6.42
    规范greeks数据订阅解订参数
	修正获取历史合约方法，以降低内存占用
2024/04/11 icetcore 6.6.41
    修正Dogs greeks数据中的一段代码错误
2024/04/11 icetcore 6.6.40
    修正订阅greeks数据时,标的数据比greeks数据后推送导致数据合并错误
2024/04/11 icetcore 6.6.39
    修正期权CPIV历史和实时不一致
2024/04/10 icetcore 6.6.38
    修正getATM获取虚值期权合约错误
2024/03/21 icetcore 6.6.37
    新增Greeks历史数据Skew栏位
2024/03/18 icetcore 6.6.36
    新增TCorelog写入python包版本
2024/03/15 icetcore 6.6.35
    周期数据合成滤除服务器存储的多余数据
2024/03/12 icetcore 6.6.34
    添加群组账号接口
2024/02/26 icetcore 6.6.33
    修正行情解订参数
2024/02/26 icetcore 6.6.32
    修正订阅复权数据实时和动态K线上数据时，没有实时数据
2024/02/23 icetcore 6.6.31
    修正当dogs历史数据时间栏位为空时，用有数据的时间栏位替换
2024/02/22 icetcore 6.6.30
    修正当现量为0 时，使用当日总成交量计算现量
2024/02/06 icetcore 6.6.28
    修正K线合成可能出现混乱问题
	修正subbar的list采用deepcopy，避免数据不同周期数据污染
2024/01/30 icetcore 6.6.27
    增加neworder错误信息
2024/01/22 icetcore 6.6.26
    修正在跨日时段回补日K数据会回补不到最新K
    修正外盘数据滤除规则
2024/01/10 icetcore 6.6.25
    新增greeks数据的dogsk历史数据栏位CallOI PutOI CallVol PutVol
2024/01/01 icetcore 6.6.24
	移除已经废弃使用的包
2023/12/20 icetcore 6.6.23
	优化6.6.22版新增栏位获取方法，修改动态Greeksline数据拼接新增CallOI PutOI CallVol PutVol
2023/12/20 icetcore 6.6.22
    新增期权标的期货Greeks历史数据栏位CallOI PutOI CallVol PutVol(返回对应月份call/put期权所有行权价的当日成交量/持仓量数据)
2023/11/27 icetcore 6.6.21
    修正订阅DOGS ETF期权分红合约带A的合约处理错误
	修正订阅DOGS 指数期权标的错误
2023/11/27 icetcore 6.6.20
    修正TICK周期数据代码错误
2023/11/27 icetcore 6.6.19
    期权持仓监控positionmoniter新增TdSqrt$Vega YdSqrt$Vega(当日/昨日调整后$Vega)
2023/11/25 icetcore 6.6.17
    修正下单参数扩展参数带入方式不正确
2023/11/25 icetcore 6.6.16
    移除6.6.14修改
2023/11/13 icetcore 6.6.14
    修改认证方式
2023/10/25 icetcore 6.6.13
    symbollookup合约搜索滤除空代码
2023/10/24 icetcore 6.6.12
    没有成交价量的实时行情不参与KBar合成
2023/10/19 icetcore 6.6.10
	修正positionmoniter标的delta数据多除100
2023/10/13 icetcore 6.6.9
    修正positionmoniter期权持仓监控数据中的标的持仓delta数据放大后没有缩小
    修正跨日时段时间处理错误导致大周期数据合成时将数据错误滤除
    修正getorderinfo返回委托单信息重复问题
    修正避免重复订阅