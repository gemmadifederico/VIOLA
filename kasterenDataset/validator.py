import pandas as pd
from urllib.parse import parse_qs, urlparse
NUM_THREADS = 4

caseID = ""
label = ""
activity = ""

fpCase = 0
fnCase = 0
tpCase = 0
actCase = 0
otCase = 0
ooCase = 0

fpTotal = 0
fnTotal = 0
tpTotal = 0
actTotal = 0
otTotal = 0
ooTotal = 0

output = pd.DataFrame(columns=["Case_ID","Start time","End time","Sensor","Label","Activity_ID","Val","Recognized","Conformance"])


# log = pd.read_csv("output_test.csv", header = 0)
log = pd.read_csv("output.csv", header = 0)
log.fillna('', inplace=True)

for index, line in log.iterrows():

    print(str(line["Case_ID"]) + "," + str(line["Label"]) + "," + str(line["Recognized"]))

    if line["Case_ID"] != caseID:
        # new case

        if label != activity:
            fnCase += 1
            
        if caseID != "":
            print("False positives :" + str(fpCase))
            print("False negatives: " + str(fnCase))
            print("True positives: " + str(tpCase))
            print("Total activities per case: " + str(actCase))
            print("On-time activities per case: " + str(otCase))
            print("Out-of-order activities per case: " + str(ooCase))
            print("Conformance per case: " + str(otCase/(otCase+ooCase)))
            print()

        caseID = line["Case_ID"]

        fpTotal = fpTotal + fpCase
        fnTotal = fnTotal + fnCase
        tpTotal = tpTotal + tpCase
        actTotal = actTotal + actCase
        otTotal = otTotal + otCase
        ooTotal = ooTotal + ooCase

        fpCase = 0
        fnCase = 0
        tpCase = 0
        actCase = 0
        otCase = 0
        ooCase = 0

        label = ""
        activity = ""
        
        print("Case :" + caseID)

    if line["Label"] != label and line["Label"] != "":
        # new label
        
        if label != activity and label != "":
            fnCase += 1
        
        label = line["Label"]
        activity = ""
        actCase += 1
        
    if line["Recognized"] != activity and line["Recognized"] != "":
        # new activity recognized
        if line["Recognized"] == label:
            tpCase += 1
            activity = line["Recognized"]
        else:
            fpCase += 1
        if line["Conformance"] == "onTime":
            otCase += 1
        else:
            ooCase += 1

if label != activity:
    fnCase += 1    

print("False positives :" + str(fpCase))
print("False negatives: " + str(fnCase))
print("True positives: " + str(tpCase))
print("Total activities per case: " + str(actCase))
print("On-time activities per case: " + str(otCase))
print("Out-of-order activities per case: " + str(ooCase))
print("Conformance per case: " + str(otCase/(otCase+ooCase)))
print()

fpTotal = fpTotal + fpCase
fnTotal = fnTotal + fnCase
tpTotal = tpTotal + tpCase
actTotal = actTotal + actCase
otTotal = otTotal + otCase
ooTotal = ooTotal + ooCase

print("Total false positives :" + str(fpTotal))
print("Total false negatives: " + str(fnTotal))
print("Total true positives: " + str(tpTotal))
print("Total activities for all cases: " + str(actTotal))
print("On-time activities for all cases: " + str(otTotal))
print("Out-of-order activities for all cases: " + str(ooTotal))
print("Overall conformance: " + str(otTotal/(otTotal+ooTotal)))
print()
