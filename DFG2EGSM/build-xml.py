import pm4py
import xml.etree.ElementTree as ET


dfg, start_activities, end_activities = pm4py.objects.dfg.importer.importer.apply('./test.dfg')

print(dfg)
print(len(dfg))

print(start_activities)
print(end_activities)

pm4py.view_dfg(dfg, start_activities, end_activities)

pres = dict()
succs = dict()

for kx, vx in dfg.items():
    #identify predecessors for each activity
    pre = pres.get(kx[1].replace(' ','_'))
    if not pre:
        pres[(kx[1].replace(' ','_'))] = list()
    pres[(kx[1].replace(' ','_'))].append(kx[0].replace(' ','_'))
    #identify successors for each activity
    succ = succs.get(kx[0].replace(' ','_'))
    if not succ:
        succs[(kx[0].replace(' ','_'))] = list()
    succs[(kx[0].replace(' ','_'))].append(kx[1].replace(' ','_'))
    
#add activities with no predecessors
for sa in start_activities:
    if (sa.replace(' ','_') not in pres):
        pres[(sa.replace(' ','_'))] = list()

#add activities with no successors
for ea in end_activities:
    if (ea.replace(' ','_') not in succs):
        succs[(ea.replace(' ','_'))] = list()

print(pres)
print(succs)
    

#create information model
infomodelxsd = ET.Element('xs:schema', {'xmlns:xs':'http://www.w3.org/2001/XMLSchema', 'attributeFormDefault':'unqualified', 'elementFormDefault':'qualified'})
#create egsm model
compositeapp = ET.Element('ca:CompositeApplicationType', {'xmlns:ca':'http://siena.ibm.com/model/CompositeApplication', 'version':'2.0', 'name':'Definitions_1_application'})
eventmodel = ET.SubElement(compositeapp, 'ca:EventModel', {'id':'Definitions_1_eventModel', 'name':'Definitions_1_eventModel'})
for activity in pres:
    event = ET.SubElement(eventmodel, 'ca:Event', {'id': activity+'_s', 'name': activity+'_s'})
    event = ET.SubElement(eventmodel, 'ca:Event', {'id': activity+'_e', 'name': activity+'_e'})
definitions = ET.SubElement(compositeapp, 'ca:Component', {'id':'Definitions_1'})
infomodel = ET.SubElement(definitions, 'ca:InformationModel', {'id':'infoModel', 'rootDataItemId':'infoModel'})
infomodelref = ET.SubElement(infomodel, 'ca:DataItem', {'id':"infoModel", 'rootElement':'infoModel', 'schemaUri':'data/infoModel.xsd'})
gsm = ET.SubElement(definitions, 'ca:GuardedStageModel', {'id': 'test_GSM', 'name': 'Default Process'})
#create process stage
procstage = ET.SubElement(gsm, 'ca:Stage', {'id': 'process', 'name': 'Default Process'})

#generate one stage per activity

