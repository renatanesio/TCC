from typing import Dict
import pendulum


class Charges:
    def __init__(self, instance: Dict):
        """
            Initialize Charges attributes
        Args:
            instance: dictionary of instance
        """

        self.__num_charges = len(instance["Cast_plan"])

        self.cast_plan = {}
        self.__init_cast_plan(instance)

        self.last_stage = self.cast_plan[1]["ChargeRoute"][-1]

        self.current_earliest_available_time = {key: pendulum.datetime(1980, 1, 1, 0, 0) for key in
                                                list(range(1, self.__num_charges + 1))}

        self.previous_machine = {key: None for key in list(range(1, self.__num_charges + 1))}

        self.earliest_starting_time = {key: [] for key in list(range(1, self.__num_charges + 1))}

        self.__non_cc_processing_time = None
        self.__init_non_cc_processing_time(instance)

        self.cc_processing_time = None
        self.__init_cc_processing_time(instance)

        self.allocation = {key: {"Allocation": [], "StartingTime": [], "EndingTime": []} for key in
                           list(range(1, self.__num_charges + 1))}

    def __init_cast_plan(self, instance: Dict):
        """
            Function to initiate dictionary of cast plan

            cast_plan: dictionary of cast information, indexed by charge index
                └── CC: machine index of the predefined continuous caster
                └── CastID: cast index
                └── ChargeRoute: stage route of this charge, which is composed of stage index

        Args:
            instance: dictionary of instance

        """
        for index, row in instance["Cast_plan"].iterrows():
            self.cast_plan[row["ChargeID"]] = {"CC": row["CC"],
                                               "ChargeRoute": [int(item) for item in row["ChargeRoute"].split("-")]}

    def __init_non_cc_processing_time(self, instance: Dict):
        """
            Function to initiate dictionary of cast non_cc_processing_time

            non_cc_processing_time: dictionary of processing time in non-continuous casting stage,
                indexed by charge index and StageID
                    └── MinTime: minimum processing time
                    └── Standard_Time: standard processing time
                    └── MaxTime: maximum processing time
        Args:
            instance: dictionary of instance


        """
        self.__non_cc_processing_time = {key: {} for key in list(range(1, self.__num_charges + 1))}

        for index, row in instance["nonCC_Processing_Time"].iterrows():
            if row["ChargeID"] in self.__non_cc_processing_time.keys():
                self.__non_cc_processing_time[row["ChargeID"]][row["StageID"]] = {"MinTime": row["MinTime"],
                                                                                  "StandardTime": row["Standard_Time"],
                                                                                  "MaxTime": row["MaxTime"]}

    def __init_cc_processing_time(self, instance: Dict):
        """
            Function to initiate dictionary of cast non_cc_processing_time

            cc_processing_time: dictionary of processing time in non-continuous casting stage,
                indexed by charge index
                    └── MinTime: minimum processing time
                    └── Standard_Time: standard processing time
                    └── MaxTime: maximum processing time
        Args:
            instance: dictionary of instance

        Returns:

        """
        self.cc_processing_time = {key: {} for key in list(range(1, self.__num_charges + 1))}
        self.cc_processing_time["Charge_Sequences"] = {}

        for index, row in instance["CC_Processing_Time"].iterrows():
            if row["ChargeID"] in self.cc_processing_time:
                if row["CCID"] not in self.cc_processing_time["Charge_Sequences"]:
                    self.cc_processing_time["Charge_Sequences"][row["CCID"]] = []

                self.cc_processing_time["Charge_Sequences"][row["CCID"]].append(row["ChargeID"])

                self.cc_processing_time[row["ChargeID"]] = {"MinTime": row["MinTime"],
                                                            "StandardTime": row["Standard_Time"],
                                                            "MaxTime": row["MaxTime"]}

    def in_stage(self, h: int):
        """
            Get list of charges processed in stage h
        Args:
            h: stage

        Returns:
            charges_in_stage: list of int, contains indexes of charges processed in stage h

        """

        charges_in_stage = []
        for charge, cast_plan in self.cast_plan.items():
            if h in cast_plan["ChargeRoute"]:
                charges_in_stage.append(charge)

        return charges_in_stage

    def allocate(self, charge_index, machine_index, starting_time, ending_time):
        self.allocation[charge_index]["Allocation"].append(machine_index)
        self.allocation[charge_index]["StartingTime"].append(starting_time)
        self.allocation[charge_index]["EndingTime"].append(ending_time)

        self.current_earliest_available_time[charge_index] = ending_time

    def process_time(self, charge_index, stage, pt_type: str = "StandardTime"):
        if stage == self.last_stage:
            return self.cc_processing_time[charge_index][pt_type]

        else:
            return int(self.__non_cc_processing_time[charge_index][stage][pt_type])
