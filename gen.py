import random
import json
import pymysql

RANDOM_SEED = 42


def db_connect(host, port, user, password, db_name, charset):
    db = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db_name,
        charset=charset
    )
    cursor = db.cursor()

    return db, cursor


def generate_tllfile(filename, id, phases, type="static", programID="my_program", offset="0"):
    with open(f"files/network/tllogic/{filename}.tll.xml", "w") as tll:
        tll.write(f'<tlLogic id="{id}" type="{type}" programID="{programID}" offset="{offset}">\n')

        _phases = json.loads(phases)

        for i, phase in json.loads(phases).items():
            tll.write(f'   <phase duration="{phase["duration"]}" state="{phase["state"]}"/>\n')
        tll.write('</tlLogic>')

    return filename, id


def generate_nodfile(filename, id, shape, x="0.0", y="0.0", type="traffic_light", tl=None):
    ids = dict()

    with open(f"files/network/node/{filename}.nod.xml", "w") as nod:
        nod.write(f'<nodes>\n')
        if "traffic" in type:
            nod.write(f'   <node id="{id}" x="{x}" y="{y}" type="{type}" tl="{tl}"/>\n')
        else:
            nod.write(f'   <node id="{id}" x="{x}" y="{y}" type="{type}"/>\n')
        ids[id] = (x, y)

        # in dummy node
        tem_in = {2: [(300, 0), (-300, 0)],
               3: [(0, 300), (300, 0), (-300, 0)],
               4: [(0, 300), (300, 0), (0, -300), (-300, 0)]}
        for i, point in enumerate(tem_in[shape]):
            nod.write(f'   <node id="{id}_{i+1}" x="{float(x)+point[0]}" y="{float(y)+point[1]}" type="priority"/>\n')
            ids[f"{id}_{i+1}"] = (f"{float(x)+point[0]}", f"{float(y)+point[1]}")

        # out dummy node
        tem_out = {2: [(310, 0), (-310, 0)],
               3: [(0, 310), (310, 0), (-310, 0)],
               4: [(0, 310), (310, 0), (0, -310), (-310, 0)]}
        nod.write('\n')
        for i, point in enumerate(tem_out[shape]):
            nod.write(f'   <node id="{id}_{i+51}" x="{float(x)+point[0]}" y="{float(y)+point[1]}" type="priority"/>\n')
            ids[f"{id}_{i + 51}"] = (f"{float(x) + point[0]}", f"{float(y) + point[1]}")

        nod.write('</nodes>')

    return filename, ids


def generate_edgfile(filename, roads):
    # roads = { id: {node1, node2, num, speed, length} }
    ids = []
    ids_in = []
    ids_out = []


def generate_confile():
    pass


def generate_roufile():
    pass


