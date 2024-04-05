import pandas as pd
import numpy as np
from decimal import Decimal

input_path = "C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/pohang_target_node.csv"

data = pd.read_csv(input_path, encoding='cp949')#, sep="\t")
data = data[:63]
print(data)

coords_x = []
coords_y = []

for idx, ser in data.iterrows():
    coord = ser["coords"]
    coord_x, coord_y = coord[2:-2].split(', ')
    coord_x = round(Decimal(coord_x), 4)
    coord_y = round(Decimal(coord_y), 4)
    print(coord_x, coord_y)
    coords_x.append(coord_x)
    coords_y.append(coord_y)

data = data.assign(coords_x=coords_x)
data = data.assign(coords_y=coords_y)
print(data)

out_path = "C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/pohang_target_node_arrange.csv"
data.to_csv(out_path, index_label=False, index=False, encoding='cp949')
