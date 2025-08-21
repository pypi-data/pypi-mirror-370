import numpy as np
from contextlib import contextmanager

epsilon: float = 0
spent: float = 0
unspent: float = 0

@contextmanager
def budget(e: float):
    global epsilon
    global spent
    global unspent
    old_epsilon = epsilon
    old_spent = spent
    new_epsilon = e + unspent
    try:
        epsilon = new_epsilon
        unspent = 0
        spent = 0
        yield
    finally:
        epsilon = old_epsilon
        unspent = new_epsilon - spent
        spent = old_spent + spent
        print(f"unspent epsilon: {unspent}")



@contextmanager
def spend(p: float = 100):
    global epsilon
    global spent
    global unspent
    old_epsilon = epsilon
    new_epsilon = p / 100.0 * epsilon + unspent
    if new_epsilon > epsilon - spent:
        raise ValueError("Cannot spend more than the current budget")
    try:
        epsilon = new_epsilon
        yield
    finally:
        print(f"spent: {epsilon}!")
        spent = spent + new_epsilon
        unspent = 0
        epsilon = old_epsilon

@contextmanager
def unsafe_spend(p: float = 100):
    global epsilon
    global spent
    global unspent
    old_epsilon = epsilon
    old_spent = spent
    new_epsilon = p / 100.0 * epsilon + unspent
    if new_epsilon > epsilon - spent:
        raise ValueError("Cannot spend more than the current budget")
    try:
        epsilon = new_epsilon
        spent = -float("inf")
        yield
    finally:
        spent = old_spent + new_epsilon
        unspent = 0
        epsilon = old_epsilon

@contextmanager
def consuming(p: float):
    global epsilon
    global spent
    global unspent
    old_epsilon = epsilon
    old_spent = spent
    #print(f"entering consuming new budget: {epsilon}, unspent={unspent}, spent={spent}")
    new_epsilon = p / 100.0 * epsilon + unspent
    if new_epsilon > (epsilon - spent):
        raise ValueError(f"Cannot consume {new_epsilon}, which is bigger than available {epsilon - spent}")
    try:
        epsilon = new_epsilon
        unspent = 0
        spent = 0
        yield
    finally:
        epsilon = old_epsilon
        unspent = new_epsilon - spent
        spent = old_spent + spent
        #print(f"exiting consuming new budget: {epsilon}, unspent={unspent}, spent={spent}")



class PDIterator:
    def __init__(self, iter, f=lambda i,n: 1):
        global epsilon
        global spent
        self.old_epsilon = epsilon
        self.old_spent = spent

        self.i = 0
        self.iter = iter
        self.eps = [f(i, len(iter)) for i in range(0,len(iter))]
        total = sum(self.eps)
        self.eps = [x/total*epsilon for x in self.eps]
        spent = 0


    def __iter__(self):
        return self

    def __next__(self):
        i = self.i
        self.i += 1
        global epsilon
        global spent
        global unspent


        if(i >= len(self.iter)):
            #the exit of consuming
            epsilon = self.old_epsilon
            unspent = self.eps[i - 1] - spent if len(self.iter)>0 else unspent
            spent = self.old_spent + spent
            raise StopIteration
        else:
            if i > 0:
                #this is the exit of a consuming
                epsilon = self.old_epsilon
                unspent = self.eps[i - 1] - spent
                spent = self.old_spent + spent

            self.old_epsilon = epsilon
            self.old_spent = spent
            #distribute unspent in the rest of the iterations
            if unspent>0:
                e_chunk = unspent/(len(self.eps)-i)
                self.eps = self.eps[:i] + [x + e_chunk for x in self.eps[i:]]
            epsilon = self.eps[i]
            unspent = 0
            spent = 0
            return self.iter[i]

def foo(x):
    laplace_mechanism(10, 1)



def laplace_mechanism(x: float, sens: float) -> float:
    with spend():
        return x + np.random.laplace(loc=0, scale=sens / epsilon)

def above_threshold(queries, df, T):
    with unsafe_spend():
        T_hat = laplace_mechanism(T, 2)
        for idx, q in enumerate(queries):
            nu_i = laplace_mechanism(0, 4)
            if q(df) + nu_i >= T_hat:
                return id
        return None


def f():
    with consuming(40): laplace_mechanism(10, 1)
    with consuming(60): laplace_mechanism(10, 1)

with budget(10):
    with consuming(50):
        [laplace_mechanism(x, 1) for x in PDIterator(range(0,10), lambda i,n: 1/pow(2,n-i))]
    with consuming(30):
        laplace_mechanism(10, 1)
    with consuming(10):
        f()




