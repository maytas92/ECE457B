_DEBUG = 0
# Object for building rules. Example call:
#   rule = Rule(<optional english expression of the rule>)
#   rule.if_('verb', f1).and_('adjective', f2).then('adverb', f3)
# Must specify a 'then' membership function.
class Rule(object):
    def __init__(self, rulename=None, **kwargs):
        self._rulename = rulename #optional parameter, useful for debugging
        self._conditions = []
        self._consequence = None

    # Add an 'if' condition to the rule. Ideally, you should only
    # call this at the beginning. Subsequent calls should be made to
    # the 'and_' function.
    def if_(self, variable_name, membership_function):
        self._conditions.append((variable_name, membership_function,))
        return self

    # Add an 'and' condition to the rule. Ideally, you should
    # only this after an initial call to the 'if_' function.
    def and_(self, *args, **kwargs):
        return self.if_(*args, **kwargs)

    # Object for building rules. Example call:
    #   rule = Rule()
    #   rule.if_('verb', f1).and_('adjective', f2).then('adverb', f3)
    # Must specify a 'then' membership function.
    def then(self, variable_name, membership_function):
        self._consequence = (variable_name, membership_function,)
        return self

    def get_conditions(self):
        return self._conditions

    def get_consequence(self):
        if not self._consequence:
            raise Exception("Consequence not specified for this rule '%s'" % (self._rulename,))
        return self._consequence[1]

    def clear(self):
        self._conditions = []
        self._consequence = None

    def describe(self):
        return self._rulename

# Performs fuzzy inferencing. The constructor takes in undefined
# number of 'Rule' objects. Example call:
#   inferencer = Inferencer(rule1, rule2, rule3, ..., ruleN)
class Inferencer(object):
    def __init__(self, *rules, **kwargs):
        self._rules = rules

    # Returns a membership function that represents the output
    # of this rule. 'rule' is an object of type Rule. 'inputs'
    # is a dictionary that maps the input's name to its value.
    def _compute_rule(self, rule, inputs):
        intersections = []
        for (variable_name, membership_function) in rule.get_conditions():
            #print variable_name, membership_function
            if variable_name not in inputs:
                if _DEBUG:
                    print 'Ignoring rule "', rule.describe(), '" due to insufficient parameters'
                continue
                #raise Exception("Input not specified for variable '%s'" % (variable_name,))
            inputvalue = inputs[variable_name]

            intersections.append(membership_function(inputvalue))

        # Empty intersections is false
        if not intersections:
            return lambda x: 0
        # The firing strength is the minimum of all
        # the intersection points.
        firing_strength = min(intersections)


        # The output membership function of this rulue is the firing
        # strength times the consequence membership function
        return lambda x: firing_strength * rule.get_consequence()(x)

    # Performs fuzzy inferencing based on some input values.
    # Rules must be defined over the values passed in.
    # Example call:
    #   inferencer.infer(x=x_value, y=y_value, z=z_value)
    def infer(self, **inputs):
        print inputs
        # Get the consequence membership functions from all the rules
        consequences = map(lambda rule: self._compute_rule(rule, inputs), self._rules)
        # The output membership function at 'x' is the
        # consequence with the highest value at 'x'.
        return lambda x: max(map(lambda c: c(x), consequences))


def main():
    f1 = lambda word: 0.8
    f2 = lambda word: 0.1
    f3 = lambda x: x

    f4 = lambda word: 0.9
    f5 = lambda word: 0.5
    f6 = lambda x: x

    rule1 = Rule('IF verb is f1 AND adjective is f2 THEN adverb is f3')
    rule1.if_('verb', f1).and_('adjective', f2).then('adverb', f3)

    rule2 = Rule('IF verb is f4 AND adjective is f5 THEN adverb is f6')
    rule2.if_('verb', f4).and_('adjective', f5).then('adverb', f6)

    inferencer = Inferencer(rule1, rule2)
    ouptput_membership_function = inferencer.infer(verb='hello', adjective='world')

    print ouptput_membership_function(5) # This should print 2.5

    # After this pass 'ouptput_membership_function' to the defuzzifier.
    # Call would look something this this:
    outputvalue = defuzzifier(output_membership_function, 0.0, 5.0, 1);
    #outputvalue = defuzzifier(ouptput_membership_function, step_size=1e-1)

if __name__ == '__main__':
    main()
