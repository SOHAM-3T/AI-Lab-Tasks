import random

class BayesNetSampler:
    def __init__(self, bn, vars_order=None):
        self.bn = bn
        if vars_order is None:
            self.vars = list(bn.keys())
        else:
            self.vars = list(vars_order)
        self.children = {v: [] for v in self.vars}
        for v in self.vars:
            for p in bn[v]['parents']:
                self.children[p].append(v)

    def p_true(self, var, assignment):
        parents = tuple(assignment[p] for p in self.bn[var]['parents'])
        return self.bn[var]['cpt'][parents]

    def sample_var(self, var, assignment):
        p = self.p_true(var, assignment)
        return random.random() < p

    # Prior sampling
    def prior_sample(self):
        sample = {}
        for v in self.vars:
            sample[v] = self.sample_var(v, sample)
        return sample

    # Rejection sampling
    def rejection_sampling(self, query_var, evidence, N=10000):
        count_query_true = 0
        count_accept = 0
        for _ in range(N):
            s = self.prior_sample()
            match = True
            for ev, val in evidence.items():
                if s.get(ev) != val:
                    match = False
                    break
            if not match:
                continue
            count_accept += 1
            if s[query_var]:
                count_query_true += 1
        if count_accept == 0:
            return None
        return count_query_true / count_accept

    # Likelihood Weighting
    def likelihood_weighting(self, query_var, evidence, N=10000):
        weight_true = 0.0
        weight_total = 0.0
        for _ in range(N):
            w = 1.0
            sample = {}
            for v in self.vars:
                if v in evidence:
                    p = self.p_true(v, sample)
                    ev_val = evidence[v]
                    w *= p if ev_val else (1 - p)
                    sample[v] = ev_val
                else:
                    sample[v] = self.sample_var(v, sample)
            if sample[query_var]:
                weight_true += w
            weight_total += w
        if weight_total == 0:
            return None
        return weight_true / weight_total

    def gibbs_sampling(self, query_var, evidence, N=5000, burn_in=1000, thin=1):

        non_evidence = [v for v in self.vars if v not in evidence]
        if not non_evidence:
            return 1.0 if evidence.get(query_var, False) else 0.0

        state = dict(evidence)
        for v in non_evidence:
            state[v] = random.choice([False, True])

        def markov_blanket_prob_true(var):
            prob_var_true = self.p_true(var, state)
            prod_true = prob_var_true
            for child in self.children[var]:
                parent_vals = []
                for p in self.bn[child]['parents']:
                    if p == var:
                        parent_vals.append(True)
                    else:
                        parent_vals.append(state[p])
                parent_tuple = tuple(parent_vals)
                p_child_given_parents = self.bn[child]['cpt'][parent_tuple]
                child_val = state[child]
                prod_true *= p_child_given_parents if child_val else (1 - p_child_given_parents)
            return prod_true

        count_true = 0
        samples_collected = 0
        steps = 0
        total_steps = burn_in + N * thin
        while steps < total_steps:
            for var in non_evidence:
                p_t = markov_blanket_prob_true(var)
                prob_var_false = 1.0 - self.p_true(var, state)
                prod_false = prob_var_false
                for child in self.children[var]:
                    parent_vals = []
                    for p in self.bn[child]['parents']:
                        if p == var:
                            parent_vals.append(False)
                        else:
                            parent_vals.append(state[p])
                    parent_tuple = tuple(parent_vals)
                    p_child_given_parents = self.bn[child]['cpt'][parent_tuple]
                    child_val = state[child]
                    prod_false *= p_child_given_parents if child_val else (1 - p_child_given_parents)

                denom = p_t + prod_false
                if denom == 0:
                    prob_true_given_mb = 0.5
                else:
                    prob_true_given_mb = p_t / denom

                state[var] = random.random() < prob_true_given_mb

            steps += 1
            if steps > burn_in and ((steps - burn_in) % thin == 0):
                samples_collected += 1
                if state[query_var]:
                    count_true += 1
                if samples_collected >= N:
                    break

        if samples_collected == 0:
            return None
        return count_true / samples_collected


if __name__ == "__main__":
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
    vars_order = ['Burglary', 'Earthquake', 'Alarm', 'JohnCalls', 'MaryCalls']
    sampler = BayesNetSampler(bn, vars_order)

    print("Demo: estimating P(Burglary | JohnCalls=True)")
    evidence = {'JohnCalls': True}
    print("Rejection (N=20000):", sampler.rejection_sampling('Burglary', evidence, N=20000))
    print("Likelihood (N=20000):", sampler.likelihood_weighting('Burglary', evidence, N=20000))
    print("Gibbs (N=5000):", sampler.gibbs_sampling('Burglary', evidence, N=5000, burn_in=1000))
    print("Prior (N=20000, via rejection):", sampler.rejection_sampling('Burglary', evidence, N=20000))

    print("\nDemo: estimating P(Alarm | Burglary=True)")
    evidence2 = {'Burglary': True}
    print("Rejection (N=20000):", sampler.rejection_sampling('Alarm', evidence2, N=20000))
    print("Likelihood (N=20000):", sampler.likelihood_weighting('Alarm', evidence2, N=20000))
    print("Gibbs (N=5000):", sampler.gibbs_sampling('Alarm', evidence2, N=5000, burn_in=1000))
    print("Prior (N=20000 via samples):")
    print("  via rejection (same as above):", sampler.rejection_sampling('Alarm', evidence2, N=20000))