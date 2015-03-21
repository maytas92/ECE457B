class Defuzzifier:

    def __init__(self):
        pass
    def xfrange(self, start, stop, step):
        while start < stop:
            yield start
            start += step
    def defuzzify(self, f, start, end, step_size=1e-3):
        weight_sum = 0
        total_sum =0
        for x in self.xfrange(start, end, step_size):
            total_sum += f(x) * x
            weight_sum += f(x)
        if weight_sum > 0 :
            return total_sum/weight_sum
        else :
            return 0

    def __call__(self,*args,**kwargs):
         return self.defuzzify(*args,**kwargs)
