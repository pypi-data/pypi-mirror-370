import random
from . import qm as qm
from .BooleanNetwork import BooleanNetwork
from .logic_processing import get_inputs, switch_directions

def regenerate_network(bnetwork, preserve_in_degrees, preserve_out_degrees, preserve_funcs, p=1):
    
    def choose_n(inp, n_):
        """
        Given an input list, return n randomly chosen items from list. Output is a 
        list of length n.
        """
        if isinstance(inp, dict):
            inp_copy = list(inp)
        else:
            inp_copy = inp[:]
            
        out = []
        
        while len(out) < n_:
            ix = random.randint(0, len(inp_copy)-1)
            out.append(inp_copy.pop(ix))
        return out
    
    def generate_new_expressions(regulation_dictionary):
        """
        Input is a dictionary indicating the nodes that regulate each node. Keys
        are node names and corresponding values are list of node names that 
        regulate the key node.
        
        Returns dicts indicating each node's new expressions and minterms.
        """
        
        def generate_random_bool_function(var_names):
            
            def generate_minterms(n_):
                return [i for i in range(n_) if bool(random.randint(0,1))]
            
            n = len(var_names)
            num_vars = -1
            while num_vars != n:
                # regenerate the expression until num_vars = n, so no redundancies
                minterms = generate_minterms(n)
                qm_ = qm.QM(var_names)
                solution = qm_.solve(minterms, [])[1]
                optimal = qm_.get_function(solution)
                num_vars = len(set(get_inputs(optimal)))
            
            return optimal, minterms
        
        
        new_expressions = {}
        new_minterms = {}
        for node, variable_names in regulation_dictionary.items():
            
            optimal, minterms = generate_random_bool_function(variable_names)
            new_expressions[node] = optimal
            new_minterms[node] = (minterms, list(reversed(variable_names)))
        
        return new_expressions, new_minterms
    
    def rename_variables_in_formula(formula, renaming_dict):
        
        # assert get_inputs(formula) == set(renaming_dict)
        new_formula = formula
        for old_name, new_name in renaming_dict.items():
            new_formula = new_formula.replace(' ' + old_name + ' ', ' ' + new_name + ' ')
        return new_formula
    
    def choose_random_key_from_dict(inp):
        return random.choices(list(inp), inp.values())[0]

    def get_regulation_dict(in_degs_counts, out_degs_counts):
        
        in_degs_counts_copy = {k: v for k, v in in_degs_counts.items()}
        out_degs_counts_copy = {k: v for k, v in out_degs_counts.items()}
        regulation_dict = {}
        
        for i in range(sum(in_degs_counts_copy.values())):
            to_rand = choose_random_key_from_dict(in_degs_counts_copy)
            from_rand = choose_random_key_from_dict(out_degs_counts_copy)
            
            if to_rand in regulation_dict:
                # if all possible from_rand in regulation_dict[to_rand], start over
                if all([elt in regulation_dict[to_rand] for elt in out_degs_counts_copy]):
                    return get_regulation_dict(in_degs_counts, out_degs_counts)
                # if didn't start over, pick new from_rand that isn't already
                # regulating to_rand 
                while from_rand in regulation_dict[to_rand]:
                    from_rand = choose_random_key_from_dict(out_degs_counts_copy)
            
            in_degs_counts_copy[to_rand] -= 1
            out_degs_counts_copy[from_rand] -= 1
            
            if in_degs_counts_copy[to_rand] == 0:
                del in_degs_counts_copy[to_rand]
            if out_degs_counts_copy[from_rand] == 0:
                del out_degs_counts_copy[from_rand]
            
            if to_rand in regulation_dict:
                regulation_dict[to_rand].append(from_rand)
            else:
                regulation_dict[to_rand] = [from_rand]
                
        return regulation_dict
    
    expressions = bnetwork.expressions
    external = bnetwork.external
    all_nodes = list(set(expressions) | external)
    
    if preserve_in_degrees and preserve_out_degrees:
        
        if p == 1:
            in_degs = bnetwork.get_in_degs()
            out_degs = switch_directions(in_degs)
            
            in_degs_counts = {k: len(v) for k, v in in_degs.items()}
            out_degs_counts = {k: len(v) for k, v in out_degs.items()}
            regulation_dict = {}
            
            for i in range(sum(in_degs_counts.values())):
                to_rand = choose_random_key_from_dict(in_degs_counts)
                from_rand = choose_random_key_from_dict(out_degs_counts)
                
                if to_rand in regulation_dict:
                    # if all possible from_rand in regulation_dict[to_rand], start over
                    if all([elt in regulation_dict[to_rand] for elt in out_degs_counts]):
                        return regenerate_network(bnetwork, True, True, preserve_funcs)
                    # if didn't start over, pick new from_rand that isn't already
                    # regulating to_rand 
                    while from_rand in regulation_dict[to_rand]:
                        from_rand = choose_random_key_from_dict(out_degs_counts)
                
                in_degs_counts[to_rand] -= 1
                out_degs_counts[from_rand] -= 1
                
                if in_degs_counts[to_rand] == 0:
                    del in_degs_counts[to_rand]
                if out_degs_counts[from_rand] == 0:
                    del out_degs_counts[from_rand]
                
                if to_rand in regulation_dict:
                    regulation_dict[to_rand].append(from_rand)
                else:
                    regulation_dict[to_rand] = [from_rand]
            
            if not preserve_funcs: 
                new_expressions, new_minterms = generate_new_expressions(regulation_dict)
            else:
                new_expressions = {}
                new_minterms = None
                for node, variable_names in regulation_dict.items():
                    transfer_dict = {elt: variable_names[i] for i, elt in enumerate(list(in_degs[node]))}
                    new_expressions[node] = rename_variables_in_formula(expressions[node], transfer_dict)
                
            return BooleanNetwork(new_expressions, external, new_minterms)
            
        in_degs = bnetwork.get_in_degs()
        out_degs = bnetwork.get_out_degs()
        
        regulation_dict_original = bnetwork.get_in_degs()
        
        in_degs_counts = {}
        out_degs_counts = {}
        
        for node, regulators in in_degs.items():
            for regulator in regulators:
                
                rand = random.uniform(0, 1)
                if p > rand:
                    # delete node

                    if node in in_degs_counts:
                        in_degs_counts[node] += 1
                    else:
                        in_degs_counts[node] = 1
                    
                    if regulator in out_degs_counts:
                        out_degs_counts[regulator] += 1
                    else:
                        out_degs_counts[regulator] = 1
                        
                    regulation_dict_original[node] -= {regulator}
            
        assert(sum(in_degs_counts.values()) == sum(out_degs_counts.values()))
        
        in_degs_counts_copy = {k: v for k, v in in_degs_counts.items()}
        out_degs_counts_copy = {k: v for k, v in out_degs_counts.items()}
        regulation_dict_new = get_regulation_dict(in_degs_counts, out_degs_counts)
        
        regulation_dict_original = regulation_dict_original | {k: [] for k in expressions if k not in regulation_dict_original}
        regulation_dict_new = regulation_dict_new | {k: [] for k in expressions if k not in regulation_dict_new}
        regulation_dict = {k: (list(v), regulation_dict_new[k]) for k, v in regulation_dict_original.items()}
        
        new_expressions = {}
        new_minterms = None
        assert (set(regulation_dict) == set(in_degs))
        
        old = 0
        new = 0
        
        for node, (regulators_old, regulators_new) in regulation_dict.items():
            
            assert len(in_degs[node]) == len(regulators_old) + len(regulators_new), (
                    "NODE: " + str(node) + "\n" + 
                    "Old regulators: " + str(regulators_old) + 
                    " New regulators: " + str(regulators_new) + "\n" + 
                    "In degs: " + str(in_degs[node]) + "\n" + str(in_degs_counts_copy) + str(out_degs_counts_copy)
                    )
            old += len(regulators_old)
            new += len(regulators_new)
            random.shuffle(regulators_new)
            transfer_dict = {regulator: regulator for regulator in regulators_old} 
            transfer_dict = transfer_dict | {elt: regulators_new[i] for i, elt in enumerate(list(in_degs[node] - set(regulators_old)))}
            new_expressions[node] = rename_variables_in_formula(expressions[node], transfer_dict)
                
        
        return BooleanNetwork(new_expressions, external, new_minterms)
    
    if preserve_in_degrees:

        in_degs = {key: len(set(get_inputs(val))) for key, val in expressions.items()}
        regulation_dict = {key: choose_n(all_nodes, val) for key, val in in_degs.items()}
        new_expressions, new_minterms = generate_new_expressions(regulation_dict)
        
        return BooleanNetwork(new_expressions, external, new_minterms)
    
    if preserve_out_degrees:
        
        in_degs = bnetwork.get_in_degs()
        out_degs = switch_directions(in_degs)
        num_out_degs = {k: len(v) for k, v in out_degs.items()}
        out_regulation_dict = {key: choose_n(list(expressions), val) for key, val in num_out_degs.items()}
        regulation_dict = switch_directions(out_regulation_dict)
        new_expressions, new_minterms = generate_new_expressions(regulation_dict)
            
        return BooleanNetwork(new_expressions, external, new_minterms)