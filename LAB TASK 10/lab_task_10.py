from itertools import product

bn = {
    'Burglary': { 'parents': [], 'p_true': 0.001 },
    'Earthquake': { 'parents': [], 'p_true': 0.002 },
    'Alarm': {
        'parents': ['Burglary', 'Earthquake'],
        'p_true': {
            (True, True): 0.95,
            (True, False): 0.94,
            (False, True): 0.29,
            (False, False): 0.001
        }
    },
    'JohnCalls': { 'parents': ['Alarm'], 'p_true': { (True,): 0.90, (False,): 0.05 } },
    'MaryCalls': { 'parents': ['Alarm'], 'p_true': { (True,): 0.70, (False,): 0.01 } }
}

vars_order = list(bn.keys())

def prob_var(v, val, assign):
    node = bn[v]
    parents = node['parents']
    if not parents:
        p = node['p_true']
    else:
        parent_vals = tuple(assign[p] for p in parents)
        p = node['p_true'][parent_vals]
    return p if val else 1 - p

def joint(assign):
    p = 1.0
    for v in vars_order:
        p *= prob_var(v, assign[v], assign)
    return p

def enumeration_ask(query_var, evidence):
    hidden = [v for v in vars_order if v not in evidence and v != query_var]

    def sum_for(query_val):
        total = 0.0
        for vals in product([False, True], repeat=len(hidden)):
            a = dict(evidence)
            a[query_var] = query_val
            for v, val in zip(hidden, vals):
                a[v] = val
            total += joint(a)
        return total

    num = sum_for(True)
    denom = sum_for(True) + sum_for(False)
    return num / denom if denom > 0 else None


def dist(var, evidence):
    p_true = enumeration_ask(var, evidence)
    return {'True': p_true, 'False': None if p_true is None else 1 - p_true}

if __name__ == '__main__':
    print("a) P(JohnCalls | Burglary=True, Earthquake=True):", dist('JohnCalls', {'Burglary': True, 'Earthquake': True}))

    print("b) P(Alarm | Burglary=True):", dist('Alarm', {'Burglary': True}))

    print("c) P(Earthquake | MaryCalls=True):", dist('Earthquake', {'MaryCalls': True}))

    print("d) P(Burglary | Alarm=True):", dist('Burglary', {'Alarm': True}))

    # check independence: JohnCalls ⟂ MaryCalls | Alarm
    for a_state in [True, False]:
        p_j_given_a = enumeration_ask('JohnCalls', {'Alarm': a_state})
        p_j_given_a_m = enumeration_ask('JohnCalls', {'Alarm': a_state, 'MaryCalls': True})
        print(f"\nAlarm={a_state}: P(John=True | Alarm) = {p_j_given_a:.6f}, "
              f"P(John=True | Alarm, Mary=True) = {p_j_given_a_m:.6f}, "
              f"diff = {abs(p_j_given_a - p_j_given_a_m):.6g}")
