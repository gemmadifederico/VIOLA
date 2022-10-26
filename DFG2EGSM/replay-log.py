import pm4py
import requests
import time
url = 'http://localhost:8083/api/updateInfoModel'
log = pm4py.read_xes('./running-example.xes')

for tr in log:
    for e in tr:
        act = (e['Activity'].replace(' ','_'))
        #send activity start - end
        requests.get(url, params={'name': act+"_s"})
        time.sleep(1)
        requests.get(url, params={'name': act+"_e"})
        time.sleep(1)
    time.sleep(3)
