import re

class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Not:
    def __init__(self, arg):
        self.arg = arg
    def __repr__(self):
        return f"~{self.arg}"

class And:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left}&{self.right})"

class Or:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left}|{self.right})"

class Implies:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left}->{self.right})"

class Iff:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left}<->{self.right})"

#Tokeniser
token_spec = [
    ("SKIP", r"[ \t\n]+"),
    ("IFF", r"<->"),
    ("IMPL", r"->"),
    ("AND", r"&"),
    ("OR", r"\|"),
    ("NOT", r"~"),
    ("LP", r"\("),
    ("RP", r"\)"),
    ("NAME", r"[A-Za-z][A-Za-z0-9_]*"),
]
tok_regex = "|".join("(?P<%s>%s)" % p for p in token_spec)
get_token = re.compile(tok_regex).match #get next token

def tokenize(s):
    pos = 0
    tokens = []
    m = get_token(s, pos)
    while m:
        typ = m.lastgroup
        if typ != "SKIP":
            tokens.append((typ, m.group(0)))
        pos = m.end()
        m = get_token(s, pos)
    if pos != len(s):
        raise SyntaxError("Unexpected: %r" % s[pos:])
    tokens.append(("EOF", ""))
    return tokens

class Parser:
    def __init__(self, s):
        self.tokens = tokenize(s)
        self.pos = 0
    def peek(self):
        return self.tokens[self.pos][0]
    def accept(self, typ=None):
        tok = self.tokens[self.pos]
        if typ is None or tok[0] == typ:
            self.pos += 1
            return tok
        return None
    def expect(self, typ):
        tok = self.accept(typ)
        if not tok:
            raise SyntaxError(f"Expected {typ}, got {self.tokens[self.pos]}")
        return tok
    def parse(self):
        node = self.parse_iff()
        self.expect("EOF")
        return node
    def parse_iff(self):
        left = self.parse_impl()
        while self.peek() == "IFF":
            self.accept("IFF")
            right = self.parse_impl()
            left = Iff(left,right)
        return left
    def parse_impl(self):
        left = self.parse_or()
        while self.peek() == "IMPL":
            self.accept("IMPL")
            right = self.parse_or()
            left = Implies(left,right)
        return left
    def parse_or(self):
        left = self.parse_and()
        while self.peek() == "OR":
            self.accept("OR")
            right = self.parse_and()
            left = Or(left,right)
        return left
    def parse_and(self):
        left = self.parse_not()
        while self.peek() == "AND":
            self.accept("AND")
            right = self.parse_not()
            left = And(left,right)
        return left
    def parse_not(self):
        if self.peek() == "NOT":
            self.accept("NOT")
            return Not(self.parse_not())
        return self.parse_atom()
    def parse_atom(self):
        if self.peek() == "LP":
            self.accept("LP")
            node = self.parse_iff()
            self.expect("RP")
            return node
        return Var(self.expect("NAME")[1])

# CNF
def eliminate_iff(n):
    if isinstance(n, Iff):
        return And(Implies(eliminate_iff(n.left), eliminate_iff(n.right)),
                   Implies(eliminate_iff(n.right), eliminate_iff(n.left)))
    if isinstance(n, (Implies,And,Or)):
        return type(n)(eliminate_iff(n.left), eliminate_iff(n.right))
    if isinstance(n, Not):
        return Not(eliminate_iff(n.arg))
    return n

def eliminate_implies(n):
    if isinstance(n, Implies):
        return Or(Not(eliminate_implies(n.left)), eliminate_implies(n.right))
    if isinstance(n, (And,Or)):
        return type(n)(eliminate_implies(n.left), eliminate_implies(n.right))
    if isinstance(n, Not):
        return Not(eliminate_implies(n.arg))
    return n

