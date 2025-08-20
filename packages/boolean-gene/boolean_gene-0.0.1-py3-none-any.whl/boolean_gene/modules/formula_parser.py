from typing import List, Dict

def find_closing_parens(lst: List[str], idx: int) -> int:
    """
    Given a list representing a formula, returns the index of the closing parenthesis 
    corresponding to the open parenthesis at the given index. Returns -1 if no matching parenthesis is found.
    """
    assert lst[idx] == "("
    count = 0
    for i in range(idx, len(lst)):
        elt = lst[i]
        if elt == "(":
            count += 1
        if elt == ")":
            count -= 1
        if count == 0:
            return i
    return -1

def remove_extra_parens(lst: List[str]) -> None:
    """
    Removes unneeded parentheses around literals. Modifies input list in-place.
    >>> lst = ['(', 'NOT', 'A', ')']
    >>> remove_extra_parens(lst)
    >>> print(lst)
    ['NOT', 'A']
    """
    remove = True
    while remove:
        remove = set()
        for i, elt in enumerate(lst):
            if elt == "(":
                end_idx = find_closing_parens(lst, i)
                smaller_lst = lst[i + 1 : end_idx]
                if not ("AND" in smaller_lst or "OR" in smaller_lst):
                    remove.update({i, end_idx})
        for idx in sorted(remove, reverse=True):
            del lst[idx]

def parse(formula: List[str], parameters: Dict[str,bool]) -> bool:
    """
    Evaluates formula with variable values given by parameters dictionary.
    """
    newf = formula.replace(" AND ", " and ")
    newf = newf.replace(" OR ", " or ")
    newf = newf.replace("NOT ", "not ")
    return eval(newf, parameters | {"__builtins__": __builtins__})

def string_preprocess(inp: str) -> str:
    """
    Replaces special Python characters in gene names with non-special characters, allowing use in eval()
    """
    out = inp.replace(",", "_").replace("/", "_").replace("+", "__").replace("-", "").replace(";", "_").replace(" or ", " OR ").replace(" and ", " AND ").replace("not ", "NOT ").replace('.', 'point')
    non_variables = {"(", "", ")", "AND", "NOT", "OR"}
    inp_as_list = out.split(' ')
    rm_idx = []

    # remove parentheses and leading digits from variable names
    if inp_as_list[0] not in non_variables: 
        inp_as_list[0] = inp_as_list[0].replace("(", "").replace(")", "")
        if inp_as_list[0][0] in '0123456789':
            inp_as_list[0] = 'num_' + inp_as_list[0]
    for i in range(len(inp_as_list)-1, 0, -1):
        # start at ix=-1, end at ix=1

        cur = inp_as_list[i]
        nxt = inp_as_list[i-1]
        
        if cur not in non_variables:
            inp_as_list[i] = cur.replace('(', '').replace(')', '')
            if inp_as_list[i][0] in '0123456789':
                inp_as_list[i] = 'num_' + inp_as_list[i]
            if nxt not in non_variables:
                inp_as_list[i-1] += '_' + inp_as_list[i]
                rm_idx.append(i)
            
    for idx in rm_idx:
        del inp_as_list[idx]
        
    return ' '.join(inp_as_list)

def split_formula(formula: str):
    """
    Converts formula from string to 2-element tuple, unless formula is a literal.

    >>> split_formula("( A OR B ) AND NOT C")
    (((('A', 'B'), 'OR'), 'NOT C'), 'AND')

    >>> split_formula("A")
    'A'
    """
    def remove_enclosing_parens(lst_: List[str]):
        if lst_[0] == '(' and lst_[-1] == ')':
            return remove_enclosing_parens(lst_[1:-1])
        return lst_
    
    def remove_double_nots(lst: List[str]) -> None:
        """
        Removes pairs of consecutive 'NOT's from input, modifying input in-place.
        """

        for i in range(len(lst) - 2, -1, -1):
            elt = lst[i]
            if elt == "NOT" and lst[i + 1] == "NOT":
                del lst[i + 1]
                del lst[i]

    formula_lst = [elt for elt in formula.split(" ") if elt != ""]
    remove_extra_parens(formula_lst)
    remove_double_nots(formula_lst)

    if (
        formula_lst[0] == "("
        and find_closing_parens(formula_lst, 0) == len(formula_lst) - 1
    ):
        return split_formula(" ".join(formula_lst[1:-1]))

    if len(formula_lst) < 3:
        return " ".join(formula_lst)

    if (
        formula_lst[0] == "NOT"
        and formula_lst[1] == "("
        and find_closing_parens(formula_lst, 1) == len(formula_lst) - 1
    ):
        count = 0
        modified_lst = formula_lst[2:-1]
        modified_lst = remove_enclosing_parens(modified_lst)

        for i, elt in enumerate(modified_lst):
            if elt == "(":
                count += 1
            if elt == ")":
                count -= 1
            if count == 0 and (elt == "AND" or elt == "OR"):
                subformula_1 = "NOT ( " + " ".join(modified_lst[:i]) + " )"
                not_operator = elt
                subformula_2 = "NOT ( " + " ".join(modified_lst[i + 1 :]) + " )"

                if not_operator == "AND":
                    operator = "OR"
                else:
                    operator = "AND"

                return (
                    (split_formula(subformula_1), split_formula(subformula_2)),
                    operator,
                )

    count = 0

    for i, elt in enumerate(formula_lst):
        if elt == "(":
            count += 1
            continue
        if elt == ")":
            count -= 1
            continue
        if count == 0 and (elt == "AND" or elt == "OR"):
            subformula_1 = formula_lst[:i]
            operator = elt
            subformula_2 = formula_lst[i + 1 :]

            return (
                (
                    split_formula(" ".join(subformula_1)),
                    split_formula(" ".join(subformula_2)),
                ),
                operator,
            )
        
