import pandas as pd
import numpy as np
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

speed_answer = pd.read_csv("speed_answer.csv", encoding="cp949")

sql = "SELECT `id`, `speed` FROM road"
re = dbm.read_query(sql)
max_speed = {}
for r in re:
    max_speed[r[0]] = int(r[1])

new_column = []
for i, d in speed_answer.iterrows():
    new_column.append(max_speed[d["road"]])

speed_answer["max_speed"] = new_column
speed_answer["speed_ratio"] = round(speed_answer["speed"]/speed_answer["max_speed"], 2)

speed_answer.to_csv("speed_answer_with_ratio.csv", encoding="cp949", index=False)
