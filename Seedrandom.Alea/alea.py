import z3

class Alea:
    def __init__(self, s0, s1, s2):
        self.s0 = s0
        self.s1 = s1
        self.s2 = s2
        self.c = 1
        self.norm32 = 2.3283064365386963e-10

    def next(self):
        t = 2091639.0 * self.s0 + self.c * self.norm32
        self.s0 = self.s1
        self.s1 = self.s2
        self.c = int(t)
        self.s2 = t - self.c
        return self.s2

def recover(ys, truncation):
    S  = z3.Solver()
    s0 = z3.FP("s0", z3.Float64())
    s1 = z3.FP("s1", z3.Float64())
    s2 = z3.FP("s2", z3.Float64())
    c  = z3.FP("c",  z3.Float64())

    # Rounding mode that matches python, js etc
    rm = z3.RNA()

    def __alea_sym(s0, s1, s2, c):
        a = z3.fpMul(rm, z3.FPVal("2091639.0", z3.Float64()), s0)
        b = z3.fpMul(rm, c, z3.FPVal("2.3283064365386963e-10", z3.Float64()))
        t = z3.fpAdd(rm, a, b)
        s0 = s1
        s1 = s2
        c = z3.fpRoundToIntegral(z3.RTZ(), t) # RTZ = Round Towards Zero
        s2 = z3.simplify(z3.fpSub(rm, t, c))
        return s0, s1, s2, c

    ## add constraints
    t0, t1, t2, t3 = s0, s1, s2, 1
    for y in ys:
        t0, t1, t2, t3 = __alea_sym(t0, t1, t2, t3)
        S.add(z3.fpRoundToIntegral(
            z3.RTZ(), z3.fpMul(rm, t2, z3.FPVal(str(truncation), z3.Float64()))) == y)

    status = S.check()
    if status == z3.unsat:
        raise Exception("Sequence is not recoverable")
    m = S.model()

    return(eval(str(m[s0])), eval(str(m[s1])), eval(str(m[s2])))
    c = 1

if __name__ == "__main__":

    # seeds, unknown to solver program
    S0 = 0.12519603282416938
    S1 = 0.53323355343424444
    S2 = 0.32519603282416938

    # this is just an example, should probably be adjusted
    truncation = 0x1000000

    n_samples = 8
    alea = Alea(S0, S1, S2)
    ys = [int(alea.next() * truncation) for _ in range(n_samples)]

    print("Supplied keystream: {}".format(ys))
    alea_recovered = Alea(*recover(ys, truncation))

    print("Predicted random values:")
    print([int(alea_recovered.next() * truncation) for _ in range(n_samples + 20)])

    alea = Alea(S0, S1, S2)

    print("Reference (correct) random values:")
    print([int(alea.next() * truncation) for _ in range(n_samples + 20)])
