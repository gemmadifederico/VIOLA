import pandas as pd
import requests
import json
import time
from threading import Thread
import csv
from urllib.parse import parse_qs, urlparse
NUM_THREADS = 4

caseID = ""
reset = False
filterCase = ""
output = pd.DataFrame(columns=["Case_ID","Start time","End time","Sensor_ID","Label","Label_ID","Activity_ID","Val","Recognized"])

def startStreaming():
    global reset 
    global caseID
    global output

    #IoTStream = pd.read_csv("log_labeled_test.csv", header = 0)
    IoTStream = pd.read_csv("log_labeled.csv", header = 0)
    updateInfoModelurl = "http://127.0.0.1:8083/api/updateInfoModel?name=SensorData"
    resetGSMurl = "http://127.0.0.1:8083/api/reset"
    startGSMurl = "http://127.0.0.1:8083/api/start?infoModelPath=data\dfg\infoModel.xsd&processModelPath=data\dfg\siena.xml"
    message = {
    "Hall-Bedroom_door": 0,
    "Hall-Bathroom_door": 0,
    "ToiletFlush": 0,
    "Plates_cupboard": 0,
    "Fridge": 0,
    "Microwave": 0,
    "Groceries_Cupboard": 0,
    "Hall-Toilet_door": 0,
    "Frontdoor": 0,
    "Pans_Cupboard": 0,
    "Freezer": 0,
    "Cups_cupboard": 0,
    "Dishwasher": 0,
    "Washingmachine": 0,
    "Activity_Size": 0
    }

    for index, line in IoTStream.iterrows():
        output = output.append(line)
        if filterCase == "" or filterCase == line["Case_ID"]:
            if caseID != line["Case_ID"]:
                print("new case id:" + caseID + "-->" + line["Case_ID"])
                caseID = line["Case_ID"]
                resetCounter()
                requests.get(resetGSMurl);
                requests.get(startGSMurl);        
                time.sleep(3)
            if reset == False:
                sensor_name = line["Sensor_ID"]
                message[sensor_name] += 1
                message["Activity_Size"] += 1
            else: 
                message = {key:0 for key in message}
                sensor_name = line["Sensor_ID"]
                message[sensor_name] += 1
                message["Activity_Size"] += 1
                reset = False

            print(message)
            requests.post(updateInfoModelurl, json = message)
            print("sent")
            time.sleep(1)
    output.to_csv("output.csv", index=False)


def resetCounter():
    global reset
    reset = True
    return

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
    print("RESET CALL RECEIVED")
    t2 = Thread(target= resetCounter())
    t2.start()    
    req = request.args.get("stageName")
    if(req[-3:] == "run"):
        t3 = Thread(target=printRow(req))
        t3.start()
    return "DONE"

def printRow(req):
    global output
    dict = {"Case_ID": caseID, "Recognized": req[:-4]}
    output = output.append(dict, ignore_index=True)
    return

app.run(port=8080)

