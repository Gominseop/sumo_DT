import os
import sys
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.environ['SUMO_HOME'])
print(os.environ['SUMO_HOME'])

from sumolib import checkBinary
import sumolib
import traci


def stack_car(step, red):
    tllist = traci.trafficlight.getIDList()  # --> 적색
    tl_store = {}
    simulation_time = traci.simulation.getTime()
    for tl in tllist:
        pre_state = traci.trafficlight.getRedYellowGreenState(tl)
        pre_program = traci.trafficlight.getProgram(tl)
        pre_time = traci.trafficlight.getNextSwitch(tl) - simulation_time
        pre_phase = traci.trafficlight.getPhase(tl)
        tl_store[tl] = [pre_program, pre_phase, pre_time]
        traci.trafficlight.setRedYellowGreenState(tl, "r" * len(pre_state))
    print(tl_store)

    # traci.vehicle.add() # 차량 추가
    # traci.route.add() # 경로 추가

    ns = step
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(ns)

        if ns == step + red:
            for tl in tllist:
                traci.trafficlight.setProgram(tl, tl_store[tl][0])
                traci.trafficlight.setPhase(tl, tl_store[tl][1])
                traci.trafficlight.setPhaseDuration(tl, tl_store[tl][2])  # 한번만 남은 시간을 줄이는 것으로 적용됨
            break
        ns += 1

    # signal을 실제 시간만큼 shift
    # offset은 일반적인 경우로 실질적으로는 해당 signal 패턴으로 변한 직후에 대한 정보가 들어가게됨
    # 8시에 변하고 8시 10분부터 시뮬레이션을 진행한다면 10분만큼 진행한 상황에 대해 들어가야함

    return ns




sumoBinary = "/path/to/sumo-gui"
sumoCmd = ["sumo-gui", "-c", "test_1.sumocfg", "--tripinfo-output", "tripinfo.xml"]
traci.start(sumoCmd)

# traci.trafficlight.setPhase("3500006301", 2)
# traci.trafficlight.getAllProgramLogics("3500006301")  # 전체 logic 획득, tuple
# traci.trafficlight.getPhase("3500006301")  # phase id를 가져옮
# traci.trafficlight.getProgram("3500006301")  # 기본적으로 첫 프로그램은 xml의 가장 마지막
tmp = traci.trafficlight.getAllProgramLogics("3500006301")[0]
print(tmp)

# traci.trafficlight.getNextSwitch('3500006301') - nt  # 현재 신호의 남은 시간

# subscription
# 작성 중

# traci.trafficlight.setProgram("3500006301", "program_3500006301")

# traci.trafficlight.getPhase("3500006301") # phases는 currentPhaseIndex를 return

step = 0
step = stack_car(step, 50)

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    step += 1

traci.close()
sys.stdout.flush()
