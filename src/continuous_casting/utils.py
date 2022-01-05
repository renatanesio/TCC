import os
import pandas as pd


def get_instances():
    """
        Function to get instance data from continuous_casting/data/Instance_* directory
    Returns:
        instances: dictionary of instances
    """
    # Dictionary of instances
    instances = {}

    current_directory = os.getcwd()
    current_directory = current_directory.split("continuous_casting", 1)
    current_directory = current_directory[0] + "continuous_casting"

    # data_directory = os.path.dirname(current_directory)
    data_directory = os.path.join(current_directory, "data")

    # List of paths to each instance
    instance_folders = [f.path for f in os.scandir(data_directory) if f.is_dir() and "Instance_" in f.path]

    # Navigate through instance folders
    for instance_path in instance_folders:

        # Get all csv files from an instance folder
        csv_files = [f for f in os.listdir(instance_path) if
                     os.path.isfile(os.path.join(instance_path, f)) and ".csv" in f]

        # Get instance name, e.g. 'Instance_01'
        instance = os.path.basename(os.path.normpath(instance_path))

        # Add instance to dictionary of instances
        instances[instance] = {}

        for csv_file in csv_files:
            file_path = os.path.join(instance_path, csv_file)
            file = pd.read_csv(file_path)
            instances[instance][csv_file.replace(".csv", "")] = file

    return instances