for activity in pres:

    #add corresponding events to information model
    elem = ET.SubElement(infomodelxsd, 'xs:element', {'name':activity+'_s'})
    ct = ET.SubElement(elem, 'xs:complexType')
    attr = ET.SubElement(ct, 'xs:attribute', {'name':'timestamp', 'type':'xs:dateTime', 'use':'required'})
    
    elem = ET.SubElement(infomodelxsd, 'xs:element', {'name':activity+'_e'})
    ct = ET.SubElement(elem, 'xs:complexType')
    attr = ET.SubElement(ct, 'xs:attribute', {'name':'timestamp', 'type':'xs:dateTime', 'use':'required'})

    #add corresponding data flow guard to process stage
    dfg = ET.SubElement(procstage, 'ca:DataFlowGuard', {'eventIds': activity+'_s', 'expression': 'GSM.isEventOccurring('+activity+'_s)', 'id': 'process_'+activity+'_dfg', 'language': 'JEXL', 'name': 'Process '+activity+' data flow guard'})

    #create activity valid substage
    valstage = ET.SubElement(procstage, 'ca:SubStage', {'id': activity, 'name': activity})
    vdfg = ET.SubElement(valstage, 'ca:DataFlowGuard', {'eventIds': activity+'_s', 'expression': 'GSM.isEventOccurring('+activity+'_s)', 'id': activity+'_dfg', 'language': 'JEXL', 'name': activity+' data flow guard'})
    #activity has no successors
    if len(succs[activity]) == 0:
        #add milestone to activity valid stage
        vm = ET.SubElement(valstage, 'ca:Milestone', {'eventIds': '', 'id': activity+'_m', 'name': activity+' milestone'})
        vmc = ET.SubElement(vm, 'ca:Condition', {'expression': 'GSM.isMilestoneAchieved('+activity+'_run_m)', 'id': activity+'_m_c', 'language': 'JEXL', 'name': activity+' milestone condition'})

        #add milestone to process stage
        m = ET.SubElement(procstage, 'ca:Milestone', {'eventIds': '', 'id': 'process_'+activity+'_m', 'name': 'process '+activity+' milestone'})
        mc = ET.SubElement(m, 'ca:Condition', {'expression': 'GSM.isMilestoneAchieved('+activity+'_m)', 'id': 'process_'+activity+'_m_c', 'language': 'JEXL', 'name': 'Process '+activity+' milestone condition'})
    else: 
        #the only successor is the activity itself
        if len(succs[activity]) == 1 and succs[activity][0] == activity:
            #stage should remain open, since no termination condition exists
            vm = ET.SubElement(valstage, 'ca:Milestone', {'eventIds': succ+'_s', 'id': activity+'_m_'+succ, 'name': activity+' milestone'})
            vmc = ET.SubElement(vm, 'ca:Condition', {'expression': 'false', 'id': activity+'_m_c', 'language': 'JEXL', 'name': activity+' milestone condition'})
        #activity has other successors than itself
        else:
            vmcexpr = ''
            vm = ET.SubElement(valstage, 'ca:Milestone', {'eventIds': '', 'id': activity+'_m', 'name': activity+' milestone'})
            for succ in succs[activity]:
                if succ != activity:
                    vmcexpr = vmcexpr + 'GSM.isStageActive(' + succ + ')'
                    if (succ != succs[activity][-1]):
                        vmcexpr = vmcexpr + ' or '
            vmc = ET.SubElement(vm, 'ca:Condition', {'expression': vmcexpr, 'id': activity+'_m_c', 'language': 'JEXL', 'name': activity+' milestone condition'})
    vpfgexpr = ''
    firstactexp = '('
    #check if activity is the first to be executed
    for sa in start_activities:
        if sa.replace(' ','_') == activity:
            firstactexp = firstactexp + 'not ('
            for a2 in pres:
                firstactexp = firstactexp + 'GSM.isStageActive('+a2+')'
                if (a2 != list(pres)[-1]):
                    firstactexp = firstactexp + ' or '
                else:
                    firstactexp = firstactexp + ')'
        
    predexp = '('
    #check if activity has predecessors
    for pre in pres[activity]:
        predexp = predexp + 'GSM.isStageActive('+pre+')'
        if (pre != pres[activity][-1]):
            predexp = predexp + ' or '
    
    if firstactexp != '(':
        if predexp != '(':
            vpfgexpr = firstactexp + ') or ' + predexp + ')'
        else:
            vpfgexpr = firstactexp + ')'
    else:
        vpfgexpr = predexp + ')'
            
    vpfg = ET.SubElement(valstage, 'ca:ProcessFlowGuard', {'id': activity+'_pfg', 'name': activity+' process flow guard', 'expression': vpfgexpr})

    #create activity running substage
    actstage = ET.SubElement(valstage, 'ca:SubStage', {'id': activity+'_run', 'name': activity+' running'})
    adfg = ET.SubElement(actstage, 'ca:DataFlowGuard', {'eventIds': activity+'_s', 'expression': 'GSM.isEventOccurring('+activity+'_s)', 'id': activity+'_run_dfg', 'language': 'JEXL', 'name': activity+' running data flow guard'})
    am = ET.SubElement(actstage, 'ca:Milestone', {'eventIds': activity+'_e', 'id': activity+'_run_m', 'name': activity+' running milestone'})
    amc = ET.SubElement(am, 'ca:Condition', {'expression': 'GSM.isEventOccurring('+activity+'_e)', 'id': activity+'_run_m_c', 'language': 'JEXL', 'name': activity+' running milestone condition'})
    
    if not activity in pres[activity]:
        apfg = ET.SubElement(actstage, 'ca:ProcessFlowGuard', {'id': activity+'_run_pfg', 'name': activity+' running process flow guard', 'expression': 'not GSM.isMilestoneAchieved('+activity+'_run_m)'})

ET.ElementTree(compositeapp).write("siena.xml", xml_declaration=True, encoding='utf-8')
ET.ElementTree(infomodelxsd).write("infoModel.xsd", xml_declaration=True, encoding='utf-8')

# split activity A in A_start and A_end: -> can detect any control flow issue (similar to guarded PN):
#   we can also model parallel activities
# downsides: always one stage active, no 1:1 mapping between activity and stage (but trivial to reconstruct)
#   need to add helper stage final to detect when a final stage is reached
# if only transitions from a final stage F to initial stages exist, then parent stage can be closed,
# otherwise, cannot know if current pattern is complete or other events related to it will arrive
# (problem similar to detecting when (AB*)* is matched)