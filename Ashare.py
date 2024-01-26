import json, requests
from datetime import datetime
import pandas as pd
from loguru import logger

from abc import ABC, abstractmethod

class ApiServerBase(ABC):
    # @abstractmethod
    # def query_daily_prices(self):
    #     pass

    # @abstractmethod
    # def query_hourly_prices(self):
    #     pass

    # @abstractmethod
    # def query_minute_prices(self):
    #     pass
    pass

# TODO: 'Xday','Xmonth', 'Xminute' # 'daily'(等同于'1d'), 'minute'(等同于'1m')
    
class Tencent(ApiServerBase):
    def __init__(self) -> None:
        pass

    def query_prices(self, security: str, frequency="day", end_date=datetime.now(), count=10) -> pd.DataFrame:
        '''
        腾讯日 周 月线。
        frequency in ["day", "week", "month"]
        '''

        if frequency not in ["day", "week", "month"]:
            raise RuntimeError(f"frequency error : {frequency}")

        if not isinstance(end_date, datetime):
            raise TypeError(type(end_date))
        

        # TODO: check security
        end_date_str = end_date.strftime(r'%Y-%m-%d')

        freq = frequency

        URL = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={security},{freq},,{end_date_str},{count},qfq' # TODO: qfq 前复权

        content = json.loads(requests.get(URL).content)

        if content["msg"] != "":
            raise RuntimeError(content["msg"])
            
        '''
        {
            "code": 0,
            "msg": "",
            "data": {
                "sh605577": {
                    "qfqday": [
                        [
                            "2024-01-25",
                            "27.590",
                            "30.800",
                            "30.800",
                            "27.120",
                            "285458.000"
                        ]
                    ],
        '''
        # 指数是 freq 其他的则是 qfq+freq 
        day = "day" if "qfq" + freq not in content["data"][security] else "qfq" + freq
        data = content["data"][security][day]

        columns = ['time','open','close','high','low','volume']
        df = pd.DataFrame(
            data, 
            columns=columns,
        )
        # 除了time之外都进行浮点化
        df[columns[1:]] = df[columns[1:]].astype("float")

        df.loc[:, "time"] = pd.to_datetime(df["time"])

        df.set_index(['time'], inplace=True) # Whether to modify the DataFrame rather than creating a new one.
        # df.index.name = '' TODO:?

        return df

    def query_minute_prices(self, security: str, frequency="1minute", end_date=datetime.now(), count=10) -> pd.DataFrame:
        '''
        腾讯分钟线.
        frequency in [1minute, 5minute, 10minute ...]
        '''
        if not frequency.endswith("minute"): 
            raise RuntimeError(f"frequency error :{frequency}")
            
        if not frequency[0].isdigit():
            raise RuntimeError(f"frequency error {frequency}")
            
        if not isinstance(end_date, datetime):
            raise TypeError(type(end_date))
        
        # 提取前面的数字
        freq = int(''.join(c for c in frequency if c.isdigit()))

        URL = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={security},m{freq},,{count}' 

        content = json.loads(requests.get(URL).content)
        data = content["data"][security]["m" + str(freq)]

        columns = ['time','open','close','high','low','volume','n1','n2']
        df = pd.DataFrame(
            data, 
            columns=columns
        )[columns[:-2]]

        df[columns[1:-2]] = df[columns[1:-2]].astype("float")

        df.loc[:, "time"] = pd.to_datetime(df["time"])

        df.set_index(['time'], inplace=True)

        return df

class Sina(ApiServerBase):

    # sina新浪全周期获取函数，分钟线 5m,15m,30m,60m
    def query_prices(self, security: str, frequency="5m", end_date=datetime.now(), count=10) -> pd.DataFrame:
        '''
        frequency必须是5的倍数
        '''
        if not frequency.endswith("m"): 
            raise RuntimeError(f"frequency error :{frequency}")
            
        if not frequency[0].isdigit():
            raise RuntimeError(f"frequency error {frequency}")
            
        if not isinstance(end_date, datetime):
            raise TypeError(type(end_date))

        # 提取前面的数字
        mfreq = int(''.join(c for c in frequency if c.isdigit()))

        if mfreq % 5 != 0:
            raise RuntimeError(f"frequency must be multiple of five but found :{frequency}")

        URL = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={security}&scale={mfreq}&ma=5&datalen={count}'

        content = json.loads(requests.get(URL).content)
        '''
        这边其实还有两列数据 暂时用不上
        "ma_price5": 29.488,
        "ma_volume5": 331320
        '''
        data = content

        columns = ['day','open','close','high','low','volume']
        df = pd.DataFrame(
            data, 
            columns=columns
        )

        df[columns[1:]] = df[columns[1:]].astype("float")
        df.loc[:, "day"] = pd.to_datetime(df["day"])
        df.set_index(['day'], inplace=True)

        return df

class Api:
    def __init__(self) -> None:
        self._tencent = Tencent()
        self._sina = Sina()
    
    def query_prices_untilnow(self, security: str, frequency='60minute', count=10) -> pd.DataFrame:
        '''
        tx支持: 1minute 5minute 10minute... 1day 1week 1month
        xl支持:         5minute 10minute... 1day 1week 1month
        '''

        while True:
            if any(security.endswith(end) for end in [".XSHG", ".XSHE"]):
                break
            
            if any(security.startswith(start) for start in ["sh", "sz"]):
                break
            
            raise RuntimeError(f"security format error : {security}")

        n    = int(''.join(c for c in frequency if c.isdigit()))
        freq = ''.join(c for c in frequency if c.isalpha())
        
        if freq not in ["minute", "day", "week", "month"]:
            raise RuntimeError(f"frequency error : {frequency}")
        
        #证券代码编码兼容处理 
        code = security.replace('.XSHG', '').replace('.XSHE', '')
        code = 'sh' + code if ('XSHG' in security) else 'sz' + code if ('XSHE' in security) else security

        if freq == "minute":

            try:
                return self._tencent.query_minute_prices(security, frequency, count=count)
            except Exception as e:
                logger.info(f"found exception {e}, try next server")
                
            try:
                return self._sina.query_prices(security, frequency=str(n)+"m", count=count)
            except Exception as e:
                logger.error(f"backup server failed with {e}")
                raise e

        elif freq in ["day", "week", "month"]:

            if n != 1:
                raise RuntimeError("only support 1 day/week/month")

            try:
                return self._tencent.query_prices(security, frequency=freq, count=count)
            except Exception as e:
                logger.info(f"found exception {e}, try next server")
                
            try:
                # 日线1d=240m   周线1w=1200m  1月=7200m
                if freq == "1day":
                    freq = "240m"

                elif freq == "1week":
                    freq = "1200m"
                    
                elif freq == "1month":
                    freq = "7200m"

                else:
                    raise RuntimeError(f"unhandled {freq}")
                
                return self._sina.query_prices(security, frequency=freq, count=count)

            except Exception as e:
                logger.error(f"backup server failed with {e}")
                raise e

        else:
            raise RuntimeError(f"unhandled freq : {freq}")

api = Api()
            

if __name__ == "__main__":
    print(api.query_prices_untilnow("sh605577", "1minute", count=3))
    print(api.query_prices_untilnow("sh605577", "5minute", count=3))
    print(api.query_prices_untilnow("sh605577", "1day", count=3))
    print(api.query_prices_untilnow("sh605577", "1week", count=3))
    print(api.query_prices_untilnow("sh605577", "1month", count=3))