from src.continuous_casting.machines import Machines
from src.continuous_casting.utils import get_instances

instances = get_instances()

machines_inst_01 = Machines(instances["Instance_01"])
eat_inst_01 = machines_inst_01.earliest_available_time

stage_inst_01 = machines_inst_01.stage

last_stage_inst_01 = machines_inst_01.last_stage

ceat_inst_01 = machines_inst_01.current_earliest_available_time
transport_time_inst_01 = machines_inst_01.transport_time
