import os
import time
from utils.sumo_xml import SUMOGenerator
from utils.db_manager import DBManager

HOME_PATH = os.getcwd()
print(HOME_PATH)

dbm = DBManager()
dbm.initialize_db('localhost', 3306, 'brl_manager', 'filab1020', 'brl_seoul', 'utf8')

start = 1
end = 9

icids = [f"0{i}" for i in range(start, end+1)]
icids.append('10')
print(icids)
ics = dbm.read_intersection(icids)
print(ics)

tlid = [f"0{i}" for i in range(start, end+1)]
tlid.append('10')
tls = dbm.read_tllight(tlid)

roads = dbm.read_road_from_ic(icids)

sg = SUMOGenerator()
for ic in ics:
    sg.add_intersection_by_node(ic)
for tl in tls:
    sg.add_tllogic_by_tl(tl)
for road in roads:
    sg.add_road_by_edge(road)
# for output in outputs:
#     sg.add_addition_by_output(output)

test_path = 'dummy'
test_base_name = f'dummy{start}{end+1}'

sg.generate_node_file(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.nod.xml').replace('\\', '/'))
sg.generate_edge_file(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.edg.xml').replace('\\', '/'))
sg.generate_connection_file(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.con.xml').replace('\\', '/'))
sg.generate_tll_file(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.tll.xml').replace('\\', '/'))

# sg.generate_addition_file(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.add.xml').replace('\\', '/'),
#                           os.path.join(HOME_PATH, f'{test_path}/{test_base_name}').replace('\\', '/'))

sg.make_netccfg(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.netccfg').replace('\\', '/'),
                os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.net.xml').replace('\\', '/'))
sg.generate_net_file()

sg.generate_route_file(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.net.xml').replace('\\', '/'),
                       os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.rou.xml').replace('\\', '/'),
                       end=600,
                       period=1,
                       fringe_factor=40
                       )

sg.make_sumocfg(os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.sumocfg').replace('\\', '/'),
                os.path.join(HOME_PATH, f'{test_path}/{test_base_name}.rou.xml').replace('\\', '/'),
                0, 600)
                #summary=os.path.join(HOME_PATH, f'{test_path}/{test_base_name}_summary.xml').replace('\\', '/'),
                #queue=os.path.join(HOME_PATH, f'{test_path}/{test_base_name}_queue.xml').replace('\\', '/'))

start = time.time()
#sg.run_sumocfg(print_out=True)
print('spend time: ', time.time() - start)

#dbm.add_result(sg.output_id, sg.result_paths)
#dbm.commit()
