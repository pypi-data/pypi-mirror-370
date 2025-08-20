import os
from .modules.analysis import clustering_analysis
from .modules.io_utils import save_data

def main(input, output, num_random_nets):
    data = clustering_analysis(input, num_random_nets)
    header = ["Gene name", "Clustering coefficient (input network)"]
    for i in range(num_random_nets):
        header.append("Clustering coefficient (random network "+str(i+1)+")")
    path_to_output = os.path.join(output, "clustering_coefficients.csv")
    save_data(data, header, path_to_output)