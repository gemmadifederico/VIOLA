import pandas as pd
import requests
import json
import time
from threading import Thread, Lock
NUM_THREADS = 4

caseID = ""
reset = False
filterCase = ""
delay = 0
output = pd.DataFrame(columns=["Case_ID","Timestamp","Type","Sensor","Label","Label_ID","Activity_ID","Recognized","Conformance","Nonce","Delay"])
lockPrint = Lock()
lockReset = Lock()    

def startStreaming():
    global reset 
    global caseID
    global output
    global delay

    # IoTStream = pd.read_csv("normal/Lnormal_labeled_train.csv", header = 0)
    IoTStream = pd.read_csv("normal/Lnormal_labeled_test.csv", header = 0)
    # IoTStream = pd.read_csv("shuffle/Lerror1_labeled.csv", header = 0)
    # IoTStream = pd.read_csv("different/Lerror2_labeled.csv", header = 0)
    IoTStream['Timestamp'] = pd.to_datetime(IoTStream['Timestamp'], format="%Y-%m-%d %H:%M:%S.%f")
    updateInfoModelurl = "http://127.0.0.1:8083/api/updateInfoModel?name=SensorData"
    resetGSMurl = "http://127.0.0.1:8083/api/reset"
    startGSMurl = "http://127.0.0.1:8083/api/start?infoModelPath=data\dfg\infoModel.xsd&processModelPath=data\dfg\siena.xml"
    message = {
        # 'door_A' : 0,
        # 'sens3_A' : 0,
        # 'sens1_A' : 0,
        # 'sens4_A' : 0,
        # 'sens2_A' : 0,
        # 'door_B' : 0,
        # 'sens4_B' : 0,
        # 'sens3_B' : 0,
        # 'sens1_B' : 0,
        # 'sens2_B' : 0,
        # 'door_C' : 0,
        # 'sense1_C' : 0,
        # 'sens4_C' : 0,
        # 'sens2_C' : 0,
        # 'sens3_C' : 0,
        # 'sens4_D' : 0,
        # 'sens3_D' : 0,
        # 'sens2_D' : 0,
        # 'sens1_D' : 0,
        # 'door_D' : 0,
    }

    for idc, case in IoTStream.groupby("Case_ID"):
        requests.get(resetGSMurl)
        requests.get(startGSMurl)
        for id, window in case.groupby(pd.Grouper(freq="30s", key = "Timestamp")):
            if(window.empty):
                pass
            else:
                start = time.time()
                caseID = window.iloc[0]["Case_ID"]
                for ix, el in window.iterrows():
                    printRow(el)
                    sensor_name = el["Sensor"]
                    # Set the sensor identifier as 1 in the given window
                    message[sensor_name] = 1
                # Send the message
                requests.post(updateInfoModelurl, json = message)
                print(message)
                # Reset the message
                message = {key:0 for key in message}
                delay = (time.time() - start) * 1000
                # Wait few seconds befor passing to the next window
                # time.sleep(0.01)
    output.to_csv("output.csv", index=False)

# def resetCounter():
#     global reset
#     reset = True
#     return

from flask import Flask, request
app = Flask(__name__)

@app.route('/api/updateInfoModel', methods=['POST'])
def index():
    print("Received call post")
    return (request.form)

@app.route('/api/start', methods=['GET'])
def index1():
    print("STARTING STREAMING")
    t1 = Thread(target= startStreaming())
    t1.start()
    return "DONE"

@app.route('/api/reset', methods=['GET'])
def index2():
    lockReset.acquire()
    print("RESET CALL RECEIVED")
    # t2 = Thread(target= resetCounter())
    # t2.start()    
    req = request.args.get("stageName")
    cf = request.args.get("compliance")
    ets = request.args.get("timestamp")
    # if(req != "process" and req[-3:] != "run"):
    # if(req != "process"):
    dict = {"Case_ID": caseID, "Recognized": req, "Conformance":cf, "Nonce": ets}
    printRow(dict)
        # t3 = Thread(target=printRow(req,cf))
        # t3.start()
    lockReset.release()
    return "DONE"

def printRow(row):
    lockPrint.acquire()
    global output
    row["Delay"] = delay
    output = output.append(row, ignore_index=True)
    lockPrint.release()
    return


app.run(port=8080)