if __name__ == "__main__":
    db, cursor = db_connect(
        "127.0.0.1", 3306, "root", "filab1020", "brl", "utf8"
    )

    cross_id = "0"

    sql = f"SELECT * FROM intersection WHERE id = '{cross_id}'"
    cursor.execute(sql)
    cross_data = cursor.fetchone()
    print("cross_data", cross_data, '\n')

    sql = f"SELECT * FROM traffic_light WHERE id = '{cross_data[6]}'"
    cursor.execute(sql)
    tll_data = cursor.fetchone()
    print("tll_data", tll_data, '\n')

    sql = f"SELECT * FROM intersection_node JOIN intersection_road \
    ON intersection_node.node_id = intersection_road.inter_id AND \
    intersection_node.index = intersection_road.way_id WHERE \
    intersection_node.node_id = '{cross_id}'"
    cursor.execute(sql)
    cross_around_data = cursor.fetchall()
    print("cross_around_data", cross_around_data, '\n')

    cross_traffic = []
    cross_traffic_end = []
    for data in cross_around_data:
        if data[6] == 'in':
            cross_traffic.append(data)
        elif data[6] == 'out':
            cross_traffic_end.append(data)
    cross_traffic = tuple(cross_traffic)
    print("cross_traffic", cross_traffic, '\n')
    cross_traffic_end = tuple(cross_traffic_end)
    print("cross_traffic_end", cross_traffic_end, '\n')

    # tllogic generate
    with open(f"files/network/tllogic/brl.tll.xml", "w") as tll:
        tll.write(f'<tlLogic id="{tll_data[0]}" type="{tll_data[2]}" programID="{tll_data[1]}" offset="0">\n')

        _phase_num = tll_data[3]
        _phases = json.loads(tll_data[4])

        for index, value in _phases.items():
            _phase_info = ''
            for s, d in zip(value['state'], cross_traffic):
                rou = d[9].replace(',', '')
                for r in rou:
                    if r == 'R':
                        _phase_info += 's'
                    elif s == 'R':
                        _phase_info += 'r'
                    elif s == 'Y':
                        _phase_info += 'y'
                    elif s == 'G':
                        _phase_info += 'G'
            tll.write(f'   <phase duration="{value["duration"]}" state="{_phase_info}"/>\n')
        tll.write('</tlLogic>')

    # node generate
    with open(f"files/network/node/brl.nod.xml", "w") as nod:
        nod.write(f'<nodes>\n')
        # cross node
        if "traffic" in cross_data[4]:
            nod.write(
                f'   <node id="{cross_data[0]}" x="{cross_data[2]}" y="{cross_data[3]}" type="{cross_data[4]}" tl="{tll_data[0]}"/>\n\n'
            )
        else:
            nod.write(
                f'   <node id="{cross_data[0]}" x="{cross_data[2]}" y="{cross_data[3]}" type="{cross_data[4]}"/>\n\n'
            )

        # cross around node
        can_id = []
        for ct in cross_traffic:
            nod.write(
                f'   <node id="{f"{ct[0]}_{ct[1]}"}" x="{cross_data[2] + ct[2]}" y="{cross_data[3] + ct[3]}" type="priority"/>\n'
            )
            can_id.append((ct[0], ct[1]))
        nod.write('\n')

        # dummy node
        nod.write(f'   <node id="1" x="{cross_data[2]}" y="{cross_data[3]+500}" type="priority"/>\n')
        nod.write(f'   <node id="2" x="{cross_data[2]+500}" y="{cross_data[3]}" type="priority"/>\n')
        nod.write(f'   <node id="3" x="{cross_data[2]}" y="{cross_data[3]-500}" type="priority"/>\n')
        nod.write(f'   <node id="4" x="{cross_data[2]-500}" y="{cross_data[3]}" type="priority"/>\n\n')

        nod.write(f'   <node id="51" x="{cross_data[2]}" y="{cross_data[3]+510}" type="priority"/>\n')
        nod.write(f'   <node id="52" x="{cross_data[2]+510}" y="{cross_data[3]}" type="priority"/>\n')
        nod.write(f'   <node id="53" x="{cross_data[2]}" y="{cross_data[3]-510}" type="priority"/>\n')
        nod.write(f'   <node id="54" x="{cross_data[2]-510}" y="{cross_data[3]}" type="priority"/>\n')

        nod.write('</nodes>')

    # edge generate
    sql = f"SELECT * FROM road WHERE node1_id = '{cross_data[0]}'"
    cursor.execute(sql)
    road_data = cursor.fetchall()
    print('road_data', road_data, '\n')

    with open(f"files/network/edge/brl.edg.xml", "w") as edg:
        edg.write('<edges>\n')
        # connect around node
        for rd in road_data:
            edg.write(f'   <edge id="{rd[0]}i" from="{rd[0]}" to="{cross_data[0]}" numLanes="{rd[7]}" speed="{rd[8]}" />\n')
            edg.write(f'   <edge id="{rd[0]}o" from="{cross_data[0]}" to="{rd[0]}" numLanes="{rd[6]}" speed="{rd[8]}" />\n\n')

        # connect around dummy
        for i, rd in enumerate(road_data):
            edg.write(f'   <edge id="{i+1}i" from="{i+1}" to="{rd[0]}" numLanes="{rd[7]}" speed="{rd[8]}" />\n')
            edg.write(f'   <edge id="{i+1}o" from="{rd[0]}" to="{i+1}" numLanes="{rd[6]}" speed="{rd[8]}" />\n\n')

        # connect dummy
        edg.write(f'   <edge id="51i" from="1" to="51" numLanes="1" speed="20.000" />\n')
        edg.write(f'   <edge id="51o" from="51" to="1" numLanes="1" speed="20.000" />\n\n')
        edg.write(f'   <edge id="52i" from="2" to="52" numLanes="1" speed="20.000" />\n')
        edg.write(f'   <edge id="52o" from="52" to="2" numLanes="1" speed="20.000" />\n\n')
        edg.write(f'   <edge id="53i" from="3" to="53" numLanes="1" speed="20.000" />\n')
        edg.write(f'   <edge id="53o" from="53" to="3" numLanes="1" speed="20.000" />\n\n')
        edg.write(f'   <edge id="54i" from="4" to="54" numLanes="1" speed="20.000" />\n')
        edg.write(f'   <edge id="54o" from="54" to="4" numLanes="1" speed="20.000" />\n')

        edg.write('</edges>')

    # connection generate
    with open(f"files/network/connection/brl.con.xml", "w") as con:
        con.write('<connections>\n')

        toLaneNum = dict()
        for outw in cross_traffic_end:
            toLaneNum[outw[5]] = outw[7]
        print('toLaneNum', toLaneNum)

        for inw in cross_traffic:
            fromRoadIndex = inw[5]
            fromLaneNum = inw[7]
            laneRoute = inw[9].split(',')

            rIndex = (int(fromRoadIndex) - 1) % 4
            sIndex = (int(fromRoadIndex) + 2) % 4
            lIndex = (int(fromRoadIndex) + 1) % 4

            fromID = f'{cross_data[0]}_{fromRoadIndex}'
            rID = f'{cross_data[0]}_{rIndex}'
            sID = f'{cross_data[0]}_{sIndex}'
            lID = f'{cross_data[0]}_{lIndex}'

            r_now = 0
            s_now = toLaneNum[str(sIndex)] - fromLaneNum
            l_now = toLaneNum[str(lIndex)] - 1

            # 어느 Node 방향이 우 직 좌 인지도 정보가 필요함
            for j, lr in enumerate(laneRoute):
                for r in lr:
                    if r == 'R':
                        con.write(f'   <connection from="{fromID}i" to="{rID}o" fromLane="{j}" toLane="{r_now}"/>\n')
                        r_now += 1
                    elif r == 'S':
                        con.write(f'   <connection from="{fromID}i" to="{sID}o" fromLane="{j}" toLane="{s_now}"/>\n')
                        s_now += 1
                    elif r == 'L':
                        con.write(f'   <connection from="{fromID}i" to="{lID}o" fromLane="{j}" toLane="{l_now}"/>\n')
                        l_now -= 1
            con.write('\n')
        con.write('</connections>\n')

    """
    sql = f"SELECT * FROM intersection_node iNode JOIN intersection_road iRoad \
    ON iNode.node_id = iRoad.inter_id AND iNode.index = iRoad.way_id JOIN \
    road rRoad ON (iNode.node_id, iNode.index) = (rRoad.node1_id, rRoad.node1_index) \
    WHERE iNode.node_id = '{cross_id}'"
    """


