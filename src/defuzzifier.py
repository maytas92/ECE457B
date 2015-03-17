def defuzzifier(f, start, end, step_size=1e-3):
    wieght_sum = 0
    total_sum =0
    for x in xrange(start, end, step_size):
        total_sum += f(x) * x
        wieght_sum += f(x)
    return total_sum/wieght_sum
