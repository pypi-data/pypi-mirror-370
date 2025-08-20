import os
import csv
from .formula_parser import string_preprocess, get_inputs

def get_txt_from_dir(directory: str):
    """
    From input directory, return list of expressions .txt files and external
    components .txt files
    """
    expressions = []
    external_components = []
    for elt in os.listdir(directory):
        if 'expressions' in elt:
            expressions.append(elt)
        elif 'external_components' in elt:
            external_components.append(elt)
    expressions.sort()
    external_components.sort()
    
    assert len(expressions) == len(external_components)
    
    return expressions, external_components

def read_expressions_from_txt(path_to_txt_file):
    """
    Returns dictionary that maps genes to their corresponding expressions in input
    text file.
    Makes the following replacements: {',': '_', '/': '_', '+', '__', '-': ''}

    Input: string (path to txt file)
    Output: dict (keys = gene names, values = string expressions)

    """
    out = {}
    reader = open(os.path.expanduser(path_to_txt_file), "r")
    for line in reader:
        if line[-1] == "\n":
            line = line[:-1]
        line = line.replace("=  ", "= ")
        line = line.replace("  =", " =")
        var, formula = line.split(" = ")
        out[string_preprocess(var)] = string_preprocess(formula)
    return out

def read_external_from_txt(path_to_txt_file):
    """
    Returns set containing external signals given text file.
    Makes the following replacements: {',': '_', '/': '_', '+', '__', '-': ''}

    Input: string (path to file)
    Output: set
    """
    out = set()
    reader = open(path_to_txt_file, "r")
    for line in reader:
        if line[-1] == "\n":
            line = line[:-1]
        out.add(string_preprocess(line))
    return out

def infer_external_from_expressions(expressions):
    out = set()
    for formula in expressions.values():
        inputs = set(get_inputs(formula))
        ext_inputs = set([elt for elt in inputs if elt not in expressions.keys()])
        out = out | ext_inputs
    return out

def save_data(data, header, path_to_file):
    with open(os.path.expanduser(path_to_file), mode='w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in data:
            writer.writerow(list(row))