from src.continuous_casting.charges import Charges
from src.continuous_casting.utils import get_instances

instances = get_instances()

charges_inst_01 = Charges(instances["Instance_01"])
cast_plan_inst_01 = charges_inst_01.cast_plan

current_earliest_available_time_inst_01 = charges_inst_01.current_earliest_available_time
previous_machine_inst_01 = charges_inst_01.previous_machine
earliest_starting_time_inst_01 = charges_inst_01.earliest_starting_time
