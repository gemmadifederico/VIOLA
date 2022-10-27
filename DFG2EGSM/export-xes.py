import pm4py
log = pm4py.read_xes('./running-example.xes')

dfg, start_activities, end_activities = pm4py.discover_dfg(log)
print(dfg)
pm4py.objects.dfg.exporter.exporter.apply(dfg, './test.dfg')