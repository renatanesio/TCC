from src.continuous_casting.simulation import Simulation
from src.continuous_casting.utils import get_instances
import sys

sys.setrecursionlimit(100000)

instances = get_instances()

instance_names = list(instances.keys())

instance_data = {'instances': [], 'num_charges': [], 'num_machines': [], 'num_stages': []}

for instance in instance_names:
    simulation = Simulation(instances[instance], name=instance.replace("_", " "))
    instance_data['instances'].append(instance.replace("_", " "))
    instance_data['num_charges'].append(simulation.instance_data['num_charges'])
    instance_data['num_machines'].append(simulation.instance_data['num_machines'])
    instance_data['num_stages'].append(simulation.instance_data['num_stages'])

small_info = {'least_num_charges': {'number': min(instance_data['num_charges']),
                                    'source_instance': instance_names[instance_data['num_charges'].index(
                                        min(instance_data['num_charges']))]},

              'largest_num_charges': {'number': max(instance_data['num_charges']),
                                      'source_instance': instance_names[instance_data['num_charges'].index(
                                          max(instance_data['num_charges']))]},

              'least_num_machines': {'number': min(instance_data['num_machines']),
                                     'source_instance': instance_names[instance_data['num_machines'].index(
                                         min(instance_data['num_machines']))]},

              'largest_num_machines': {'number': max(instance_data['num_machines']),
                                       'source_instance': instance_names[instance_data['num_machines'].index(
                                           max(instance_data['num_machines']))]},

              'least_num_stages': {'number': min(instance_data['num_stages']),
                                   'source_instance': instance_names[instance_data['num_stages'].index(
                                       min(instance_data['num_stages']))]},

              'largest_num_stages': {'number': max(instance_data['num_stages']),
                                     'source_instance': instance_names[instance_data['num_stages'].index(
                                         max(instance_data['num_stages']))]},

              }
