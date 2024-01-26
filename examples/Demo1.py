#A股票行情数据获取演示   https://github.com/mpquant/Ashare
from ashare import api
from datetime import datetime
    
# 证券代码兼容多种格式 通达信，同花顺，聚宽
# sh000001 (000001.XSHG)    sz399006 (399006.XSHE)   sh600519 ( 600519.XSHG ) 

df = api.query_prices_untilnow('sh000001', frequency='1day', count=5)      #默认获取今天往前5天的日线行情
print('上证指数日线行情\n',df)

df = api.query_data_region('000001.XSHG', start=datetime(2022, 2, 3), end=datetime(2023, 1, 1))   #可以指定结束日期，获取历史行情
print('上证指数历史行情\n',df)
    
df = api.query_data_region('sh600519', frequency='15minute', count=5)     #分钟线行情，只支持从当前时间往前推，可用'1m','5m','15m','30m','60m'
print('贵州茅台15分钟线\n',df)

df = api.query_data_region('600519.XSHG',frequency='60minute', count=6)  #分钟线行情，只支持从当前时间往前推，可用'1m','5m','15m','30m','60m'
print('贵州茅台60分钟线\n',df)
