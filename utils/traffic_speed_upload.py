import pandas as pd
import numpy as np
from element import TLLogic, TLPhase, ICNode, SideNode
from db_manager import DBManager, DBClient

dbm = DBManager()
dbm.initialize_db(
    '127.0.0.1',
    3306,
    'root',
    'filab1020',
    'filab_traffic',
    'utf8'
)

name = ['동해안로', '새천년대로', '중앙로', '중흥로', '포스코대로', '희망대로']

target = pd.read_csv(f"traffic_data/속도_대상.csv", encoding="cp949")

data_volume = pd.read_csv(f"traffic_data/속도_2024_4.csv", encoding="cp949")

out_data = pd.DataFrame(columns=["date", "time", "road", "speed"])
j = 0

for idx, v in data_volume.iterrows():
    y = v["year"]
    m = v["month"]
    d = v["day"]
    interval = v["interval"]
    speed = [v["0"], v["1"], v["2"], v["3"], v["4"], v["5"], v["6"], v["7"], v["8"], v["9"], v["10"], v["11"],
              v["12"], v["13"], v["14"], v["15"], v["16"], v["17"], v["18"], v["19"], v["20"], v["21"], v["22"],
              v["23"]]

    value = target[target["segment"] == interval]
    if not value.empty:
        ids = value["id"].values[0].split(';')
        for i in ids:
            dbd = []
            for ti, vol in enumerate(speed):
                out_data.loc[j] = (d, ti, i, int(vol))
                j += 1
                sql = (f'UPDATE traffic_copy SET `speed` = {int(vol)} '
                       f'WHERE (`datetime`, `road_id`) = ("{y}-{m}-{d} {ti}:00:00", "{i}")')
                dbm.write_query(sql)
    else:
        continue

dbm.commit()
out_data.to_csv(f'C:/Users/FILAB/Desktop/arrange/5_code/SUMO/sumo_DT/utils/traffic_data/속도_답3.csv', encoding='cp949', index=False)
