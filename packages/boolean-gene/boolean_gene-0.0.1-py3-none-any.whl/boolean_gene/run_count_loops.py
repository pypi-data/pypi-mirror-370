import os
from .modules.analysis import count_loops
from .modules.io_utils import save_data

def main(input, output, num_random_nets):
    data = count_loops(input, num_random_nets)
    header = ["Number of genes in loop", "Count (input network)"]
    for i in range(num_random_nets):
        header.append("Count (random network "+str(i+1)+")")
    path_to_output = os.path.join(output, "loop_counts.csv")
    save_data(data, header, path_to_output)