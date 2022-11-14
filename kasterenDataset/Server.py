import pandas as pd
import requests
import json
import time
from threading import Thread, Lock
import csv
NUM_THREADS = 4

caseID = ""
reset = False
filterCase = ""
output = pd.DataFrame(columns=["Case_ID","Start time","End time","Sensor","Label","Activity_ID","Recognized","Conformance"])
lockPrint = Lock()
lockReset = Lock() 

def startStreaming():
    global reset 
    global caseID
    global output

    IoTStream = pd.read_csv("log_labeled.csv", header = 0)
    IoTStream['Start time'] = pd.to_datetime(IoTStream['Start time'], format='%Y-%m-%d %H:%M:%S')
    updateInfoModelurl = "http://127.0.0.1:8083/api/updateInfoModel?name=SensorData"
    resetGSMurl = "http://127.0.0.1:8083/api/reset"
    startGSMurl = "http://127.0.0.1:8083/api/start?infoModelPath=data\dfg\infoModel.xsd&processModelPath=data\dfg\siena.xml"
    message = {
    # "Hall-Bedroom_door": 0,
    # "Hall-Bathroom_door": 0,
    # "ToiletFlush": 0,
    # "Plates_cupboard": 0,
    # "Fridge": 0,
    # "Microwave": 0,
    # "Groceries_Cupboard": 0,
    # "Hall-Toilet_door": 0,
    # "Frontdoor": 0,
    # "Pans_Cupboard": 0,
    # "Freezer": 0,
    # "Cups_cupboard": 0,
    # "Dishwasher": 0,
    # "Washingmachine": 0
    }

    for idc, case in IoTStream.groupby("Case_ID"):
        requests.get(resetGSMurl);
        requests.get(startGSMurl);
        for id, window in case.groupby(pd.Grouper(freq="2min", key = "Start time")):
            if(window.empty):
                pass
            else:
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
    # if(req != "process" and req[-3:] != "run"):
    if(req != "process"):
        dict = {"Case_ID": caseID, "Recognized": req, "Conformance":cf}
        printRow(dict)
        # t3 = Thread(target=printRow(req,cf))
        # t3.start()
    lockReset.release()
    return "DONE"

def printRow(row):
    lockPrint.acquire()
    global output
    output = output.append(row, ignore_index=True)
    lockPrint.release()
    return

app.run(port=8080)

