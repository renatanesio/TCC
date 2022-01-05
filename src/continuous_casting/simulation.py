from copy import copy
from random import shuffle
from datetime import datetime
import pandas as pd
import plotly.figure_factory as ff
import pytz

from src.continuous_casting.charges import Charges
from src.continuous_casting.machines import Machines


class Simulation:
    def __init__(self, instance, name):
        """
            Initialize current earliest available time (tau_i) for each charge to 0
            and current earliest available time (mu_m) for each machine to the
            earliest available time (et_m). Set stage index (h=1).
        """

        print("Step 1")
        self.name = name
        self.charges = Charges(instance)  # Setting charges
        self.machines = Machines(instance)  # Setting machines
        self.h = 0
        self.__initial_zeta = None
        self.__z1 = 0
        self.__z2 = 0
        self.__z3 = 0

        self.gantt_data = {"Task": [], "Start": [], "Finish": [], "Complete": []}

        self.__step_2()

    def __step_2(self):
        """
           If h < H, where h is stage index and H is the last stage, go to Step 3;
           otherwise, go to Step 8.
       """

        print("Step 2")

        if self.h < self.machines.last_stage:  # If h < H
            self.__step_3()  # Go to step 3

        else:
            self.__step_8()  # Go to stage 8

    def __step_3(self):
        """
            If h = 1, generate a permutation zeta = {zeta(1), zeta(2), ..., zeta(n_1)} for all the charges that
            will be processed in stage h (stage 1) according to the chromosome representation.

            Otherwise, calculate the earliest starting time es_oi of each charge i that will be processed in
            stage h and generate a permutation zeta = (zeta(1), zeta(2), ..., zeta(n_h)) for these charges
            according to the non-decreasing sequence of charge's earliest starting time es_oi.

                The starting time of charge i on a machine m (m ∈ W_h) is s_oim = max{mu_m, tau_i + tt_m'm},
                where machine m' refers to the machine which has been assigned to charge i in stage h_oi-1.

                Then, es_oi can be computed as follows: es_oi = min{s_oim}, m ∈ W_h.
           """

        print("Step 3")

        if self.h == 0:  # Fist stage
            self.__zeta = self.charges.in_stage(self.h)  # Get charges processed in stage h
            shuffle(self.__zeta)  # Get a permutation of zeta

            self.__initial_zeta = copy(self.__zeta)

        else:
            self.__zeta = self.__generate_non_decreasing_sequence()

        self.__step_4()  # Go to step 4

    def __step_4(self):
        """
            If zeta is empty, go to Step 7, otherwise, go to Step 5.
        """
        print("Step 4")

        if not self.__zeta:  # If zeta is empty
            self.__step_7()  # Go to step 7

        else:
            self.__step_5()  # Go to step 5

    def __step_5(self):
        """
               Take the first charge zeta(1) from zeta and allocate it to the machine so that charge zeta(1)
               has the earliest starting time in stage h.

                    If the number of machines that have the same earliest starting time for processing charge zeta(1)
                    is greater than 1, a random assignment will be executed to break the tie.

                    The earliest starting time of charge zeta(1) is computed according to the formula:
                        es_ozeta1 = min{max{mu_m, tau_zeta1+tt_mm}},
                        where tau_zeta1 and mu_m are the current earliest available times
                        of charge zeta(1) and machine m, respectively.

                    Note that the transport time tt_mm = 0 if h = 1.

                    The starting time of charge zeta(1) is s_ozeta1 = es_ozeta1.

                    The ending time of charge zeta(1) is e_ozeta(1) = s_ozeta1 + wt_hzeta1_standard

                    The current earliest available time of machine m* should be updated by mu_m* = e_ozeta_1

                    The current earliest available time of charge zeta(1) should be updated by tau_zeta1 = e_ozeta_1
           """

        print("Step 5")

        zeta1 = self.__zeta[0]  # Take the first charge zeta(1) from

        self.__allocate(zeta1)

        self.__step_6()

    def __step_6(self):
        """
            Remove charge zeta(1) from set zeta, and go to Step 4.
        """

        print("Step 6")
        self.__zeta.pop(0)  # Remove zeta(1)
        self.__step_4()

    def __step_7(self):
        """
            h = h + 1, go to Step 2.
        """
        print("Step 7")

        self.h += 1  # Update h
        self.__step_2()  # Go to Step 2

    def __step_8(self):
        """
            The machine allocation for each charge in the last stage and the charge sequence processed
            by each continuous caster are all predefined.

            Determine starting and ending time for each charge on its predefined machine without considering the
            continuity of casting. The schedule of the charges on each continuous caster m (m ∈ W_H) can be computed by
            the following iterative formulas:

                - s_Oi = max{mu_m, tau_i + tt_mm}
                - e_Oi = s_Oi + ct_mi_sta

                - mu_m = {e_Oi for i ∈ {li(j-1), li(j-1)+2, ..., li(j)-1}} or
                {e_Oi+st for i=li(j)},

            where i ∈ psi_j, j ∈ omega_m.
            """
        print("Step 8")
        self.__allocate_last_stage()

        self.__step_9()

    def __step_9(self):
        """
            For each cast j (j ∈ {1, 2, ..., J}), keep the starting time and ending time of its last charge li(j)
            computed in Step 8 unchanged, and then use the following formulas to adjust the starting times and
            ending times of the other charges in reverse direction:
                - e_Oi = s_oi1+1
                - s_Oi = e_Oi - ct_mi_sta,
            where i ∈ {li(j)-1, ..., li(j-1)+2, li(j-1)+1}
            """
        print("Step 9")

        self.__adjust_casters()

        self.__objective_functions()

        self.plot_gantt()

        print("End of simulation")

    def __adjust_casters(self):
        casters = [machine_index for machine_index, stage in self.machines.stage.items() if
                   stage == self.machines.last_stage]

        for caster in casters:
            last_allocation_index = len(self.machines.allocation[caster]['Allocation']) - 1
            for allocation_index, charge_id in reversed(
                    list(enumerate(self.machines.allocation[caster]['Allocation']))):
                if allocation_index != last_allocation_index:
                    ending_time = self.machines.allocation[caster]['StartingTime'][allocation_index + 1]

                    casting_time = self.charges.cc_processing_time[charge_id]['StandardTime'] * 60
                    starting_time = datetime.timestamp(ending_time) - casting_time
                    starting_time = datetime.fromtimestamp(starting_time, pytz.utc)

                    self.machines.allocation[caster]['StartingTime'][allocation_index] = None
                    self.machines.allocation[caster]['StartingTime'][allocation_index] = starting_time

                    self.machines.allocation[caster]['EndingTime'][allocation_index] = None
                    self.machines.allocation[caster]['EndingTime'][allocation_index] = ending_time

                    index = self.charges.allocation[charge_id]["Allocation"].index(caster)

                    self.charges.allocation[charge_id]["StartingTime"][index] = None
                    self.charges.allocation[charge_id]["StartingTime"][index] = starting_time

                    self.charges.allocation[charge_id]["EndingTime"][index] = None
                    self.charges.allocation[charge_id]["EndingTime"][index] = ending_time

    def __allocate_last_stage(self):
        for cc_machine in self.charges.cc_processing_time["Charge_Sequences"].keys():
            for charge_index in self.charges.cc_processing_time["Charge_Sequences"][cc_machine]:
                previous_machine = self.charges.previous_machine[charge_index]

                machine_ceat = self.machines.current_earliest_available_time[cc_machine]

                machine_tt = self.machines.transport_time(previous_machine, cc_machine)
                charge_ceat = self.charges.current_earliest_available_time[charge_index]
                charge_ceat_and_tt = datetime.timestamp(charge_ceat) + machine_tt * 60
                charge_ceat_and_tt = datetime.fromtimestamp(charge_ceat_and_tt, pytz.utc)

                starting_time = max(machine_ceat, charge_ceat_and_tt)

                process_time = self.charges.cc_processing_time[charge_index]["StandardTime"]

                ending_time = datetime.timestamp(starting_time) + process_time * 60
                ending_time = datetime.fromtimestamp(ending_time, pytz.utc)

                self.charges.allocate(charge_index, cc_machine, starting_time, ending_time)
                self.machines.allocate(charge_index, cc_machine, starting_time, ending_time)

    def __allocate(self, charge_index, pt_type: str = "StandardTime"):
        """
            Allocate charges to machines
        Args:
            charge_index: int, index of charge to allocate
            pt_type: string, "MaxTime", "MinTime" or "StandardTime" (default)
        """
        machines_in_stage = self.machines.in_stage(self.h)

        machines_ceat = {}
        machines_tt = {}
        availability = {}
        previous_machine = self.charges.previous_machine[charge_index]
        charge_ceat = self.charges.current_earliest_available_time[charge_index]

        for machine_index in machines_in_stage:
            machines_ceat[machine_index] = self.machines.current_earliest_available_time[machine_index]
            machines_tt[machine_index] = self.machines.transport_time(previous_machine, machine_index)

            charge_ceat_and_tt = datetime.timestamp(charge_ceat) + machines_tt[machine_index] * 60

            charge_ceat_and_tt = datetime.fromtimestamp(charge_ceat_and_tt, pytz.utc)
            availability[machine_index] = max(charge_ceat_and_tt, machines_ceat[machine_index])

        earliest_machine_available = min(availability, key=availability.get)

        starting_time = availability[earliest_machine_available]

        process_time = self.charges.process_time(charge_index, self.h, pt_type)

        ending_time = datetime.timestamp(starting_time) + process_time * 60
        ending_time = datetime.fromtimestamp(ending_time, pytz.utc)

        self.charges.allocate(charge_index, earliest_machine_available, starting_time, ending_time)
        self.charges.previous_machine[charge_index] = earliest_machine_available

        self.machines.allocate(charge_index, earliest_machine_available, starting_time, ending_time)

    def __generate_non_decreasing_sequence(self):

        charges_in_stage = self.charges.in_stage(self.h)

        machines_in_stage = self.machines.in_stage(self.h)

        starting_times = {}
        eat_charges = {}
        for charge in charges_in_stage:
            starting_times[charge] = {}
            charge_ceat = self.charges.current_earliest_available_time[charge]
            previous_machine = self.charges.previous_machine[charge]
            for machine in machines_in_stage:
                machine_ceat = self.machines.current_earliest_available_time[machine]
                machine_tt = self.machines.transport_time(previous_machine, machine)

                charge_ceat_tt = datetime.timestamp(charge_ceat) + machine_tt * 60
                charge_ceat_tt = datetime.fromtimestamp(charge_ceat_tt, pytz.utc)

                starting_times[charge][machine] = max(charge_ceat_tt, machine_ceat)

            eat_charges[charge] = starting_times[charge][min(starting_times[charge], key=starting_times[charge].get)]

        return sorted(eat_charges, key=eat_charges.__getitem__)

    @property
    def initial_zeta(self):
        return self.__initial_zeta

    def __objective_functions(self, lambda1=1, lambda2=1, lambda3=1):

        self.__calculate_penalty_makespan(lambda1)

        self.__calculate_penalty_waiting_time(lambda2)

        self.__calculate_penalty_deviation_std_processing_time(lambda3)

    @property
    def z1(self):
        return self.__z1

    @property
    def z2(self):
        return self.__z2

    @property
    def z3(self):
        return self.__z3

    def __calculate_penalty_makespan(self, lambda1):
        last_stage = self.machines.last_stage
        last_machines = self.machines.in_stage(last_stage)
        ending_times = [self.machines.allocation[machine]['EndingTime'][-1] for machine in last_machines]
        self.__z1 = lambda1 * datetime.timestamp(max(ending_times))

    def __calculate_penalty_waiting_time(self, lambda2):
        z2 = 0
        for charge, allocation in self.charges.allocation.items():
            last_position = len(allocation['Allocation']) - 1
            for position, machine in enumerate(allocation['Allocation']):
                if position != last_position:
                    next_machine = self.charges.allocation[charge]["Allocation"][position + 1]
                    starting_time_next = datetime.timestamp(allocation["StartingTime"][position + 1])
                    ending_time_current = datetime.timestamp(allocation["EndingTime"][position])
                    transport_time = self.machines.transport_time(machine, next_machine) * 60

                    penalty = starting_time_next - ending_time_current - transport_time

                    z2 += penalty

        self.__z2 = lambda2 * z2

    def __calculate_penalty_deviation_std_processing_time(self, lambda3):
        z3 = 0
        for charge, allocation in self.charges.allocation.items():
            last_position = len(allocation['Allocation']) - 1
            for position, machine in enumerate(allocation['Allocation']):
                starting_time = datetime.timestamp(allocation["StartingTime"][position])
                ending_time = datetime.timestamp(allocation["EndingTime"][position])
                stage = self.charges.cast_plan[charge]['ChargeRoute'][position]

                if position != last_position:
                    process_time = self.charges.process_time(charge, stage, "StandardTime") * 60

                else:
                    process_time = self.charges.cc_processing_time[charge]['StandardTime'] * 60

                penalty = max(0, ending_time - starting_time - process_time) - \
                          min(0, ending_time - starting_time - process_time)

                z3 += penalty

        self.__z3 = lambda3 * z3

    def plot_gantt(self):
        for charge, allocation in self.charges.allocation.items():
            for position, machine in enumerate(allocation['Allocation']):
                self.gantt_data["Task"].append(machine)

                start = self.charges.allocation[charge]['StartingTime'][position]
                self.gantt_data["Start"].append(start)

                end = self.charges.allocation[charge]['EndingTime'][position]
                self.gantt_data["Finish"].append(end)

                duration_minutes = (datetime.timestamp(end) - datetime.timestamp(start)) / 60
                self.gantt_data["Complete"].append(int(duration_minutes))

        gantt_df = pd.DataFrame(self.gantt_data["Task"], columns=['Task'])
        gantt_df = gantt_df.assign(Start=self.gantt_data["Start"])
        gantt_df = gantt_df.assign(Finish=self.gantt_data["Finish"])
        gantt_df = gantt_df.assign(Complete=self.gantt_data["Complete"])

        gantt_df.sort_values(by=['Task'], inplace=True)

        gantt_df["Task"] = gantt_df["Task"].apply(lambda x: f"Machine {x}")
        gantt_df.reset_index(drop=True, inplace=True)

        fig = ff.create_gantt(gantt_df, bar_width=0.4, showgrid_y=True, height=800, colors="Reds", index_col='Complete',
                              show_colorbar=True, group_tasks=True, title=f"Gantt chart - {self.name}")
        fig.show()
