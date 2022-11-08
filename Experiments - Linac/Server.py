import pandas as pd
import requests
import json
import time
from threading import Thread
NUM_THREADS = 4

caseID = ""
reset = False
filterCase = ""

def startStreaming():
    global reset 
    global caseID

    IoTStream = pd.read_csv("normal/Ltrain_labeled.csv", header = 0)
    updateInfoModelurl = "http://127.0.0.1:8083/api/updateInfoModel?name=SensorData"
    resetGSMurl = "http://127.0.0.1:8083/api/reset"
    startGSMurl = "http://127.0.0.1:8083/api/start?infoModelPath=data\dfg\infoModel.xsd&processModelPath=data\dfg\siena.xml"
    message = {
        'door_A' : 0,
        'sens3_A' : 0,
        'sens1_A' : 0,
        'sens4_A' : 0,
        'sens2_A' : 0,
        'door_B' : 0,
        'sens4_B' : 0,
        'sens3_B' : 0,
        'sens1_B' : 0,
        'sens2_B' : 0,
        'door_C' : 0,
        'sense1_C' : 0,
        'sens4_C' : 0,
        'sens2_C' : 0,
        'sens3_C' : 0,
        'sens4_D' : 0,
        'sens3_D' : 0,
        'sens2_D' : 0,
        'sens1_D' : 0,
        'door_D' : 0,
    }

    for index, line in IoTStream.iterrows():
        if filterCase == "" or filterCase == line["Case_ID"]:
            if caseID != line["Case_ID"]:
                print("new case id:" + caseID + "-->" + line["Case_ID"])
                caseID = line["Case_ID"]
                reset = True
                requests.get(resetGSMurl);
                requests.get(startGSMurl);        
                time.sleep(3)
            if reset == False:
                sensor_name = line["Sensor"]
                message[sensor_name] += 1
            else: 
                message = {key:0 for key in message}
                sensor_name = line["Sensor"]
                message[sensor_name] += 1
                reset = False

            print(message)
            #requests.post(url, json = json.dumps(message))
            requests.post(updateInfoModelurl, json = message)
            print("sent")
            time.sleep(1)

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
    return "RESET DONE"

app.run(port=8080)

