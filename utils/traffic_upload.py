import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

file_list = os.listdir('datas')
file_dict = {'기타': [],
             '새천년대로': [],
             '포스코대로': [],
             '희망대로': []}

for n in file_list:
    if '기타' in n:
        file_dict['기타'].append(n)
    elif '새천년대로' in n:
        file_dict['새천년대로'].append(n)
    elif '포스코대로' in n:
        file_dict['포스코대로'].append(n)
    elif '희망대로' in n:
        file_dict['희망대로'].append(n)

mapping = pd.read_csv('datas/mapping.csv', encoding='cp949')
map_dict = {'기타': mapping[mapping['road'] == '기타'],
            '새천년대로': mapping[mapping['road'] == '새천년대로'],
            '포스코대로': mapping[mapping['road'] == '포스코대로'],
            '희망대로': mapping[mapping['road'] == '희망대로']}

for k, v in map_dict.items():
    if v.empty:
        continue

    for fn in file_dict[k]:
        fdf = pd.read_csv(f'datas/{fn}', encoding='cp949')
        jdf = pd.merge(left=fdf, right=v, how="inner", on="interval")
        for idx, row in jdf.iterrows():
            sql = ''
            week = 0
            dt1 = datetime(2023, 1, 1)
            dt2 = datetime(row["year"], row["month"], row["day"])
            a = dt2-dt1
            if a.days % 7 == 5:
                week = 1
            elif a.days % 7 == 6:
                week = 2

            if row['type'] == 0:
                sql = (f'INSERT INTO traffic_history (`year`, `month`, `day`, `node_id`, `index`, `direction`, `week`, `type`, '
                       f'`00`, `01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `11`, '
                       f'`12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`) '
                       f'VALUES ({row["year"]}, {row["month"]}, {row["day"]}, "{row["node_id"]}", {row["index"]}, '
                       f'{row["direction"]}, {week}, 0, {row["0"]}, {row["1"]}, {row["2"]}, {row["3"]}, {row["4"]}, {row["5"]}, '
                       f'{row["6"]}, {row["7"]}, {row["8"]}, {row["9"]}, {row["10"]}, {row["11"]}, {row["12"]}, '
                       f'{row["13"]}, {row["14"]}, {row["15"]}, {row["16"]}, {row["17"]}, {row["18"]}, {row["19"]}, '
                       f'{row["20"]}, {row["21"]}, {row["22"]}, {row["23"]})')

            elif row['type'] == 1:
                sql = (f'INSERT INTO traffic_history (`year`, `month`, `day`, `road_id`, `direction`, `week`, `type`, '
                       f'`00`, `01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `11`, '
                       f'`12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`) '
                       f'VALUES ({row["year"]}, {row["month"]}, {row["day"]}, "{row["road_id"]}", {row["direction"]}, '
                       f'{week}, 1, {row["0"]}, {row["1"]}, {row["2"]}, {row["3"]}, {row["4"]}, {row["5"]}, '
                       f'{row["6"]}, {row["7"]}, {row["8"]}, {row["9"]}, {row["10"]}, {row["11"]}, {row["12"]}, '
                       f'{row["13"]}, {row["14"]}, {row["15"]}, {row["16"]}, {row["17"]}, {row["18"]}, {row["19"]}, '
                       f'{row["20"]}, {row["21"]}, {row["22"]}, {row["23"]})')
            dbm.write_query(sql)
        dbm.commit()
