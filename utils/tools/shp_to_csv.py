# -*- coding: utf-8 -*-

import shapefile
import pandas as pd
from pyproj import Proj, transform
import networkx as nx
from queue import Queue

shp_path_node = 'C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/[2023-10-13]NODELINKDATA/MOCT_NODE.shp'
sf_node = shapefile.Reader(shp_path_node, encoding='cp949 ')
shp_path_link = 'C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/[2023-10-13]NODELINKDATA/MOCT_LINK.shp'
sf_link = shapefile.Reader(shp_path_link, encoding='cp949 ')

print('load')

#grab the shapefile's field names
# node
fields_node = [x[0] for x in sf_node.fields][1:]
records_node = sf_node.records()
shps = [s.points for s in sf_node.shapes()] # node has coordinate data.
# link
fields_link = [x[0] for x in sf_link.fields][1:]
records_link = sf_link.records()

print('get field')

#write the records into a dataframe
# node
node_dataframe = pd.DataFrame(columns=fields_node, data=records_node)
#add the coordinate data to a column called "coords"
node_dataframe = node_dataframe.assign(coords=shps)
# link
link_dataframe = pd.DataFrame(columns=fields_link, data=records_link)

print(node_dataframe.loc[1])

print(node_dataframe.shape, link_dataframe.shape)
print(node_dataframe.dtypes)
print(link_dataframe.dtypes)

# Data restriction
sc = {'161': ['인천광역시', '중구'],
      '162': ['인천광역시', '동구'],
      '163': ['인천광역시', '미추홀구'],
      '164': ['인천광역시', '연수구'],
      '165': ['인천광역시', '남동구'],
      '166': ['인천광역시', '부평구'],
      '167': ['인천광역시', '계양구'],
      '168': ['인천광역시', '서구'],
      '169': ['인천광역시', '강화군'],
      '170': ['인천광역시', '옹진군']}

sc = {'350': ['포항시', '남구'],
      '351': ['포항시', '북구']}

df_node = pd.DataFrame()
df_link = pd.DataFrame()

res_node = node_dataframe[node_dataframe['NODE_ID'].str.startswith('161')]
print(res_node)

for reg in sc:
    print(sc[reg][0], sc[reg][1])
    res_node = node_dataframe[node_dataframe['NODE_ID'].str.startswith(reg)].copy()
    res_node.loc[:, 'STATE'] = sc[reg][0]
    res_node.loc[:, 'COUNTY'] = sc[reg][1]
    res_link = link_dataframe[link_dataframe['LINK_ID'].str.startswith(reg)].copy()
    res_link.loc[:, 'STATE'] = sc[reg][0]
    res_link.loc[:, 'COUNTY'] = sc[reg][1]
    df_node = pd.concat([df_node, res_node], ignore_index=True)
    df_link = pd.concat([df_link, res_link], ignore_index=True)

df_node.rename(columns={'NODE_ID': 'Id'}, inplace=True)
df_link.rename(columns={'F_NODE': 'FROM', 'T_NODE': 'TO'}, inplace=True)

print(df_node)

# Change coordinate system
# korea 2000/central belt 2010 (epsg:5186) to wgs84(epsg:4326)
inProj = Proj(init='epsg:5186')
outProj = Proj(init='epsg:4326')
latitude = []
longitude = []
for idx, row in df_node.iterrows():
    x, y = row.coords[0][0], row.coords[0][1]  # korea 2000 좌표계
    print(x, y)
    nx, ny = transform(inProj, outProj, x, y)     # 새로운 좌표계
    latitude.append(ny)
    longitude.append(nx)
df_node['latitude'] = latitude
df_node['longitude'] = longitude
# del df_node['coords'] # delete coords

df_node.to_csv('C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/pohang_node.csv',
               header=True, encoding='utf-8-sig')
df_link.to_csv('C:/Users/FILAB/Desktop/arrange/3_과제/2022-2024BRL/2023년도 2년차/정기 회의/인천/pohang_link.csv',
               header=True, encoding='utf-8-sig')
print('end')

a = Queue()
a.put(1)
b = a.get()