import pm4py
import pandas as pd

dateCols = ['Start time','End time']
dataframe = pd.read_csv('../kasterenDataset/log_labeled.csv', sep=',', parse_dates=dateCols)
#dataframe = pd.read_csv('./test2.csv', sep=';', parse_dates=dateCols)
dataframe = dataframe.drop_duplicates(subset=['Case_ID', 'Label'], keep='first')
dataframe = dataframe.rename(columns={'Case_ID': 'case:concept:name', 'Label':'concept:name'})

dataframe = dataframe.set_index(['Start time'])
# morning routines
# dataframe = dataframe.between_time('09:00', '13:00')
# evening
# dataframe = dataframe.between_time('18:00', '00:00')

print(dataframe)
log = pm4py.convert_to_event_log(dataframe)
variants = pm4py.get_variants_as_tuples(log)

print('variants:')
print(len(variants))
print('traces per variant:')
for v in variants:
    print(len(variants[v]))

# filtering top k variants
# log = pm4py.filter_variants_top_k(log, 2)
# filtering variants with at least x% coverage
# log = pm4py.filter_variants_by_coverage_percentage(log, 0.05)

dfg, start_activities, end_activities = pm4py.discover_dfg(log)
print(dfg)
print(start_activities)
pm4py.view_dfg(dfg, start_activities, end_activities)

pm4py.objects.dfg.exporter.exporter.apply(dfg, './test-csv.dfg', pm4py.objects.dfg.exporter.variants.classic, {pm4py.visualization.dfg.visualizer.Variants.FREQUENCY.value.Parameters.START_ACTIVITIES:start_activities,pm4py.visualization.dfg.visualizer.Variants.FREQUENCY.value.Parameters.END_ACTIVITIES:end_activities})