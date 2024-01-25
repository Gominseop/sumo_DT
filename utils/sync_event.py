import time
import pandas as pd
import numpy as np
from db_manager import DBManager, DBClient
from datetime import datetime, timedelta

# 값 변환 event
# 기간 관련 thread 또는 process

# 추가 도로를 생성하고 기존 도로의 available을 0으로 수정
# 종료 시그널 이후 변경 대상을 폐기하고 기존 도로를 available 1로 수정

# 영구 변화
# 기존 값을 history로 넘기고 자체를 변경

# 교통량: 태규형이 만든 것에 맞춰서 실시간으로 구성할 수 있는 것처럼 작성

# 도로 변화의 예시는 서울의 돌발 이벤트를 사용

# event를 관리하는 테이블을 사용하여 지속적으로 process를 잡아먹지 않도록 처리

# 일상 sync와 돌발 sync를 구분해서 설명

# event는
ex_event = {
    'o_time': '발생시간',
    'category': '영구 0 vs 일시 + 시간 1 vs 일시 + 트리거 2',
    'e_time': '유지시간, 끝시간',
    'type': '돌발유형, 도로 추가인지 감소인지 등 예시는 추가 감소 하나씩 하자',
    'target': '도로 id',
    'control_type': '통제 방법 (전체 vs 부분), 일단 전체만 처리'
}


def event_process1(event_id, o_time, category, event_type, target, control_type, e_time=None):
    event_insert = (f'INSERT INTO event (`id`, `occur_time`, `category`, `end_time`, `type`, `target`, `control_type`) '
                    f'VALUES ("{event_id}", "{o_time}", {category}, "{e_time}", {event_type}, "{target}", {control_type})')
    dbm.write_query(event_insert)
    print("이벤트 추가 성공", event_id)

    target_update = f'UPDATE road SET `available` = 0 WHERE `id` = "{target}"'
    dbm.write_query(target_update)
    print("대상 업데이트 성공", target)

    target_read = dbm.read_road_from_id(target)[0]
    target_read.id = "tmp_" + target_read.id
    target_read.laneNum12 = target_read.laneNum12 - 1
    target_read.laneNum21 = target_read.laneNum21 - 1
    target_read.available = 1
    dbm.add_road(target_read)
    print("대상 변경 성공", "tmp_" + target_read.id)
    dbm.commit()

    time.sleep(20)
    event1_reset(event_id, target)
    print("이벤트 끝")

def event1_reset(event_id, target):
    sql1 = f'UPDATE road SET `available` = 1 WHERE `id` = "{target}"'
    dbm.write_query(sql1)

    sql2 = f'DELETE FROM road WHERE `id` = "tmp_{target}"'
    dbm.write_query(sql2)

    sql3 = f'DELETE FROM event WHERE `id` = "{event_id}"'
    dbm.write_query(sql3)
    dbm.commit()

def event_process2(event_id, o_time, category, event_type, target, control_type, e_time=None):
    event_insert = (f'INSERT INTO event (`id`, `occur_time`, `category`, `type`, `target`, `control_type`) '
                    f'VALUES ("{event_id}", "{o_time}", {category}, {event_type}, "{target}", {control_type})')
    dbm.write_query(event_insert)
    print("이벤트 추가 성공", event_id)

    target_update = f'UPDATE road SET `laneNum12` = 4, `laneNum21` = 4 WHERE `id` = "{target}"'
    dbm.write_query(target_update)
    print("대상 업데이트 성공", target)
    dbm.commit()

    time.sleep(20)
    event2_reset(event_id, target)
    print("이벤트 처리 완료")

def event2_reset(event_id, target):
    sql1 = f'UPDATE road SET `laneNum12` = 3, `laneNum21` = 3 WHERE `id` = "{target}"'
    dbm.write_query(sql1)

    sql2 = f'DELETE FROM event WHERE `id` = "{event_id}"'
    dbm.write_query(sql2)
    dbm.commit()

def event_process3(event_id, o_time, category, event_type, target, control_type, e_time=None):
    event_insert = (f'INSERT INTO event (`id`, `occur_time`, `category`, `end_time`, `type`, `target`, `control_type`) '
                    f'VALUES ("{event_id}", "{o_time}", {category}, "{e_time}", {event_type}, "{target}", {control_type})')
    dbm.write_query(event_insert)
    print("이벤트 추가 성공", event_id)

    sql = 'SELECT id FROM traffic_light'
    tmp = dbm.read_query(sql)
    tlids = []
    for i in tmp:
        if len(i[0]) > 3 and '_' not in i[0]:
            tlids.append(i[0])

    for j in tlids:
        if target == '0':
            sql = f'UPDATE intersection SET tlLogic = "{j}" WHERE id = "{j}"'
        else:
            sql = f'UPDATE intersection SET tlLogic = "{j}_{target}" WHERE id = "{j}"'
        dbm.write_query(sql)
    dbm.commit()


if __name__ == '__main__':
    dbm = DBManager()
    dbm.initialize_db(
        '127.0.0.1',
        3306,
        'root',
        'filab1020',
        'filab_traffic',
        'utf8'
    )

    control_num = 3

    # test 1: 감소 3->4를 3에서 2로 변경
    if control_num == 1:
        event_id = 'e001'
        o_time = datetime(2024, 1, 22, 18, 10, 10)
        category = 1
        e_time = datetime(2024, 1, 22, 19, 10, 10)
        event_type = 0  # 0: 도로 감소, 1: 도로 추가, 2: 신호 변경 등
        target = '3500007500-3500007900'  # node 3, 4 사이
        control_type = 1  # 0 부분, 1 전체
        event_process1(event_id, o_time, category, event_type, target, control_type, e_time)

    # test 2: 증가 3->4, 3에서 4로 변경
    if control_num == 2:
        event_id = 'e002'
        o_time = datetime(2024, 1, 22, 19, 20, 10)
        category = 0
        event_type = 1  # 0: 도로 감소, 1: 도로 추가, 2: 신호 변경 등
        target = '3500007500-3500007900'  # node 3, 4 사이
        control_type = 1  # 0 부분, 1 전체
        event_process2(event_id, o_time, category, event_type, target, control_type)

    # test 3: traffic_set 변경
    if control_num == 3:
        event_id = 'e003'
        o_time = datetime(2024, 1, 22, 19, 0, 0)
        category = 0
        e_time = datetime(2024, 1, 23, 0, 0, 0)
        event_type = 2  # 0: 도로 감소, 1: 도로 추가, 2: 신호 변경 등
        target = '3'  # traffic 뒤 자리
        control_type = 1  # 0 부분, 1 전체
        event_process3(event_id, o_time, category, event_type, target, control_type, e_time)
