import os
from .modules.analysis import count_attractors
from .modules.io_utils import save_data

def main(input, output, num_random_nets, num_simulations_per_network, timesteps_per_simulation):
    data = count_attractors(input, num_random_nets, num_simulations_per_network, timesteps_per_simulation)
    header = ["Number of genes in oscillator", "Frequency (input network)"]
    for i in range(num_random_nets):
        header.append("Frequency (random network "+str(i+1)+")")
    path_to_output = os.path.join(output, "stability_analysis.csv")
    save_data(data, header, path_to_output)