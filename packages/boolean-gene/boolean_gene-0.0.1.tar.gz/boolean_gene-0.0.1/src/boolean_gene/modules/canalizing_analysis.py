def canalize(minterms):
    
    minterms_lst = minterms[0]
    variables_lst = minterms[1]
    
    def find_all_possible_rows(variable_name, variable_value):
        
        out = set()
        ix = variables_lst.index(variable_name)
        end = 2**len(variables_lst)
        
        for i in range(end):
            binary_num = bin(i)[2:]
            binary_num = '0'*(len(variables_lst) - len(binary_num)) + binary_num
            if int(binary_num[ix]) == int(variable_value):
                out.update({i})
        return out
        
    
    def check_canalizability(variable_name, variable_value):
        
        possible = find_all_possible_rows(variable_name, variable_value)
        overlap = possible.intersection(set(minterms_lst))
        
        if overlap == set():
            return False
        elif overlap == possible:
            return True
        return None
    
    def extra(num):
        if num == 0:
            return "NOT "
        return ""
    
    for variable in variables_lst:
        for value in {True, False}:
            canalizable = check_canalizability(variable, value)
            if canalizable is not None:
                return extra(int(value)) + variable, canalizable