# Represents the elements of a fuzzy set
# X with a triangular membership function.
# Example call:
# t = Triangle(0, 3, 6)
# Subsequently, the object 't' may be used
# to find the degree of membership of an
# input 'x' in the fuzzy set X.
class Triangle:
    # A triangular membership function is characterized
    # by three parameters - a, b, and c.
    def __init__(self, a, b, c):
        if a > b or b > c:
            raise Exception("Invalid parameters when constructing a triangular membership function." +
                                            "Ensure the inputs are such that 'a' <='b' <= 'c'")
        self._a = a
        self._b = b
        self._c = c

    # Returns the membership of an element 'x' 
    # based on the triangular membership function
    # parameter 'a', 'b' and 'c'. 
    def get_membership(self, x, num_digits_precision=4):
        if x < self._a:
            return 0
        elif x >= self._a and x <= self._b:
            if self._a == self._b:
                return 1
            return round((x - self._a) / float(self._b - self._a), num_digits_precision)
        elif x >= self._b and x <= self._c:
            if self._b == self._c:
                return 1
            return round((self._c - x) / float(self._c - self._b), num_digits_precision)
        elif x > self._c:
            return 0

def main():
    # A typical triangular membership function
    t1 = Triangle(0, 3, 6)
    # A triangular membership function that is clipped
    # from the left hand side
    t2 = Triangle(0, 0, 5)
    # A triangular membership function that is clipped
    # from the right hand side
    t3 = Triangle(3, 6, 6)

    # A triangular membership function with negative integer
    # input
    t4 = Triangle(0, -2, -2)
    # invalid triangular membership functions
    #t4 = Triangle(1, 0, 3)
    #t5 = Triangle(1, 3, 2)

    print "Testing a normal triangular membership function"
    for i in range(-1, 8):
        print "x=", i, " membership=", t1.get_membership(i, 2)

    print "Testing the left clipped triangular membership function"
    for i in range(-1, 7):
        print "x=", i, " membership=", t2.get_membership(i)

    print "Testing the right clipped triangular membership function"
    for i in range(2, 8):
        print "x=", i, " membership=", t3.get_membership(i)

    print "Testing the triangular membership function with negative input"
    for i in ranage(-3, 1):
        print "x=", i, " membership=", t4.get_membership(i)
        
if __name__ == '__main__':
    main()
