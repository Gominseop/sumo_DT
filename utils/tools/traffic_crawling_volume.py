import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import time
import datetime
import pandas as pd
import numpy as np


driver = webdriver.Chrome()

url = "https://utis.pohang.go.kr/statistics/traffic01"

driver.get(url)

time.sleep(2)

button = driver.find_element(by=By.XPATH, value='//*[@id="background"]/div[1]/div[3]/div/div/form/button')

# 0: 기타, 1: 포스코대로, 2: 새천년대로, 3: 희망대로
road_name = driver.find_element(by=By.XPATH, value='//*[@id="roadName"]')
road_select = Select(road_name)

rns = ['기타', '포스코대로', '새천년대로', '희망대로']

# 0: 2022, 1: 2023, 2: 2024
year = driver.find_element(by=By.XPATH, value='//*[@id="year"]')
year_select = Select(year)

# month = index + 1
month = driver.find_element(by=By.XPATH, value='//*[@id="month"]')
month_select = Select(month)

# day = index + 1
day = driver.find_element(by=By.XPATH, value='//*[@id="day"]')
day_select = Select(day)

columns = ['road', 'year', 'month', 'day', 'interval',
           0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

# for r in range(4):
#     rn = rns[r]
#     road_select.select_by_index(r)
#     time.sleep(0.2)
#
#     # 2023만 사용
#     year_select.select_by_index(1)
#     time.sleep(0.2)
#
#     for m in range(12):
#         month_select.select_by_index(m)
#         time.sleep(0.2)
#
#         dr = 30
#         if m in [0, 2, 4, 6, 7, 10, 12]:
#             dr = 31
#         elif m == 1:
#             dr = 28
#
#         df = pd.DataFrame(columns=columns)
#         i = 0
#
#         for d in range(dr):
#             day_select.select_by_index(d)
#             time.sleep(0.2)
#
#             button.click()
#             time.sleep(3)
#
#             print(rn, 2023, m+1, d+1)
#
#             table = driver.find_element(by=By.XPATH, value='//*[@id="background"]/div[1]/div[3]/div/div/div/div/table')
#             tbody = table.find_element(by=By.TAG_NAME, value='tbody')
#             rows = tbody.find_elements(By.TAG_NAME, "tr")
#
#             for index, value in enumerate(rows):
#                 row = value.find_elements(by=By.TAG_NAME, value='td')
#
#                 tlist = [rn, 2023, m+1, d+1]
#                 for k in row:
#                     v = k.text
#                     if v == '-' or v == '':
#                         v = 0
#                     elif '>' in v:
#                         pass
#                     else:
#                         v = int(v)
#                     tlist.append(v)
#                 df.loc[i] = tlist
#
#                 i += 1
#
#         df.to_csv(f'datas/{rn}_2023_{m+1}.csv', encoding='cp949', index=False)

# 단일용
r = 1
m = 3

vp = False

rn = rns[r]
road_select.select_by_index(r)
time.sleep(0.2)

# 2023만 사용
year_select.select_by_index(2)
time.sleep(0.2)

month_select.select_by_index(m)
time.sleep(0.2)

dr = 30
if m in [0, 2, 4, 6, 7, 9, 11]:
    dr = 31
elif m == 1:
    dr = 28

df = pd.DataFrame(columns=columns)
i = 0

for d in range(dr):
    vp = False

    day_select.select_by_index(d)
    time.sleep(0.2)

    button.click()
    time.sleep(2)

    print(rn, 2024, m + 1, d + 1)

    table = driver.find_element(by=By.XPATH, value='//*[@id="background"]/div[1]/div[3]/div/div/div/div/table')
    tbody = table.find_element(by=By.TAG_NAME, value='tbody')
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for index, value in enumerate(rows):
        row = value.find_elements(by=By.TAG_NAME, value='td')

        tlist = [rn, 2023, m + 1, d + 1]
        for k in row:
            v = k.text
            if v == '-' or v == '':
                v = 0
            elif '>' in v:
                pass
            elif v == '조회 된 항목이 없습니다':
                vp = True
                break
            else:
                v = int(v)
            tlist.append(v)

        if vp:
            break
        df.loc[i] = tlist
        i += 1
df.to_csv(f'C:/Users/FILAB/Desktop/arrange/5_code/SUMO/sumo_DT/utils/traffic_data/{rn}_2024_{m + 1}.csv', encoding='cp949', index=False)

time.sleep(5)
