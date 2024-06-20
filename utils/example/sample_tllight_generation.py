import pandas as pd
import numpy as np
from element import TLLogic, TLPhase, ICNode, SideNode
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

ics = dbm.read_intersection([
    '3500006301', '3500006700', '3500007500', '3500007900', '3500008000', '3510000200', '3510000250',
    '3510000300', '3510000400', '3510000450', '3510021700', '3510021750', '3510021500', '3510021400',
    '3500065800', '3500065850', '3500062500', '3500062550', '3510021350', '3510021300', '3510021200',
    '3510021250', '3500062100', '3500060600', '3500060650', '3500060660', '3500062400', '3500060100',
    '3500060800', '3500058900', '3500060850', '3500060860', '3500059350', '3500058550', '3500302300',
    '3500051804', '3500051802', '3500007400', '3500007100', '3500006900', '3500058700', '3500006901',
    '3500058500', '3500006600', '3500006650', '3500006660', '3500006800', '3500007300', '3500007350',
    '3500007700', '3500059300', '3500059800', '3500059850'])

# phases = TLPhase(5)
# phases.append(40, "RRgRg")
# phases.append(4, "RRYRY")
# phases.append(25, "RRLRL")
# phases.append(4, "RRrRr")
# phases.append(25, "GRRRR")
# phases.append(4, "YRRRR")
# phases.append(25, "RGRRR")
# phases.append(4, "RYRRR")
# phases.append(25, "RRRGR")
# phases.append(4, "RRRYR")

# dbm.add_tllight('10', 'program_10', 'static', 0, 5, phases)
# dbm.commit()

for i in ics:
    if i.type == "priority":
        continue
    if i.shape == 2:
        phases = TLPhase(2)
        phases.append(20, "GG")
        phases.append(4, "YY")
        phases.append(10, "RR")
        dbm.add_tllight(i.id, f'program_{i.id}', 'static', 0, 2, phases)
    elif i.shape == 3:
        phases = TLPhase(3)
        phases.append(20, "GRR")
        phases.append(4, "YRR")
        phases.append(20, "RGR")
        phases.append(4, "RYR")
        phases.append(20, "RRG")
        phases.append(4, "RRY")
        dbm.add_tllight(i.id, f'program_{i.id}', 'static', 0, 3, phases)
    elif i.shape == 4:
        phases = TLPhase(4)
        phases.append(20, "GRRR")
        phases.append(4, "YRRR")
        phases.append(20, "RGRR")
        phases.append(4, "RYRR")
        phases.append(20, "RRGR")
        phases.append(4, "RRYR")
        phases.append(20, "RRRG")
        phases.append(4, "RRRY")
        dbm.add_tllight(i.id, f'program_{i.id}', 'static', 0, 4, phases)
    elif i.shape == 5:
        phases = TLPhase(5)
        phases.append(20, "GRRRR")
        phases.append(4, "YRRRR")
        phases.append(20, "RGRRR")
        phases.append(4, "RYRRR")
        phases.append(20, "RRGRR")
        phases.append(4, "RRYRR")
        phases.append(20, "RRRGR")
        phases.append(4, "RRRYR")
        phases.append(20, "RRRRG")
        phases.append(4, "RRRRY")
        dbm.add_tllight(i.id, f'program_{i.id}', 'static', 0, 5, phases)
dbm.commit()
