import pm4py
import xml.etree.cElementTree as ET

dfg, start_activities, end_activities = pm4py.objects.dfg.importer.importer.apply('./test.dfg')

print(dfg)
print(len(dfg))

print(start_activities)

print(end_activities)

pres = dict()

# identify predecessors for each activity
for kx, vx in dfg.items():
    pre = pres.get(kx[1])
    if not pre:
        pres[kx[1]] = list()
    pres[kx[1]].append(kx[0])
print(pres)
    
pm4py.view_dfg(dfg, start_activities, end_activities)



# split activity A in A_start and A_end: -> can detect any control flow issue (similar to guarded PN):
#   we can also model parallel activities
# downsides: always one stage active, no 1:1 mapping between activity and stage (but trivial to reconstruct)
#   need to add helper stage final to detect when a final stage is reached
# if only transitions from a final stage F to initial stages exist, then parent stage can be closed,
# otherwise, cannot know if current pattern is complete or other events related to it will arrive
# (problem similar to detecting when (AB*)* is matched)