def move_not_inward(n):
    if isinstance(n, Not):
        a = n.arg
        if isinstance(a, Not):
            return move_not_inward(a.arg)
        if isinstance(a, And):
            return Or(move_not_inward(Not(a.left)), move_not_inward(Not(a.right)))
        if isinstance(a, Or):
            return And(move_not_inward(Not(a.left)), move_not_inward(Not(a.right)))
        return n
    if isinstance(n, (And,Or)):
        return type(n)(move_not_inward(n.left), move_not_inward(n.right))
    return n

def distribute_or_over_and(n):
    if isinstance(n, Or):
        A, B = distribute_or_over_and(n.left), distribute_or_over_and(n.right)
        if isinstance(A, And):
            return And(distribute_or_over_and(Or(A.left,B)), distribute_or_over_and(Or(A.right,B)))
        if isinstance(B, And):
            return And(distribute_or_over_and(Or(A,B.left)), distribute_or_over_and(Or(A,B.right)))
        return Or(A,B)
    if isinstance(n, And):
        return And(distribute_or_over_and(n.left), distribute_or_over_and(n.right))
    return n

def to_cnf(s):
    t = Parser(s).parse()
    t = eliminate_iff(t)
    t = eliminate_implies(t)
    t = move_not_inward(t)
    t = distribute_or_over_and(t)
    clauses=[]
    def extract(n):
        if isinstance(n, And): extract(n.left); extract(n.right)
        else:
            lits=set()
            def collect(x):
                if isinstance(x, Or):
                    collect(x.left)
                    collect(x.right)
                elif isinstance(x, Not) and isinstance(x.arg, Var):
                    lits.add("~"+x.arg.name)
                elif isinstance(x, Var):
                    lits.add(x.name)
                else:
                    raise ValueError("Unexpected node:"+repr(x))
            collect(n)
            clauses.append(frozenset(lits))
    extract(t)
    return clauses

# Resolution
def complement(lit):
    return lit[1:] if lit.startswith("~") else "~"+lit

def resolve(ci,cj):
    resolvents=set()
    for d in ci:
        if complement(d) in cj:
            r=(ci-{d})|(cj-{complement(d)})
            resolvents.add(frozenset(r))
    return resolvents

def pl_resolution(premises, goal, max_steps=10000):
    prem=[]
    for p in premises: prem.extend(to_cnf(p))
    neg_goal=to_cnf("~("+goal+")")
    clauses_list=[]; provenance={}; idmap={}
    def add(cl,p1=None,p2=None):
        if cl in idmap:
            return idmap[cl]
        cid=len(clauses_list)
        clauses_list.append(cl)
        idmap[cl]=cid
        provenance[cid]=(p1,p2)
        return cid
    for c in prem:
        add(c)
    sos=set(neg_goal)
    for c in sos:
        add(c)
    all_clauses=set(idmap.keys())
    steps=0
    while steps<max_steps:
        new=set()
        for ci in list(sos):
            for cj in list(all_clauses):
                if ci==cj:
                    continue
                for r in resolve(ci,cj):
                    if not r:
                        pid1,pid2=idmap[ci],idmap[cj]
                        nil_id=add(frozenset(),pid1,pid2)
                        trace=[(i,clauses_list[i],provenance[i][0],provenance[i][1]) for i in range(len(clauses_list))]
                        return True,steps+1,trace
                    if r not in all_clauses: new.add(r)
        if not new: break
        for r in new:
            ci,cj=list(sos)[0],list(all_clauses)[0]
            add(r,idmap[ci],idmap[cj])
        all_clauses|=new; sos=new; steps+=1
    trace=[(i,clauses_list[i],provenance[i][0],provenance[i][1]) for i in range(len(clauses_list))]
    return False,steps,trace

def print_trace(trace):
    print("\nProof Trace:")
    for cid,cl,p1,p2 in trace:
        clause=" | ".join(sorted(cl)) if cl else "NIL"
        print(f"{cid:3}: {clause:30}   parents: {p1}, {p2}")

if __name__=="__main__":
    premises=["(A & B) -> C", "C -> B"]
    goal="A"
    proven,steps,trace=pl_resolution(premises,goal)
    print("Proved?",proven,"| Steps:",steps)
    print_trace(trace)
