import sympy as sp
import random
from .logic_processing import switch_directions, find_minterms, get_inputs
from .formula_parser import reduce
from .canalizing_analysis import canalize

class BooleanNetwork:
    def __init__(self, expressions, external, minterms=None):
        # self.state and self.expressions are dicts
        # (map var to truth value or var to formula)

        self.state = {gene: None for gene in expressions}
        self.bitstate = '_'*len(expressions)
        self.expressions = expressions
        self.external = external
        if minterms is None:
            self.minterms = {gene: None for gene in expressions}
        else:
            self.minterms = minterms
        self.order = tuple(expressions)
        self.compiled_expressions = {k: compile(formula.replace(" AND ", " and ").replace(" OR ", " or ").replace("NOT ", "not "), '<string>', 'eval') for k, formula in expressions.items()}
        self.external_values = {elt: None for elt in external}
        
    def initialize_external(self, ext_dict=None):
        if ext_dict is not None:
            self.external_values = ext_dict
        else:
            self.external_values = {elt: bool(random.randint(0, 1)) for elt in self.external}

    def step(self):
        new_state = {}
        new_bitstate = ''
        for node in self.expressions:
            new_val = self.step_variable(node)
            new_state[node] = new_val
            new_bitstate += str(int(new_val))
        self.state = new_state
        self.bitstate = new_bitstate
        
    def step_variable(self, node):
        out = eval(self.compiled_expressions[node], self.state | self.external_values)
        assert isinstance(out, bool), (self.external, self.external_values)
        return eval(self.compiled_expressions[node], self.state | self.external_values)
        
    def set_state(self, state):
        if isinstance(state, str):
            self.bitstate = state
            for i, elt in enumerate(state):
                self.state[self.order[i]] = bool(elt)
        elif isinstance(state, dict):
            self.state = state
            new_bitstate = ''
            for node, value in state.items():
                new_bitstate += str(int(value))
            self.bitstate = new_bitstate
        
    
    def randomize_state(self):
        self.bitstate = ''
        for gene in self.expressions:
            val = random.randint(0, 1)
            self.state[gene] = bool(val)
            self.bitstate += str(val)
    
    def find_attractors(self, stable_only=False, n=1000, t=100):
        """
        Returns network's attractors (including stable fixed points and oscillatory
        cycles). Excludes oscillatory cycles if stable_only is True. Finds attractors
        by running n simulations that each runs for t time steps.
        
        Input (all optional): stable_only (bool), n (int), t (int)
        Output: dict where keys are tuples corresponding to attractors and values
        are ints showing how many times in the n simulations that attractor was
        reached.

        """

        out = {}
        for __ in range(n):
            self.randomize_state()
            self.initialize_external()
            history = [self.bitstate]

            for _ in range(t):
                self.step()
                
                translated_state = self.bitstate
                
                if translated_state in history:
                    idx = history.index(translated_state)
                    cycle = tuple(history[idx:])

                    if len(cycle) > 1 and stable_only:
                        break

                    found = False
                    for elt in out:
                        if set(elt) == set(cycle):
                            out[elt] += 1
                            found = True
                            break
                    if found:
                        break
                    out[cycle] = 1
                    break
                
                history.append(translated_state)
        return out
    
    def lyapunov_stable(self, bitstate_fp, sq_dist, step_limit=1000):
        """
        A fixed point is said to be Lyapunov stable if all initial conditions 
        that differ from the fixed point by 1 bit go to the fixed point.
        
        bitstate_fp: bitstring, representing a fixed point
        sq_dist: int, look at all initial conditions that start a distance 
        sqrt(sq_dist) away from the fixed point
        step_limit: Max number of steps taken to attempt to reach an attractor
        before giving up
        
        Return: True if f.p. is Lyapunov stable. (False, initial_condition) otherwise,
        where initial_condition is an initial condition that causes Lyapunov stability
        to fail.
        """
        
        def switch_n_bits(bitstr, n): 
            
            def n_tuplet_gen(n_, min_val, max_val):
                if n_ == 1:
                    out = min_val
                    while out < max_val:
                        yield [out]
                        out += 1
                else:        
                    first = min_val
                    while first <= max_val - n:
                        for rest in n_tuplet_gen(n_-1, first+1, max_val):
                            yield [first] + rest
                        first += 1
            
            for idx_list in n_tuplet_gen(n, 0, len(bitstr)):
                bitstr_lst = list(bitstr)
                for idx in idx_list:
                    bitstr_lst[idx] = str(1-int(bitstr_lst[idx]))
                yield ''.join(bitstr_lst)
                
        all_visited = set()
        for initial_condition in switch_n_bits(bitstate_fp, sq_dist):
            self.set_state(initial_condition)
            step_counter = 0
            history = {self.bitstate}
            all_visited.add(self.bitstate)
            while self.bitstate != bitstate_fp:
                
                self.step()
                if self.bitstate in history:
                    return (False, initial_condition)
                
                history.add(self.bitstate)
                if self.bitstate in all_visited:
                    
                    break
                
                all_visited.add(self.bitstate)
                if step_counter == step_limit:
                    print('Step limit reached with no attractor found!')
                    return (False, initial_condition)
        return True
    
    def canalize_variable(self, variable):
        
        expression = self.expressions[variable]
        minterms = self.minterms[variable]
        
        if minterms is None:
            minterms = find_minterms(expression)
        
        return canalize(minterms)
    
    def nested_canalize_variable(self, variable):
        new_formula = self.expressions[variable]
        out = tuple()
        canal = self.canalize_variable(variable)

        while canal is not None and new_formula not in {"True", "False"}:
            
            out += (canal,)
            if canal[0][:4] == "NOT ":
                new_formula = reduce(new_formula, canal[0][4:])
                
            else:
                new_formula = reduce(new_formula, canal[0], falsify=True)
            canal = canalize(find_minterms(new_formula))
            
        return out, new_formula
    
    @property
    def nested_canalize(self):
        
        return {variable: self.nested_canalize_variable(variable) 
                for variable in self.expressions}
    
    @property
    def external_bitstate(self):
        external_bitstate = ''
        for value in self.external_values.values():
            if value:
                external_bitstate += '1'
            else:
                external_bitstate += '0'
        return external_bitstate
    
        
    def number_of_inputs(self):
        
        return {k: len(get_inputs(v)) for k, v in self.expressions.items()}
    
    def get_in_degs(self):
        
        return {k: set(get_inputs(v)) for k, v in self.expressions.items()}
    
    def get_out_degs(self):
        return switch_directions(self.get_in_degs())
    
    def is_bipartite(self):
        
        red = set()
        blue = set()
        connections = self.get_out_degs()
        i = 0
        for node, children in connections.items():
            if i % 2 == 0:
                red.add(node)
                for child in children:
                    blue.add(child)
            else:
                blue.add(node)
                for child in children:
                    red.add(child)
                    
            if red.intersection(blue) != set():
                return False
            i += 1
        return True, (red, blue)
    
    @property
    def clustering_coefficients(self):
        
        def get_neighbors(node):
            return out_degs[node] | in_degs[node]
        
        all_nodes = self.external | set(self.expressions)
        in_degs = self.get_in_degs()
        out_degs = self.get_out_degs()
        
        in_degs = in_degs | {node: set() for node in all_nodes - set(in_degs)}
        out_degs = out_degs | {node: set() for node in all_nodes - set(out_degs)}
        
        out = {}
        
        for node in all_nodes:
            count = 0
            neighbors = get_neighbors(node) - {node}
            if len(neighbors) == 0 or len(neighbors) == 1:
                out[node] = -1
            else:
                for neighbor in neighbors:
                    neighbors_2 = in_degs[neighbor] - {neighbor}
                    shared = neighbors_2.intersection(neighbors)
                    count += len(shared)
                cc = count/(len(neighbors)*(len(neighbors)-1))
                out[node] = cc
                assert cc <= 1, (node, neighbors)
        return out
                
    def find_cycles(self):
        
        expressions = self.expressions
        external = self.external
        
        cycles = []
        cycles_edges = []
        
        all_nodes = tuple(set(expressions) | external)
        numbering_scheme = {all_nodes[i]: i for i in range(len(all_nodes))}
        connecting_dict = {numbering_scheme[key]: set(numbering_scheme[elt] 
                                                      for elt in set(get_inputs(val))) 
                            for key, val in expressions.items()}
        # in connecting dict, node i is regulated by connecting_dict[i]
        
        colnum = 0
        matrix_values = {}
        num_edges = 0
        for node, regulators in connecting_dict.items():
            num_edges += len(regulators)
            for elt in regulators:
                matrix_values[(elt, colnum)] = -1
                matrix_values[(node, colnum)] = 1
                colnum += 1
                
        A = sp.ImmutableSparseMatrix(len(all_nodes), num_edges, matrix_values)
        for null_vec in A.nullspace():
            vals = set(null_vec)
            if 1 in vals and -1 in vals:
                continue
            cycles_edges.append([i for i in range(len(null_vec)) if null_vec[i] != 0])
            
        for cycle in cycles_edges:
            node_cycle = []
            for cur_edge in cycle:
                cur_col = A.col(cur_edge)
                start = -1
                end = -1
                cur_ix = 0
                while start == -1 or end == -1:
                    if cur_col[cur_ix] == -1:
                        start = cur_ix
                    elif cur_col[cur_ix] == 1:
                        end = cur_ix
                    cur_ix += 1
                node_cycle.append((start, end))
            start = node_cycle.pop(0)
            out_cycle = [start[0]]
            
            while node_cycle:
                cur = node_cycle.pop(0)
                if cur[0] != start[1]:
                    node_cycle.append(cur)
                else:
                    out_cycle.append(cur[0])
                    start = cur
            cycles.append(tuple(all_nodes[i] for i in out_cycle))
            
        return cycles