def reduce(formula: str, variable: str, falsify: bool = False):
    """
    Returns modified formula assuming specified variable is True (or assuming False if falsify is True).
    
    >>> reduce("A OR B", "A")
    'True'

    >>> reduce("A AND B", 'A')
    'B'

    >>> reduce("( A OR B OR C )", 'D')
    'A OR ( B OR C )'
    """

    def link(branched_formula, outermost: bool = True) -> str:
        """
        Converts formula from 2-element tuple to string, unless formula is a literal. Inverse of split_formula().

        >>> link("A")
        'A'

        >>> link((('A', 'B'), 'OR'))
        '( A OR B )'
        """

        if isinstance(branched_formula, str):
            return branched_formula

        operator = branched_formula[1]
        subformula_1 = branched_formula[0][0]
        subformula_2 = branched_formula[0][1]

        if isinstance(subformula_1, str) and isinstance(subformula_2, str):
            return "( " + subformula_1 + " " + operator + " " + subformula_2 + " )"
        if not outermost:
            return (
                "( "
                + link(subformula_1, outermost=False)
                + " "
                + operator
                + " "
                + link(subformula_2, outermost=False)
                + " )"
            )
        else:
            return (
                link(subformula_1, outermost=False)
                + " "
                + operator
                + " "
                + link(subformula_2, outermost=False)
            )
        
    def reduce_formula(branched_formula, variable: str):
        """
        Returns new formula (in 2-tuple structure) assuming variable is True. 

        >>> reduce_formula((("NOT A", "B"), "AND"), "A")
        'False'

        >>> reduce_formula((((('A', 'B'), 'OR'), 'NOT C'), 'AND'), "A")
        'NOT C'
        """

        if isinstance(branched_formula, str):
            if branched_formula == variable:
                return "True"
            if branched_formula == "NOT " + variable:
                return "False"
            return branched_formula

        operator = branched_formula[1]
        subformula_1 = branched_formula[0][0]
        subformula_2 = branched_formula[0][1]

        if "True" in branched_formula[0] or variable in branched_formula[0]:
            if operator == "OR":
                return "True"
            if operator == "AND":
                if subformula_1 in {"True", variable}:
                    return reduce_formula(subformula_2, variable)
                if subformula_2 in {"True", variable}:
                    return reduce_formula(subformula_1, variable)

        if "False" in branched_formula[0] or "NOT " + variable in branched_formula[0]:
            if operator == "AND":
                return "False"
            if operator == "OR":
                if subformula_1 in {"False", "NOT " + variable}:
                    return reduce_formula(subformula_2, variable)
                if subformula_2 in {"False", "NOT " + variable}:
                    return reduce_formula(subformula_1, variable)

        if isinstance(subformula_1, str) and isinstance(subformula_2, str):
            return branched_formula
        
        out = (
            (
                reduce_formula(subformula_1, variable),
                reduce_formula(subformula_2, variable),
            ),
            operator,
        )
        if out == branched_formula:
            return out
        return reduce_formula(out, variable)
    
    def falsify_variable(formula: str, variable: str) -> str:
        """
        Returns modified formula such that 'variable' in formula is made False at
        every instance.

        >>> falsify_variable("A AND ( B OR C OR NOT A )", "A")
        'NOT A AND ( B OR C OR A )'
        """

        formula_lst = [elt for elt in formula.split(" ") if elt != ""]
        remove_extra_parens(formula_lst)

        out = [elt if elt != variable else "NOT " + elt for elt in formula_lst]
        out = " ".join(out)
        out = [elt for elt in out.split(" ") if elt != ""]
        for i in range(len(out) - 2, -1, -1):
            elt = out[i]
            if elt == "NOT" and out[i + 1] == "NOT":
                del out[i + 1]
                del out[i]

        return " ".join(out)

    if falsify:
        return reduce(falsify_variable(formula, variable), variable, False)

    branched = split_formula(formula)
    out = reduce_formula(branched, variable)

    if isinstance(out, str):
        return out

    out = link(out)
    formula_lst = [elt for elt in out.split(" ") if elt != ""]
    remove_extra_parens(formula_lst)
    if (
        formula_lst[0] == "("
        and find_closing_parens(formula_lst, 0) == len(formula_lst) - 1
    ):
        formula_lst = formula_lst[1:-1]
    return " ".join(formula_lst)

def get_inputs(formula):
    """
    Returns genes used in input formula
    """
    if formula == '0' or formula == '1':
        return set()
    
    return tuple(
        set(elt
        for elt in formula.split(" ")
        if elt not in {"", "NOT", "OR", "AND", "(", ")"})
    )