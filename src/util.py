import math

def maxabs(x, y):
    if abs(x) > abs(y):
        return x
    elif abs(x) < abs(y):
        return y
    return 0

def avg(l):
    return sum(l) / len(l) if len(l) > 0 else 0