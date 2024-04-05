import os
import sys
import pandas as pd
import numpy as np
import copy
from datetime import datetime, timedelta
from db_manager import DBManager, DBClient, TLPhase
# from element import TLPhase, TLLogic

dbm = DBManager()
dbm.initialize_db(
    '127.0.0.1',
    3306,
    'root',
    'filab1020',
    'filab_traffic',
    'utf8'
)

sql = 'SELECT id FROM traffic_light'
tmp = dbm.read_query(sql)
tlids = []
for i in tmp:
    if len(i[0]) > 3:
        tlids.append(i[0])

a = ['3500006301', '3500006600', '3500006650', '3500006660', '3500006700',
     '3500006901', '3500007100', '3500007300', '3500007350', '3500007500',
     '3500007700', '3500007900', '3500008000', '3500051802', '3500051804',
     '3500058500', '3500058550', '3500058700', '3500058900', '3500059300',
     '3500059350', '3500059800', '3500059850', '3500060100', '3500060600',
     '3500060650', '3500060660', '3500060800', '3500060850', '3500060860',
     '3500062100', '3500062500', '3500062550', '3500065800', '3500065850',
     '3500302300', '3510000200', '3510000250', '3510000300', '3510000400',
     '3510021200', '3510021250', '3510021300', '3510021350', '3510021400',
     '3510021500', '3510021700']

tllist = dbm.read_tllight(tlids)
tllist_element = []
tllist_cycle = []
tllist_async = []

case = 1
for tl in tllist:
    yellow = 100
    cycle = 0
    plen = 0
    for inx, value in tl.phases.items():
        cycle += value["duration"]
        if yellow > value["duration"]:
            yellow = value["duration"]

    # case 1
    tmp1 = copy.deepcopy(tl)
    tmp1.id = tl.id + '_1'
    tmp1.programID = tl.programID + '_1'
    last = 0
    count = 0
    for inx, value in tmp1.phases.items():
        if value["duration"] > yellow:
            if count % 2 == 0:
                tmp1.phases[inx]["duration"] += 10
            elif count % 2 == 1:
                tmp1.phases[inx]["duration"] -= 10
            count += 1
            last = inx
    if count % 2 == 1:
        tmp1.phases[last]["duration"] -= 10
    tllist_element.append(tmp1)

    # case 2
    tmp2 = copy.deepcopy(tl)
    tmp2.id = tl.id + '_2'
    tmp2.programID = tl.programID + '_2'
    for inx, value in tmp2.phases.items():
        if value["duration"] > yellow:
            tmp2.phases[inx]["duration"] = round((tmp2.phases[inx]["duration"] - yellow)/2)
    tllist_cycle.append(tmp2)

    # case 3
    tmp3 = copy.deepcopy(tl)
    tmp3.id = tl.id + '_3'
    tmp3.programID = tl.programID + '_3'
    tmp3.offset = 0
    tllist_async.append(tmp3)

print(tllist[0].show())
print(tllist_element[0].show())
print(tllist_cycle[0].show())
print(tllist_async[0].show())

for tll in tllist_element:
    tphase = TLPhase(tll.shape)
    for i, j in tll.phases.items():
        tphase.append(j["duration"], j["state"])
    print(type(tphase))
    dbm.add_tllight(tll.id, tll.programID, tll.type, tll.offset, tll.shape, phases=tphase)
for tll in tllist_cycle:
    tphase = TLPhase(tll.shape)
    for i, j in tll.phases.items():
        tphase.append(j["duration"], j["state"])
    dbm.add_tllight(tll.id, tll.programID, tll.type, tll.offset, tll.shape, tphase)
for tll in tllist_async:
    tphase = TLPhase(tll.shape)
    for i, j in tll.phases.items():
        tphase.append(j["duration"], j["state"])
    dbm.add_tllight(tll.id, tll.programID, tll.type, tll.offset, tll.shape, tphase)
