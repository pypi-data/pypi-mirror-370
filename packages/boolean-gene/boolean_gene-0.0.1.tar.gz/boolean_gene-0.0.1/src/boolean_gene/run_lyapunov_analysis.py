import os
from .modules.analysis import lyapunov_analysis
from .modules.io_utils import save_data

def main(input, output, num_random_nets, num_simulations_per_network, timesteps_per_simulation):
    data = lyapunov_analysis(input, num_random_nets, num_simulations_per_network, timesteps_per_simulation)
    header = ["", "Input network"]
    for i in range(num_random_nets):
        header.append("Random network "+str(i+1))
    path_to_output = os.path.join(output, "lyapunov_analysis.csv")
    save_data(data, header, path_to_output)