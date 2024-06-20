import pandas as pd
import numpy as np
from element import TLLogic, TLPhase, ICNode, SideNode
from db_manager import DBManager, DBClient

dbm = DBManager()
dbm.initialize_db(
    '127.0.0.1',
    3306,
    'root',
    'password',
    'filab_traffic',
    'utf8'
)

name = ["희망대로", "새천년대로", "포스코대로"]
t = 1

out_data = pd.DataFrame(columns=["date", "time", "road", "volume"])
j = 0


for t in range(3):
    target = pd.read_csv(f"traffic_data/{name[t]}_대상.csv", encoding="cp949")
    data_volume = pd.read_csv(f"traffic_data/{name[t]}_2024_4.csv")

    for idx, v in data_volume.iterrows():
        y = v["year"]
        m = v["month"]
        d = v["day"]
        interval = v["interval"]
        volume = [v["0"], v["1"], v["2"], v["3"], v["4"], v["5"], v["6"], v["7"], v["8"], v["9"], v["10"], v["11"],
                  v["12"], v["13"], v["14"], v["15"], v["16"], v["17"], v["18"], v["19"], v["20"], v["21"], v["22"], v["23"]]

        value = target[target["segment"] == interval]
        if not value.empty:
            ids = value["id"].values[0].split(';')
            if type(value["ratio"].values[0]) == np.int64:
                ratios = [value["ratio"].values[0]]
            else:
                ratios = value["ratio"].values[0].split(';')
            for k, i in enumerate(ids):
                dbd = []
                for ti, vol in enumerate(volume):
                    dbd.append((f"{y}-{m}-{d} {ti}:00:00", i, 1, int(int(vol)*float(ratios[k])), 0, 3600))
                    out_data.loc[j] = (d, ti, i, int(vol))
                    j += 1

                sql = f"INSERT INTO traffic_copy VALUES {str(dbd)[1:-1]}"
                dbm.write_query(sql)
        else:
            continue

dbm.commit()
out_data.to_csv(f'C:/Users/FILAB/Desktop/arrange/5_code/SUMO/sumo_DT/utils/traffic_data/교통량_답3.csv', encoding='cp949', index=False)
