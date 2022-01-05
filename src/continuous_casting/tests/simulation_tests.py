from src.continuous_casting.simulation import Simulation
from src.continuous_casting.utils import get_instances
import sys

sys.setrecursionlimit(100000)

instances = get_instances()

instance_names = instances.keys()

for instance in instance_names:
    simulation = Simulation(instances[instance], name=instance.replace("_", " "))
