import numpy as np
from .formula_parser import parse, get_inputs

def find_minterms(formula):

    def translate_state_to_int(state):
        out = ""
        for elt in state.values():
            out = out + str(int(elt))
        return int(out, 2)

    def get_input_assignments(literals):
        input_as_string = "0b" + "0" * len(literals)
        while input_as_string != "0b1" + "0" * len(literals):
            yield {
                literals[i]: bool(int(char))
                for i, char in enumerate(input_as_string[2:])
                if literals[i] != "__builtins__"
            }
            input_as_string = bin(int(input_as_string, 2) + 1)
            while len(input_as_string) < len(literals) + 2:
                input_as_string = "0b0" + input_as_string[2:]

    out = []
    literals = get_inputs(formula)
    for tva in get_input_assignments(literals):
        formula_value = parse(formula, tva)
        if formula_value:
            out.append(translate_state_to_int(tva))
    return (out, list(literals))

def switch_directions(reg_dict):
    
    out = {}
    for node, regulators in reg_dict.items():
        for regulator in regulators:
            if regulator in out:
                out[regulator].add(node)
            else:
                out[regulator] = {node}
    return out

def dict_to_list(inp_dict):
    if len(inp_dict) == 0:
        return np.array([0])
    max_elt = max(inp_dict)
    out = np.zeros(max_elt)
    for key, val in inp_dict.items():
        out[key-1] += val
    return out