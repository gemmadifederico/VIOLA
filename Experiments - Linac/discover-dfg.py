import pm4py
import pandas as pd

dateCols = ['Timestamp']
dataframe = pd.read_csv('./normal/Lnormal_labeled_train.csv', sep=',', parse_dates=dateCols)

dataframe = dataframe.drop_duplicates(subset=['Case_ID', 'Label'], keep='first')
dataframe = dataframe.rename(columns={'Case_ID': 'case:concept:name', 'Label':'concept:name'})

print(dataframe)
log = pm4py.convert_to_event_log(dataframe)
variants = pm4py.get_variants_as_tuples(log)

print('variants:')
print(len(variants))
print('traces per variant:')
for v in variants:
    print(len(variants[v]))

dfg, start_activities, end_activities = pm4py.discover_dfg(log)
print(dfg)
print(start_activities)
pm4py.view_dfg(dfg, start_activities, end_activities)

pm4py.objects.dfg.exporter.exporter.apply(dfg, './train.dfg', pm4py.objects.dfg.exporter.variants.classic, {pm4py.visualization.dfg.visualizer.Variants.FREQUENCY.value.Parameters.START_ACTIVITIES:start_activities,pm4py.visualization.dfg.visualizer.Variants.FREQUENCY.value.Parameters.END_ACTIVITIES:end_activities})