# (C) Quantum Computing Inc., 2024.
import csv

def read_config_file(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

def read_coefficient_file(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        coefficients = [float(x) for x, in reader]
    return coefficients

def read_index_file(filename):
    indices = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for item in reader:
            indices.append([int(x.strip()) for x in item])
    return indices

def write_coefficient_file(filename, coefficients):
    with open(filename, "w") as fp:
        for val in coefficients:
            fp.write(f"{val}\n")

def write_indices_file(filename, indices):
    with open(filename, "w") as fp:
        writer = csv.writer(fp)
        for row in indices:
            writer.writerow(row)

