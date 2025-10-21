from typing import Any, Dict, List, Optional, Set, Tuple

Term = Any

def substitute(t: Term, theta: Dict[str, Term]) -> Term:
    if isinstance(t, str):
        if t.startswith('?'):
            return substitute(theta[t], theta) if t in theta else t
        else:
            return t
    return tuple([t[0]] + [substitute(a, theta) for a in t[1:]])

def occurs_check(var: str, term: Term, theta: Dict[str, Term]) -> bool:
    term = substitute(term, theta)
    if isinstance(term, str):
        return term == var
    for a in term[1:]:
        if occurs_check(var, a, theta):
            return True
    return False

def unify(x: Term, y: Term, theta: Dict[str, Term]) -> Optional[Dict[str, Term]]:

    x = substitute(x, theta)
    y = substitute(y, theta)
    if x == y:
        return dict(theta)

    # variable cases
    if isinstance(x, str) and x.startswith('?'):
        return unify_var(x, y, theta)
    if isinstance(y, str) and y.startswith('?'):
        return unify_var(y, x, theta)

    if isinstance(x, tuple) and isinstance(y, tuple):
        if x[0] != y[0] or len(x) != len(y):
            return None
        new_theta = dict(theta)
        for a, b in zip(x[1:], y[1:]):
            new_theta = unify(a, b, new_theta)
            if new_theta is None:
                return None
        return new_theta

    return None

def unify_var(var: str, x: Term, theta: Dict[str, Term]) -> Optional[Dict[str, Term]]:
    if var in theta:
        return unify(theta[var], x, theta)
    if isinstance(x, str) and x.startswith('?') and x in theta:
        return unify(var, theta[x], theta)
    if occurs_check(var, x, theta):
        return None
    new_theta = dict(theta)
    new_theta[var] = x
    return new_theta

def is_var(x: Term) -> bool:
    return isinstance(x, str) and x.startswith('?')

def contains_var(t: Term) -> bool:
    if isinstance(t, str):
        return is_var(t)
    return any(contains_var(a) for a in t[1:])

def forward_chain(rules: List[Tuple[List[Term], Term]], facts: Set[Term], query: Term) -> Tuple[bool, Set[Term]]:
    inferred = set(facts)  # derived facts
    added = True
    while added:
        added = False
        for premises, conclusion in rules:
            theta_list = [dict()]
            for prem in premises:
                new_theta_list = []
                for theta in theta_list:
                    prem_inst = substitute(prem, theta)
                    for fact in list(inferred):
                        theta2 = unify(prem_inst, fact, dict(theta))
                        if theta2 is not None:
                            new_theta_list.append(theta2)
                theta_list = new_theta_list
                if not theta_list:
                    break
            for theta in theta_list:
                conc_inst = substitute(conclusion, theta)
                if contains_var(conc_inst):
                    continue
                if conc_inst not in inferred:
                    inferred.add(conc_inst)
                    added = True
                    if unify(query, conc_inst, {}) is not None:
                        return True, inferred
    for f in inferred:
        if unify(query, f, {}) is not None:
            return True, inferred
    return False, inferred

if __name__ == "__main__":
    #   Parent(John, Mary)
    #   Parent(Mary, Ann)
    facts = {('Parent', 'John', 'Mary'), ('Parent', 'Mary', 'Ann')}

    # Rules:
    # 1) Parent(x,y) -> Ancestor(x,y)
    # 2) Parent(x,z) & Ancestor(z,y) -> Ancestor(x,y)
    x, y, z = '?x', '?y', '?z'
    rule1 = ([('Parent', x, y)], ('Ancestor', x, y))
    rule2 = ([('Parent', x, z), ('Ancestor', z, y)], ('Ancestor', x, y))
    rules = [rule1, rule2]

    # Query: Ancestor(John, Ann)?
    query = ('Ancestor', 'John', 'Ann')

    entailed, derived = forward_chain(rules, facts, query)

    print("Query:", query)
    print("Entailed?", entailed)
    print("Derived facts:")
    for d in sorted(derived):
        print(" ", d)
