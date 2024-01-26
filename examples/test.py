import json, requests
from datetime import datetime

code="sh000001"
unit="week"
# start_date=datetime(2021, 5, 27).strftime('%Y-%m-%d')
end_date=datetime.now().strftime('%Y-%m-%d')
count=5
URL=f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'     
# st=json.loads(requests.get(URL).content)
# print(json.dumps(st, indent=4))
# ms='qfq'+unit
# stk=st['data'][code]   

ts=5
count=5
URL=f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}' 
st=json.loads(requests.get(URL).content)
print(json.dumps(st, indent=4))

ts=5 # 必须是5的倍数
code="sh000001"
count = 10
URL=f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={ts}&ma=5&datalen={count}' 
# st=json.loads(requests.get(URL).content)
# print(json.dumps(st, indent=4))