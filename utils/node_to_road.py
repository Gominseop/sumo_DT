import pandas as pd
import numpy as np


nodes = {1: 3500006301, 2: 3500006700, 3: 3500007500, 4: 3500007900, 5: 3500008000, 6: 3510000200, 8: 3510000300,
         9: 3510000400, 15: 3510021700, 16: 3510021500, 17: 3510021400, 18: 3500065800, 20: 3500062500, 22: 3500007700,
         26: 3500007100, 27: 3500006901, 28: 3500006600, 31: 3500007300, 34: 3510021200, 36: 3500060800, 38: 3500058900,
         39: 3500302300, 40: 3500051802, 43: 3500060600, 45: 3500058500, 48: 3500059300, 50: 3510021300, 51: 3500062100,
         52: 3500059800, 55: 3500060100, 56: 3500058700, 57: 3500051804, 58: 3500062400, 59: 3500006900, 61: 3500006800,
         25: 3500007400}

nodes = {v: k for k, v in nodes.items()}

road_path = "C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/pohang_link.csv"

raw_roads = pd.read_csv(road_path, encoding='cp949', sep="\t")
print(raw_roads)

node_ids = list(nodes.keys())
print(node_ids)
target_roads = raw_roads[raw_roads["FROM"].isin(node_ids) | raw_roads["TO"].isin(node_ids)]
print(target_roads)

target_roads = target_roads.assign(FROM_ID=100)
target_roads = target_roads.assign(TO_ID=100)
print(target_roads)

for idx, ser in target_roads.iterrows():
    if ser["FROM"] in node_ids:
        target_roads.loc[idx, "FROM_ID"] = nodes[ser["FROM"]]
    if ser["TO"] in node_ids:
        target_roads.loc[idx, "TO_ID"] = nodes[ser["TO"]]
print(target_roads)

out_path = "C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/pohang_target_link_final.csv"
target_roads.to_csv(out_path, encoding='cp949')
