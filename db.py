import pymysql
import json

db = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="filab1020",
    db="brl",
    charset='utf8'
)

cursor = db.cursor()

ph = """{"0": {"duration": 33, "state": "GRRR"}, \
"1": {"duration": 6, "state":"YRRR"}, \
"2": {"duration": 33, "state":"RGRR"}, \
"3": {"duration": 6, "state":"RYRR"}, \
"4": {"duration": 33, "state": "RRGR"}, \
"5": {"duration": 6, "state": "RRYR"}, \
"6": {"duration": 33, "state": "RRRG"}, \
"7": {"duration": 6, "state": "RRRY"}}"""

insert_tl = f"INSERT into traffic_light VALUES ('1', 'tll0', 'static', 4, '{ph}')"

select_tl = f"SELECT * FROM traffic_light"

route = '''SR, LS'''
sql = f"INSERT into intersection_road VALUES ('0', '0', 'in', 2, '{route}')"

sql = f"SELECT * FROM intersection_road"
cursor.execute(sql)
a = cursor.fetchone()
db.commit()

print(a)

b = a[4]
print(b)
print(type(b))

c = b.split(',')
print(c)
print(type(c))
