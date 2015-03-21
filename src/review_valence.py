import json_reader
import valence_data
import general_membership_functions
import json
from collections import OrderedDict
import inferencer

# constant that denotes that
# a word is not found in the
# valence data set
DOES_NOT_EXIST = 10

# a constant that denotes that
# a 'pos' tag did not have
# a word with a 'max' valence
INIT_MAX_VALENCE = 0

# This class acts as a wrapper around the
# ReviewJsonReader and the ValenceData
# classes to score words based on the
# valence data set.
class ReviewValence:
    def __init__(self):
        self.review_json = json_reader.ReviewJsonReader(
                 './data/yelp_academic_dataset_review.json',
                 './output/yelp_review_output.json')
        self.review_json.open_input_file()
        self.review_json.read_input_file()
        self.valence_data = valence_data.ValenceData('./data/valence.txt')
        self.valence_data.process_data()
        self.input_mem_functions = general_membership_functions.InputMembershipFunction()
        self.output_mem_functions = general_membership_functions.OutputMembershipFunction()
        self.unique_non_valence_words = {}
        self.output_non_valence = open('./data/output_non_valence.txt', 'w+')
        # An array of review elements. Each review element contains
        # a map with a key for each 'POS tag' and its corresponding 
        # value to be the 'max' valence.
        # The 'max' valence is simply the maximum of the valences of
        # the words for each 'POS tag'. 
        self.output_pos_max_valence = []

        self.init_inferencer()

        self.input_dict_inferencer = {}

    def init_inferencer(self):
        # Only verbs
        self._rule0 = inferencer.Rule('IF verb is low_pos THEN orientation is f1')
        self._rule1 = inferencer.Rule('IF verb is med_pos THEN orientation is f1')
        self._rule2 = inferencer.Rule('IF verb is high_pos THEN orientation is f1')
        self._rule3 = inferencer.Rule('IF verb is low_neg THEN orientation is f1')
        self._rule4 = inferencer.Rule('IF verb is med_neg THEN orientation is f1')
        self._rule5 = inferencer.Rule('IF verb is high_neg THEN orientation is f1')

        # Only adjectives
        self._rule6 = inferencer.Rule('IF adjective is low_pos THEN orientation is f1')
        self._rule7 = inferencer.Rule('IF adjective is med_pos THEN orientation is f1')
        self._rule8 = inferencer.Rule('IF adjective is high_pos THEN orientation is f1')
        self._rule9 = inferencer.Rule('IF adjective is low_neg THEN orientation is f1')
        self._rule10 = inferencer.Rule('IF adjective is med_neg THEN orientation is f1')
        self._rule11 = inferencer.Rule('IF adjective is high_neg THEN orientation is f1')   

        # Only adverbs
        self._rule12 = inferencer.Rule('IF adverb is low_pos THEN orientation is f1')
        self._rule13 = inferencer.Rule('IF adverb is med_pos THEN orientation is f1')
        self._rule14 = inferencer.Rule('IF adverb is high_pos THEN orientation is f1')
        self._rule15 = inferencer.Rule('IF adverb is low_neg THEN orientation is f1')
        self._rule16 = inferencer.Rule('IF adverb is med_neg THEN orientation is f1')
        self._rule17 = inferencer.Rule('IF adverb is high_neg THEN orientation is f1')  

        # Only nouns
        self._rule18 = inferencer.Rule('IF noun is low_pos THEN orientation is f1')
        self._rule19 = inferencer.Rule('IF noun is med_pos THEN orientation is f1')
        self._rule20 = inferencer.Rule('IF noun is high_pos THEN orientation is f1')
        self._rule21 = inferencer.Rule('IF noun is low_neg THEN orientation is f1')
        self._rule22 = inferencer.Rule('IF noun is med_neg THEN orientation is f1')
        self._rule23 = inferencer.Rule('IF noun is high_neg THEN orientation is f1')

        # Here f2 may be a function such that f2 = sqrt(f1)
        # This is because two POS TAGs are being fired in conjunction -> so the consequent membership
        # function may be made less fuzzy?
        # Verbs and adverbs
        self._rule24 = inferencer.Rule('IF verb is low_pos AND adverb is low_pos THEN orientation is f2')
        self._rule25 = inferencer.Rule('IF verb is med_pos AND adverb is low_pos THEN orientation is f2')
        self._rule26 = inferencer.Rule('IF verb is high_pos AND adverb is low_pos THEN orientation is f2')
        self._rule27 = inferencer.Rule('IF verb is low_neg AND adverb is low_pos THEN orientation is f2')
        self._rule28 = inferencer.Rule('IF verb is med_neg AND adverb is low_pos THEN orientation is f2')
        self._rule29 = inferencer.Rule('IF verb is high_neg AND adverb is low_pos THEN orientation is f2')

        # Nouns and adjectives
        self._rule30 = inferencer.Rule('IF noun is low_pos AND adjective is low_pos THEN orientation is f2')
        self._rule31 = inferencer.Rule('IF noun is med_pos AND adjective is med_pos THEN orientation is f2')
        self._rule32 = inferencer.Rule('IF noun is high_pos AND adjective is high_pos THEN orientation is f2')
        self._rule33 = inferencer.Rule('IF noun is low_neg AND adjective is low_neg THEN orientation is f2')
        self._rule34 = inferencer.Rule('IF noun is med_neg AND adjective is med_neg THEN orientation is f2')
        self._rule35 = inferencer.Rule('IF noun is high_neg AND adjective is high_neg THEN orientation is f2')

        self._rules = [ 
                        self._rule0,
                        self._rule1,
                        self._rule2,
                        self._rule3,
                        self._rule4,
                        self._rule5,
                        self._rule6,
                        self._rule7,
                        self._rule8,
                        self._rule9,
                        self._rule10,
                        self._rule11,
                        self._rule12,
                        self._rule13,
                        self._rule14,
                        self._rule15,
                        self._rule16,
                        self._rule17,
                        self._rule18,
                        self._rule19,
                        self._rule20,
                        self._rule21,
                        self._rule22,
                        self._rule23,
                        self._rule24,
                        self._rule25,
                        self._rule26,
                        self._rule27,
                        self._rule28,
                        self._rule29,
                        self._rule30,
                        self._rule31,
                        self._rule32,
                        self._rule33,
                        self._rule34,
                        self._rule35]

        self.review_inferencer = inferencer.Inferencer(*self._rules)

    # Iterates through the first 'num_reviews'
    # For each review it looks up the valence
    # score for each word across all POS tags.
    def process_reviews(self, num_reviews):
        # Should return the first ten json records
        for i in range(num_reviews):
            self.review_json.process_record()
        # review_output is a map with the key being a POS Tag
        # and the value an array of words falling into that
        # POS Tag category.
        print "Iterating through review json data"
        for review_output in self.review_json.pos_tag_review_output:
            # Per review iterate through all the pos tags and associated
            # list of words
            word_with_valence_count = 0
            review_words_count = 0
            pos_tag_max_valence = OrderedDict()

            for pos_tag, words in review_output.items():
                # Check if word exists in the valence data
                max_valence = INIT_MAX_VALENCE

                for word in words:
                    review_words_count += 1
                    valence_score = self.get_valence_score(word)
                    if valence_score != DOES_NOT_EXIST:
                        # To ensure that if words have a 
                        # valence of -3, and +2: then -3 
                        # would be preferred.
                        abs_valence_score = abs(int(valence_score))

                        if abs_valence_score > max_valence:
                            max_valence = abs_valence_score
                            pos_tag_max_valence[pos_tag] = (int(valence_score), word)
                        word_with_valence_count += 1
                    else:
                        if word not in self.unique_non_valence_words:
                            self.unique_non_valence_words[word] = 1
                        else:
                            self.unique_non_valence_words[word] += 1
            print "Percent of words found in valence dataset ", word_with_valence_count / float(review_words_count) * 100

            # Append the max_valence map data to the output array
            self.output_pos_max_valence.append(pos_tag_max_valence)

        print "Iterating through non-valence data"
        for word, count in self.unique_non_valence_words.items():
            try:
                self.output_non_valence.write(word + "=" + str(count) + '\n')
            except UnicodeEncodeError:
                print "Encoding error - proceeding with next word"

        print "Inferencing"
        # Iterate through the max_valence data and get inferencing!
        for review in self.output_pos_max_valence:
            for pos_tag, tup in review.items():
                self.map_inputs_membership_function(pos_tag, tup[0], tup[1])
                self.map_outputs_membership_function()
            output = self.review_inferencer.infer(**(self.input_dict_inferencer))
            
            print "Final output", output(5)
            self.clear_rules()

    # Valence scores from the data source lie between
    # [-5, 5]. It returns the score based on the 
    # map generated by the ValenceData object.
    def get_valence_score(self, word):
        if word in self.valence_data._data_map:
            return self.valence_data._data_map[word]
        return DOES_NOT_EXIST

    # Must be called per review
    # Will set up the dict object such that it can be 
    # used for inferencing
    def map_inputs_membership_function(self, pos_tag, valence, word):

        valence_lp_lambda = lambda word : self.input_mem_functions.get_low_positive_membership(valence)
        valence_mp_lambda = lambda word : self.input_mem_functions.get_moderate_positive_membership(valence)
        valence_hp_lambda = lambda word : self.input_mem_functions.get_high_positive_membership(valence)
        valence_ln_lambda = lambda word : self.input_mem_functions.get_low_negative_membership(valence)
        valence_mn_lambda = lambda word : self.input_mem_functions.get_moderate_negative_membership(valence)
        valence_hn_lambda = lambda word : self.input_mem_functions.get_high_negative_membership(valence)

        if pos_tag == 'JJ':
            self.input_dict_inferencer['adjective'] = word
            self._rule6.if_('adjective', valence_lp_lambda)
            self._rule7.if_('adjective', valence_mp_lambda)
            self._rule8.if_('adjective', valence_hp_lambda)
            self._rule9.if_('adjective', valence_ln_lambda)
            self._rule10.if_('adjective', valence_mn_lambda)
            self._rule11.if_('adjective', valence_hn_lambda)

            self._rule30.if_('adjective', valence_lp_lambda)
            self._rule31.if_('adjective', valence_mp_lambda)
            self._rule32.if_('adjective', valence_hp_lambda)
            self._rule33.if_('adjective', valence_ln_lambda)
            self._rule34.if_('adjective', valence_mn_lambda)
            self._rule35.if_('adjective', valence_hn_lambda)
        elif pos_tag == 'VB':
            self.input_dict_inferencer['verb'] = word
            self._rule0.if_('verb', valence_lp_lambda)
            self._rule1.if_('verb', valence_mp_lambda)
            self._rule2.if_('verb', valence_hp_lambda)
            self._rule3.if_('verb', valence_ln_lambda)
            self._rule4.if_('verb', valence_mn_lambda)
            self._rule5.if_('verb', valence_hn_lambda)

            self._rule7.if_('verb', valence_lp_lambda)
            self._rule8.if_('verb', valence_mp_lambda)
            self._rule9.if_('verb', valence_hp_lambda)
            self._rule10.if_('verb', valence_ln_lambda)
            self._rule11.if_('verb', valence_mn_lambda)
            self._rule12.if_('verb', valence_hn_lambda)

            self._rule24.if_('verb', valence_lp_lambda)
            self._rule25.if_('verb', valence_mp_lambda)
            self._rule26.if_('verb', valence_hp_lambda)
            self._rule27.if_('verb', valence_ln_lambda)
            self._rule28.if_('verb', valence_mn_lambda)
            self._rule29.if_('verb', valence_hn_lambda)
        elif pos_tag == 'NN':
            self.input_dict_inferencer['noun'] = word

            self._rule18.if_('noun', valence_lp_lambda)
            self._rule19.if_('noun', valence_mp_lambda)
            self._rule20.if_('noun', valence_hp_lambda)
            self._rule21.if_('noun', valence_ln_lambda)
            self._rule22.if_('noun', valence_mn_lambda)
            self._rule23.if_('noun', valence_hn_lambda)

            self._rule30.if_('noun', valence_lp_lambda)
            self._rule31.if_('noun', valence_mp_lambda)
            self._rule32.if_('noun', valence_hp_lambda)
            self._rule33.if_('noun', valence_ln_lambda)
            self._rule34.if_('noun', valence_mn_lambda)
            self._rule35.if_('noun', valence_hn_lambda)
        elif pos_tag == 'RB':
            self.input_dict_inferencer['adverb'] = word 

            self._rule12.if_('adverb', valence_lp_lambda)
            self._rule13.if_('adverb', valence_mp_lambda)
            self._rule14.if_('adverb', valence_hp_lambda)
            self._rule15.if_('adverb', valence_ln_lambda)
            self._rule16.if_('adverb', valence_mn_lambda)
            self._rule17.if_('adverb', valence_hn_lambda)

            self._rule24.if_('adverb', valence_lp_lambda)
            self._rule25.if_('adverb', valence_mp_lambda)
            self._rule26.if_('adverb', valence_hp_lambda)
            self._rule27.if_('adverb', valence_ln_lambda)
            self._rule28.if_('adverb', valence_mn_lambda)
            self._rule29.if_('adverb', valence_hn_lambda)

    def map_outputs_membership_function(self):
        #output_lambda = lambda word : self.output_mem_functions.get_low_rating(2)
        output_lambda = lambda x : x
        #output_lambda_sqrt = lambda x : sqrt(x)
        self._rule0.then('orientation', output_lambda)
        self._rule1.then('orientation', output_lambda)
        self._rule2.then('orientation', output_lambda)
        self._rule3.then('orientation', output_lambda)
        self._rule4.then('orientation', output_lambda)
        self._rule5.then('orientation', output_lambda)
        self._rule6.then('orientation', output_lambda)

        self._rule7.then('orientation', output_lambda)
        self._rule8.then('orientation', output_lambda)
        self._rule9.then('orientation', output_lambda)
        self._rule10.then('orientation', output_lambda)
        self._rule11.then('orientation', output_lambda)
        self._rule12.then('orientation', output_lambda)

        self._rule13.then('orientation', output_lambda)
        self._rule14.then('orientation', output_lambda)
        self._rule15.then('orientation', output_lambda)
        self._rule16.then('orientation', output_lambda)
        self._rule17.then('orientation', output_lambda)
        self._rule18.then('orientation', output_lambda)

        self._rule19.then('orientation', output_lambda)
        self._rule20.then('orientation', output_lambda)
        self._rule21.then('orientation', output_lambda)
        self._rule22.then('orientation', output_lambda)
        self._rule23.then('orientation', output_lambda)

        self._rule24.then('orientation', output_lambda)
        self._rule25.then('orientation', output_lambda)
        self._rule26.then('orientation', output_lambda)
        self._rule27.then('orientation', output_lambda)
        self._rule28.then('orientation', output_lambda)
        self._rule29.then('orientation', output_lambda)

        self._rule30.then('orientation', output_lambda)
        self._rule31.then('orientation', output_lambda)
        self._rule32.then('orientation', output_lambda)
        self._rule33.then('orientation', output_lambda)
        self._rule34.then('orientation', output_lambda)
        self._rule35.then('orientation', output_lambda)

    def clear_rules(self):
        for rule in self._rules:
            rule.clear()

############### MAIN ###############
if __name__ == '__main__':
    rv = ReviewValence()
    rv.process_reviews(int(10))
