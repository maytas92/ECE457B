import membership_function

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
        self.low_positive = membership_function.Triangle(0, 0, 2)
        self.moderate_positive = membership_function.Triangle(1.75, 2.75, 4)
        self.high_positive = membership_function.Triangle(3, 5, 5)

        self.low_negative = membership_function.Triangle(-2, 0, 0)
        self.moderate_negative = membership_function.Triangle(-4, -2.75, -1.5)
        self.high_negative = membership_function.Triangle(-5, -5, -3)

    def get_low_positive_membership(self, x):
        return self.low_positive.get_membership(x)

    def get_moderate_positive_membership(self, x):
        return self.moderate_positive.get_membership(x)

    def get_high_positive_membership(self, x):
        return self.high_positive.get_membership(x)

    def get_low_negative_membership(self, x):
        return self.low_negative.get_membership(x)

    def get_moderate_negative_membership(self, x):
        return self.moderate_negative.get_membership(x)

    def get_high_negative_membership(self, x):
        return self.high_negative.get_membership(x)

class OutputMembershipFunction:
    def __init__(self):
        self.low_rating = membership_function.Triangle(0, 0, 2)
        self.moderate_rating = membership_function.Triangle(1.5, 2.75, 4)
        self.high_rating = membership_function.Triangle(3, 5, 5)

    def get_low_rating(self, x):
        return self.low_rating.get_membership(x)

    def get_moderate_rating(self, x):
        return self.moderate_rating(x)

    def get_high_rating(self, x):
        return self.high_rating(x)