import os
import sys
from datetime import datetime, time, timedelta
from db_manager import DBManager
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.environ['SUMO_HOME'])
print(os.environ['SUMO_HOME'])

from sumolib import checkBinary
import sumolib
import traci


def real_mirroring(step, red, stime):
    """
    
    :param step: 현 step
    :param red: 전적색 시간
    :param stime: 기준 시간
    :return: 
    """
    # ptime = datetime.now() # 현재 시간
    ptime = datetime(2024, 3, 11, 9, 5, 0) + timedelta(seconds=10)

    dbm = DBManager()
    dbm.initialize_db('localhost', 3306, 'root', 'password', 'filab_traffic', 'utf8')

    tllist = traci.trafficlight.getIDList()  # --> 적색
    db_tls_list = dbm.read_tllight(tllist)
    db_tls_dict = {}
    for tl in db_tls_list:
        db_tls_dict[tl.id] = tl

    tl_store = {}
    simulation_time = traci.simulation.getTime()
    for tl in tllist:
        # 현재 정보
        pre_state = traci.trafficlight.getRedYellowGreenState(tl)
        pre_program_id = traci.trafficlight.getProgram(tl)
        pre_program = traci.trafficlight.getAllProgramLogics(tl)[-1] # program이 많을 경우 기본값은 마지막꺼
        pre_time = traci.trafficlight.getNextSwitch(tl) - simulation_time
        pre_phase = traci.trafficlight.getPhase(tl)

        # 기준 정보
        db_program = db_tls_dict[tl].program_list[pre_program_id]
        gap = int((ptime-stime).seconds) % db_program.period
        # gap 만큼 추가 진행
        # 전체 phase에서 현재 phase를 찾고 순차 이동

        if gap < pre_time:
            pre_time = pre_time - gap
        elif gap >= pre_time:
            last = len(pre_program.phases) - 1
            idx = pre_phase + 1 if pre_phase < last else 0
            remain = gap - pre_time
            phases = pre_program.phases
            while True:
                remain = remain - phases[idx].duration
                if remain >= 0:
                    pass
                elif remain < 0:
                    pre_time = -remain
                    pre_phase = idx
                    traci.trafficlight.setPhase(tl, idx)
                    break
                if idx == last:
                    idx = 0
                else:
                    idx += 1

        tl_store[tl] = [pre_program_id, pre_phase, pre_time]
        traci.trafficlight.setRedYellowGreenState(tl, "r" * len(pre_state))
    # traci.vehicle.add() # 차량 추가
    # traci.route.add() # 경로 추가

    ns = step
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if ns == step + red - 1:
            for tl in tllist:
                traci.trafficlight.setProgram(tl, tl_store[tl][0])
                traci.trafficlight.setPhase(tl, tl_store[tl][1])
                traci.trafficlight.setPhaseDuration(tl, tl_store[tl][2])  # 한번만 남은 시간을 줄이는 것으로 적용됨
                ns += 1
            continue
        ns += 1
    # signal을 실제 시간만큼 shift
    # offset은 일반적인 경우로 실질적으로는 해당 signal 패턴으로 변한 직후에 대한 정보가 들어가게됨
    # 8시에 변하고 8시 10분부터 시뮬레이션을 진행한다면 10분만큼 진행한 상황에 대해 들어가야함
    return ns


sumoBinary = "/path/to/sumo-gui"
sumoCmd = ["sumo-gui", "-c", "test_2.sumocfg", "--tripinfo-output", "tripinfo.xml"]
traci.start(sumoCmd)

# traci.trafficlight.setPhase("3500006301", 2)
# traci.trafficlight.getAllProgramLogics("3500006301")  # 전체 logic 획득, tuple
# traci.trafficlight.getPhase("3500006301")  # phase id를 가져옮
# traci.trafficlight.getProgram("3500006301")  # 기본적으로 첫 프로그램은 xml의 가장 마지막
# traci.trafficlight.getAllProgramLogics("3500006301") # 모든 프로그램 목록, 상세 포함

# traci.trafficlight.getNextSwitch('3500006301') - nt  # 현재 신호의 남은 시간

# subscription
# 작성 중

# traci.trafficlight.setProgram("3500006301", "program_3500006301")

# traci.trafficlight.getPhase("3500006301") # phases는 currentPhaseIndex를 return

step = 0
step = real_mirroring(step, 150, datetime(2024, 3, 11, 9, 5, 0))

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    step += 1

traci.close()
sys.stdout.flush()
