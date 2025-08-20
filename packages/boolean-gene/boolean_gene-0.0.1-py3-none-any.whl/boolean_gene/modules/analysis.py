import numpy as np
from tqdm import tqdm
from .BooleanNetwork import BooleanNetwork
from .io_utils import read_expressions_from_txt, infer_external_from_expressions
from .regenerate_network import regenerate_network
from .logic_processing import dict_to_list
from typing import Tuple

def count_attractors(expressions_file: str, num_random_nets: int=100, num_simulations_per_network:int=1000, timesteps_per_simulation:int=100) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Quantifies the fraction of simulations of a gene network that yield an attractor and that yield a fixed point. 
    Does the same analysis averaged over multiple randomly-generated networks.
    """
    def quantify_attractor_lengths(attractors_dict):
        out = dict()
        for key, val in attractors_dict.items():
            if len(key) not in out:
                out[len(key)] = val
            else:
                out[len(key)] += val
        return out

    expressions = read_expressions_from_txt(expressions_file)
    external = infer_external_from_expressions(expressions)

    net = BooleanNetwork(expressions, external)
    attractors_actual = net.find_attractors(n=num_simulations_per_network, t=timesteps_per_simulation, stable_only=False)
    attractors_actual_lens = quantify_attractor_lengths(attractors_actual)
    out = dict_to_list(attractors_actual_lens)/num_simulations_per_network
    matrix_length = len(out)

    if num_random_nets > 0:
        print("Random network generation")
    for _ in tqdm(range(num_random_nets)):
        
        new = regenerate_network(net, True, True, True)
        attractors_random = new.find_attractors(n=num_simulations_per_network, t=timesteps_per_simulation, stable_only=False)
        attractors_random_lens = quantify_attractor_lengths(attractors_random)
        f_attractors_random = dict_to_list(attractors_random_lens)/num_simulations_per_network
        while len(f_attractors_random) > matrix_length:
            if len(np.shape(out)) > 1:
                out = np.concatenate((out, np.zeros(shape=(len(out),1))), axis=1)
            else:
                out = np.append(out, 0)
            matrix_length += 1
        while len(f_attractors_random) < matrix_length:
            f_attractors_random = np.append(f_attractors_random, 0)
        out = np.vstack((out, f_attractors_random))

    out = np.vstack((np.array(range(1,matrix_length+1)), out))
    return out.T

def lyapunov_analysis(expressions_file: str, num_random_nets:int = 100, num_simulations_per_network:int=1000, timesteps_per_simulation:int=100):

    expressions = read_expressions_from_txt(expressions_file)
    external = infer_external_from_expressions(expressions)
    
    net = BooleanNetwork(expressions, external)
    fixedpoints_actual = net.find_attractors(n=num_simulations_per_network, t=timesteps_per_simulation, stable_only=True)
    f_fixedpoints_actual = sum(fixedpoints_actual.values())/num_simulations_per_network
    f_lyapunov_actual = 0

    for fixedpoint, occurrences in fixedpoints_actual.items():
        is_lyapunov_stable = net.lyapunov_stable(fixedpoint[0], 1, timesteps_per_simulation)
        if is_lyapunov_stable:
            f_lyapunov_actual += occurrences

    f_lyapunov_actual /= num_simulations_per_network
    out = np.array([f_fixedpoints_actual, f_lyapunov_actual])
    for _ in tqdm(range(num_random_nets)):
        
        new = regenerate_network(net, True, True, True)
        fixedpoints_random = new.find_attractors(n=num_simulations_per_network, t=timesteps_per_simulation, stable_only=True)
        f_fixedpoints_random = sum(fixedpoints_random.values())/num_simulations_per_network
        f_lyapunov_random = 0

        for fixedpoint, occurrences in fixedpoints_random.items():
            is_lyapunov_stable = net.lyapunov_stable(fixedpoint[0], 1, timesteps_per_simulation)
            if is_lyapunov_stable:
                f_lyapunov_random += occurrences

        f_lyapunov_random /= num_simulations_per_network
        out = np.vstack((out, np.array([f_fixedpoints_random, f_lyapunov_random])))

    out = np.vstack(np.array(["Frequency(fixed points)", "Frequency(Lyapunov-stable fixed points)"]))
    return out.T

def count_loops(expressions_file, num_random_nets=100):
    """
    Count number of loops in each network, as well as mean loop size and 
    fraction of nodes in network participating in a loop. Also generate random 
    networks and record the same statisticsfor them.
    """
    def quantify_cycle_lengths(cycle_lengths_lst):
        out = dict()
        for elt in cycle_lengths_lst:
            if elt not in out:
                out[elt] = 1
            else:
                out[elt] += 1
        return out

    expressions = read_expressions_from_txt(expressions_file)
    external = infer_external_from_expressions(expressions)
    net = BooleanNetwork(expressions, external)
    net_cycles = net.find_cycles()
    net_cycle_lengths = [len(elt) for elt in net_cycles]
    net_cycle_lengths_dict = quantify_cycle_lengths(net_cycle_lengths)
    
    out = dict_to_list(net_cycle_lengths_dict)
    matrix_length = len(out)

    if num_random_nets > 0:
        print("Random network generation")
    for _ in tqdm(range(num_random_nets)):
        
        new = regenerate_network(net, True, True, True)
        new_cycles = new.find_cycles()
        new_cycle_lengths = [len(elt) for elt in new_cycles]
        new_cycle_lengths_dict = quantify_cycle_lengths(new_cycle_lengths)
        new_cycle_lens = dict_to_list(new_cycle_lengths_dict)
        while len(new_cycle_lens) > matrix_length:
            if len(np.shape(out)) > 1:
                out = np.concatenate((out, np.zeros(shape=(len(out),1))), axis=1)
            else:
                out = np.append(out, 0)
            matrix_length += 1
        while len(new_cycle_lens) < matrix_length:
            new_cycle_lens = np.append(new_cycle_lens, 0)
        out = np.vstack((out, new_cycle_lens))

    out = np.vstack((np.array(range(1,matrix_length+1)), out))
    return out.T

def clustering_analysis(expressions_file, num_random_nets=100):
    
    expressions = read_expressions_from_txt(expressions_file)
    external = infer_external_from_expressions(expressions)
    net = BooleanNetwork(expressions, external)
    net_ccs = net.clustering_coefficients
    
    gene_names = []
    out = []

    for gene in sorted(net_ccs.keys()):
        cc = net_ccs[gene]
        if cc != -1:
            gene_names.append(gene)
            out.append(cc)

    out = np.array(out)

    for _ in tqdm(range(num_random_nets)):
        new_ccs_list = []
        new = regenerate_network(net, True, True, True)
        new_ccs = new.clustering_coefficients

        for gene in gene_names:
            new_ccs_list.append(new_ccs[gene])
        out = np.vstack((out, new_ccs_list))

    out = np.vstack((gene_names, out))
    return out.T