import json, requests
from datetime import datetime

code="sh000001"
unit="day"
start_date=datetime(2021, 5, 27).strftime('%Y-%m-%d')
end_date=datetime.now().strftime('%Y-%m-%d')
count=100
URL=f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'     
st=json.loads(requests.get(URL).content)
print(json.dumps(st, indent=4))
# ms='qfq'+unit
# stk=st['data'][code]   