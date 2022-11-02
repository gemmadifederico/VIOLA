import pandas as pd
import requests
import json
import time
from threading import Thread
NUM_THREADS = 4

reset = False
def startStreaming():
    global reset 

    #IoTStream = pd.read_csv("log_labeled_test.csv", header = 0)
    IoTStream = pd.read_csv("log_labeled.csv", header = 0)
    url = "http://127.0.0.1:8083/api/updateInfoModel?name=SensorData"
    sensors = {
    1 : 'Microwave'         ,
    5 : 'Hall-Toilet_door'  ,
    6 : 'Hall-Bathroom_door',
    7 : 'Cups_cupboard'     ,
    8 : 'Fridge'            ,
    9 : 'Plates_cupboard'   ,
    12 : 'Frontdoor'         ,
    13 : 'Dishwasher'        ,
    14 : 'ToiletFlush'       ,
    17 : 'Freezer'           ,
    18 : 'Pans_Cupboard'     ,
    20 : 'Washingmachine'    ,
    23 : 'Groceries_Cupboard',
    24 : 'Hall-Bedroom_door' 
    }
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
        if reset == False:
            sensor_name = sensors[line["Sensor_ID"]]
            message[sensor_name] += 1
            message["Activity_Size"] += 1
        else: 
            message = {key:0 for key in message}
            sensor_name = sensors[line["Sensor_ID"]]
            message[sensor_name] += 1
            message["Activity_Size"] += 1
            reset = False

        print(message)
        #requests.post(url, json = json.dumps(message))
        requests.post(url, json = message)
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

