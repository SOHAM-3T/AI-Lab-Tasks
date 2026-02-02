import random

bn = {
    'Burglary': {'parents': [], 'cpt': {(): 0.001}},
    'Earthquake': {'parents': [], 'cpt': {(): 0.002}},
    'Alarm': {
        'parents': ['Burglary', 'Earthquake'],
        'cpt': {
            (True, True): 0.95,
            (True, False): 0.94,
            (False, True): 0.29,
            (False, False): 0.001
        }
    },
    'JohnCalls': {'parents': ['Alarm'], 'cpt': {(True,): 0.90, (False,): 0.05}},
    'MaryCalls': {'parents': ['Alarm'], 'cpt': {(True,): 0.70, (False,): 0.01}}
}

VARS = ['Burglary', 'Earthquake', 'Alarm', 'JohnCalls', 'MaryCalls']


def p_true(var, state):
    parents = tuple(state[p] for p in bn[var]['parents'])
    return bn[var]['cpt'][parents]

def sample_var(var, state):
    return random.random() < p_true(var, state)


# Prior sampling
def prior_sample():
    s = {}
    for v in VARS:
        s[v] = sample_var(v, s)
    return s

# Rejection sampling
def rejection_sampling(query, evidence, N=10000):
    accept = 0
    accept_query_true = 0
    for _ in range(N):
        s = prior_sample()
        ok = True
        for e, val in evidence.items():
            if s.get(e) != val:
                ok = False
                break
        if not ok:
            continue
        accept += 1
        if s[query]:
            accept_query_true += 1
    if accept == 0:
        return None  # no accepted samples (increase N)
    return accept_query_true / accept

# Likelihood weighting
def likelihood_weighting(query, evidence, N=10000):
    """Estimate P(query=True | evidence) by likelihood weighting."""
    w_true = 0.0
    w_total = 0.0
    for _ in range(N):
        w = 1.0
        s = {}
        for v in VARS:
            if v in evidence:
                # weight by P(evidence_value | parents)
                p = p_true(v, s)
                ev = evidence[v]
                w *= p if ev else (1 - p)
                s[v] = ev
            else:
                s[v] = sample_var(v, s)
        w_total += w
        if s[query]:
            w_true += w
    if w_total == 0:
        return None
    return w_true / w_total

# Gibbs sampling
def gibbs_sampling(query, evidence, N=5000, burn_in=1000, thin=1):
    # list of non-evidence variables to sample
    non_evidence = [v for v in VARS if v not in evidence]
    # if query is evidence, return its fixed truth directly
    if query in evidence:
        return 1.0 if evidence[query] else 0.0

    # initial state: set evidence, randomize others
    state = dict(evidence)
    for v in non_evidence:
        state[v] = random.choice([False, True])

    # precompute children for each var (simple adjacency)
    children = {v: [] for v in VARS}
    for v in VARS:
        for p in bn[v]['parents']:
            children[p].append(v)

    def prob_var_given_markov_blanket(var, value, st):
        # P(var = value | parents)
        parents_tuple = tuple(st[p] if p != var else value for p in bn[var]['parents'])
        p_var = bn[var]['cpt'][parents_tuple]

        prob = p_var if value else (1 - p_var)

        # multiply by P(child | its parents) for each child (using st with var=value)
        for ch in children[var]:
            # build parent tuple for child, replacing var's value by `value` if needed
            parent_vals = []
            for p in bn[ch]['parents']:
                if p == var:
                    parent_vals.append(value)
                else:
                    parent_vals.append(st[p])
            parent_t = tuple(parent_vals)
            p_ch = bn[ch]['cpt'][parent_t]
            ch_val = st[ch]
            prob *= p_ch if ch_val else (1 - p_ch)
        return prob

    collected = 0
    count_true = 0
    steps = 0
    total_iterations = burn_in + N * thin
    while steps < total_iterations:
        # sweep through non-evidence vars
        for var in non_evidence:
            # compute unnormalized prob for var=True and var=False
            prob_true = prob_var_given_markov_blanket(var, True, state)
            prob_false = prob_var_given_markov_blanket(var, False, state)
            denom = prob_true + prob_false
            if denom == 0:
                p_true_given_mb = 0.5
            else:
                p_true_given_mb = prob_true / denom
            state[var] = (random.random() < p_true_given_mb)
        steps += 1
        if steps > burn_in and ((steps - burn_in) % thin == 0):
            collected += 1
            if state[query]:
                count_true += 1
            if collected >= N:
                break

    if collected == 0:
        return None
    return count_true / collected

if __name__ == "__main__":
    random.seed(42)

    print("Estimate P(Burglary | JohnCalls=True)")
    evidence = {'JohnCalls': True}
    print("Rejection (N=20000):", rejection_sampling('Burglary', evidence, N=20000))
    print("Likelihood (N=20000):", likelihood_weighting('Burglary', evidence, N=20000))
    print("Gibbs (N=5000):", gibbs_sampling('Burglary', evidence, N=5000, burn_in=1000))
    print("Prior (via rejection):", rejection_sampling('Burglary', evidence, N=20000))

    print("\nEstimate P(Alarm | Burglary=True)")
    evidence2 = {'Burglary': True}
    print("Rejection (N=20000):", rejection_sampling('Alarm', evidence2, N=20000))
    print("Likelihood (N=20000):", likelihood_weighting('Alarm', evidence2, N=20000))
    print("Gibbs (N=5000):", gibbs_sampling('Alarm', evidence2, N=5000, burn_in=1000))
