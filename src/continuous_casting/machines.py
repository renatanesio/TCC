from copy import copy
from typing import Dict

import pendulum


class Machines:
    def __init__(self, instance):
        self.__num_machines = len(instance["Machine"])

        self.earliest_available_time = {}
        self.__init_earliest_available_time(instance)

        self.stage = {}
        self.__init_stage(instance)

        self.last_stage = self.stage[self.__num_machines - 1]

        self.current_earliest_available_time = copy(self.earliest_available_time)

        self.__transport_time = {key: {} for key in list(range(self.__num_machines))}
        self.__init_transport_time(instance)

        self.allocation = {key: {"Allocation": [], "StartingTime": [], "EndingTime": []} for key in
                           list(range(0, self.__num_machines))}

    def __init_earliest_available_time(self, instance: Dict):
        """
            Function to initiate dictionary of earliest available time, indexed by machine id
        Args:
            instance: dictionary of instance

        """
        for index, row in instance['Earliest_available_time'].iterrows():
            self.earliest_available_time[row["MachineID"]] = pendulum.from_format(row["EAT"], 'YYYY-MM-DD HH:mm:ss')

    def __init_stage(self, instance: Dict):
        """
            Function to initiate dictionary of stages, indexed by machine id
        Args:
            instance: dictionary of instance

        """
        for index, row in instance['Stage'].iterrows():
            self.stage[row["MachineID"]] = row["StageID"]

    def __init_transport_time(self, instance):
        """
            Function to initiate dictionary of transport time, indexed by first machine
        Args:
            instance: dictionary of instance
        """

        for index, row in instance['Transport_Time'].iterrows():
            transport_line = row["Transport_line"].split("-")
            self.__transport_time[int(transport_line[0])][int(transport_line[1])] = row["Transport_Time"]

        delete_keys = []
        for key in self.__transport_time.keys():
            if self.__transport_time[key] == {}:
                delete_keys.append(key)

        for key in delete_keys:
            del self.__transport_time[key]

    def in_stage(self, h: int):
        """
            Get list of machines from stage h
        Args:
            h: stage

        Returns:
            machines_in_stage: list of int, contains indexes of machines from stage h

        """

        machines_in_stage = []
        for machine_id, stage in self.stage.items():
            if h == stage:
                machines_in_stage.append(machine_id)

        return machines_in_stage

    def allocate(self, charge_index, machine_index, starting_time, ending_time):
        self.allocation[machine_index]["Allocation"].append(charge_index)
        self.allocation[machine_index]["StartingTime"].append(starting_time)
        self.allocation[machine_index]["EndingTime"].append(ending_time)

        self.current_earliest_available_time[machine_index] = ending_time
        self.earliest_available_time[machine_index] = ending_time

    def transport_time(self, previous_machine, next_machine):
        if not previous_machine:

            return 0

        else:
            return self.__transport_time[previous_machine][next_machine]
