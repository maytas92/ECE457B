from membershipfunction import Triangle
from math import pow

class InputMembershipFunction:
    # http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5561583
    # Based on the Membership function design section
    # The only difference is that here the range of values on the X axis
    # belong to the interval [-5, 5]. Any value that is less than
    # 0 would be part of a 'negative' membership function and vice versa.
    # There are three degress of membership functions: 'low', 'moderate'
    # and 'high'. The 'low' is a left clipped one, 'moderate' is a normal
    # triangular function and the 'high' is a right clipped one.
    def __init__(self):
        # Set up membership functions to allow for overlap
        self.low_positive = Triangle(0, 0, 2)
        self.moderate_positive = Triangle(1.75, 2.75, 4)
        self.high_positive = Triangle(3, 5, 5)

        self.low_negative = Triangle(-2, 0, 0)
        self.moderate_negative = Triangle(-4, -2.75, -1.5)
        self.high_negative = Triangle(-5, -5, -3)

    def get_low_positive_membership(self, x):
        return self.low_positive(x)

    def get_moderate_positive_membership(self, x):
        return self.moderate_positive(x)

    def get_high_positive_membership(self, x):
        return self.high_positive(x)

    def get_low_negative_membership(self, x):
        return self.low_negative(x)

    def get_moderate_negative_membership(self, x):
        return self.moderate_negative(x)

    def get_high_negative_membership(self, x):
        return self.high_negative(x)

class OutputMembershipFunction:
    def __init__(self):
        self.low_rating = Triangle(0, 0, 2)
        self.moderate_rating = Triangle(1.5, 2.5, 3.5)
        self.high_rating = Triangle(3, 5, 5)

    def get_low_rating(self, x):
        return self.low_rating(x)

    def get_very_low_rating(self, x):
        return pow(self.low_rating.get_membership(x), 2)

    def get_moderate_rating(self, x):
        return self.moderate_rating.get_membership(x)

    def get_very_moderate_rating(self, x):
        return pow(self.moderate_rating.get_membership(x), 2)

    def get_high_rating(self, x):
        return self.high_rating.get_membership(x)

    def get_very_high_rating(self, x):
        return pow(self.high_rating.get_membership(x), 2)
