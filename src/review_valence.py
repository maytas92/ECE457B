#!/usr/bin/python
import json_reader
import valence_data
import general_membership_functions
import json
from collections import OrderedDict
import inferencer
from defuzzifier import Defuzzifier as Defuzzifier
from math import exp

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

        self._build_inference()


    def _build_inference(self):
        low_positive = self.input_mem_functions.get_low_positive_membership
        med_positive = self.input_mem_functions.get_moderate_positive_membership
        high_positive = self.input_mem_functions.get_high_positive_membership

        low_negative = self.input_mem_functions.get_low_negative_membership
        med_negative = self.input_mem_functions.get_moderate_negative_membership
        high_negative = self.input_mem_functions.get_high_negative_membership

        low_otn = lambda x: self.output_mem_functions.get_low_rating(x)
        very_low_otn = lambda x : self.output_mem_functions.get_very_low_rating(x)
        moderate_otn = lambda x: self.output_mem_functions.get_moderate_rating(x)
        very_moderate_otn = lambda x : self.output_mem_functions.get_very_moderate_rating(x)
        high_otn = lambda x: self.output_mem_functions.get_high_rating(x)
        very_high_otn = lambda x: self.output_mem_functions.get_very_high_rating(x)

        # Only verbs
        self._rule0 = inferencer.Rule('IF verb is low_positive THEN orientation is moderate_otn')
        self._rule0.if_('verb', low_positive).then('orientation', moderate_otn)

        self._rule1 = inferencer.Rule('IF verb is med_positive THEN orientation is very_moderate_otn')
        self._rule1.if_('verb', med_positive).then('orientation', very_moderate_otn)

        self._rule2 = inferencer.Rule('IF verb is high_positive THEN orientation is high_otn')
        self._rule2.if_('verb', high_positive).then('orientation', high_otn)

        self._rule3 = inferencer.Rule('IF verb is low_negative THEN orientation is moderate_otn')
        self._rule3.if_('verb', low_negative).then('orientation', moderate_otn)

        self._rule4 = inferencer.Rule('IF verb is med_negative THEN orientation is low_otn')
        self._rule4.if_('verb', med_negative).then('orientation', low_otn)

        self._rule5 = inferencer.Rule('IF verb is high_negative THEN orientation is very_low_otn')
        self._rule5.if_('verb', high_negative).then('orientation', very_low_otn)

        # Only adjectives
        self._rule6 = inferencer.Rule('IF adjective is low_positive THEN orientation is moderate_otn')
        self._rule6.if_('adjective', low_positive).then('orientation', moderate_otn)

        self._rule7 = inferencer.Rule('IF adjective is med_positive THEN orientation is very_moderate_otn')
        self._rule7.if_('adjective', med_positive).then('orientation', very_moderate_otn)

        self._rule8 = inferencer.Rule('IF adjective is high_positive THEN orientation is high_otn')
        self._rule8.if_('adjective', high_positive).then('orientation', high_otn)

        self._rule9 = inferencer.Rule('IF adjective is low_negative THEN orientation is moderate_otn')
        self._rule9.if_('adjective', low_negative).then('orientation', moderate_otn)

        self._rule10 = inferencer.Rule('IF adjective is med_negative THEN orientation is low_otn')
        self._rule10.if_('adjective', med_negative).then('orientation', low_otn)

        self._rule11 = inferencer.Rule('IF adjective is high_negative THEN orientation is very_low_otn')
        self._rule11.if_('adjective', high_negative).then('orientation', very_low_otn)

        # Only adverbs
        self._rule12 = inferencer.Rule('IF adverb is low_positive THEN orientation is moderate_otn')
        self._rule12.if_('adverb', low_positive).then('orientation', moderate_otn)

        self._rule13 = inferencer.Rule('IF adverb is med_positive THEN orientation is very_moderate_otn')
        self._rule13.if_('adverb', med_positive).then('orientation', very_moderate_otn)

        self._rule14 = inferencer.Rule('IF adverb is high_positive THEN orientation is high_otn')
        self._rule14.if_('adverb', high_positive).then('orientation', high_otn)

        self._rule15 = inferencer.Rule('IF adverb is low_negative THEN orientation is moderate_otn')
        self._rule15.if_('adverb', low_negative).then('orientation', moderate_otn)

        self._rule16 = inferencer.Rule('IF adverb is med_negative THEN orientation is low_otn')
        self._rule16.if_('adverb', med_negative).then('orientation', low_otn)

        self._rule17 = inferencer.Rule('IF adverb is high_negative THEN orientation is very_low_otn')
        self._rule17.if_('adverb', high_negative).then('orientation', very_low_otn)

        # Only nouns
        self._rule18 = inferencer.Rule('IF noun is low_positive THEN orientation is moderate_otn')
        self._rule18.if_('noun', low_positive).then('orientation', moderate_otn)

        self._rule19 = inferencer.Rule('IF noun is med_positive THEN orientation is very_moderate_otn')
        self._rule19.if_('noun', med_positive).then('orientation', very_moderate_otn)

        self._rule20 = inferencer.Rule('IF noun is high_positive THEN orientation is high_positive')
        self._rule20.if_('noun', high_positive).then('orientation', high_otn)

        self._rule21 = inferencer.Rule('IF noun is low_negative THEN orientation is moderate_otn')
        self._rule21.if_('noun', low_negative).then('orientation', moderate_otn)

        self._rule22 = inferencer.Rule('IF noun is med_negative THEN orientation is low_otn')
        self._rule22.if_('noun', med_negative).then('orientation', low_otn)

        self._rule23 = inferencer.Rule('IF noun is high_negative THEN orientation is very_low_otn')
        self._rule23.if_('noun', high_negative).then('orientation', very_low_otn)

        # Here f2 may be a function such that f2 = sqrt(f1)
        # This is because two POS TAGs are being fired in conjunction -> so the consequent membership
        # function may be made less fuzzy?
        # Verbs and adverbs
        self._rule24 = inferencer.Rule('IF verb is low_positive AND adverb is low_positive THEN orientation is moderate_otn')
        self._rule24.if_('verb', low_positive).and_('adverb', low_positive).then('orientation', moderate_otn)

        self._rule25 = inferencer.Rule('IF verb is med_positive AND adverb is med_positive THEN orientation is very_moderate_otn')
        self._rule25.if_('verb', med_positive).and_('adverb', low_positive).then('orientation', very_moderate_otn)

        self._rule26 = inferencer.Rule('IF verb is high_positive AND adverb is high_positive THEN orientation is very_high_otn')
        self._rule26.if_('verb', high_positive).and_('adverb', low_positive).then('orientation', very_high_otn)

        self._rule27 = inferencer.Rule('IF verb is low_negative AND adverb is low_negative THEN orientation is moderate_otn')
        self._rule27.if_('verb', low_negative).and_('adverb', low_negative).then('orientation', moderate_otn)

        self._rule28 = inferencer.Rule('IF verb is med_negative AND adverb is med_negative THEN orientation is low_otn')
        self._rule28.if_('verb', med_negative).and_('adverb', med_negative).then('orientation', low_otn)

        self._rule29 = inferencer.Rule('IF verb is high_negative AND adverb is high_negative THEN orientation is very_low_otn')
        self._rule29.if_('verb', high_negative).and_('adverb', high_negative).then('orientation', very_low_otn)

        # Nouns and adjectives
        self._rule30 = inferencer.Rule('IF noun is low_positive AND adjective is low_positive THEN orientation is moderate_otn')
        self._rule30.if_('noun', low_positive).and_('adjective', low_positive).then('orientation', moderate_otn)

        self._rule31 = inferencer.Rule('IF noun is med_positive AND adjective is med_positive THEN orientation is very_moderate_otn')
        self._rule31.if_('noun', med_positive).and_('adjective', med_positive).then('orientation', very_moderate_otn)

        self._rule32 = inferencer.Rule('IF noun is high_positive AND adjective is high_positive THEN orientation is very_high_otn')
        self._rule32.if_('noun', high_positive).and_('adjective', high_positive).then('orientation', very_high_otn)

        self._rule33 = inferencer.Rule('IF noun is low_negative AND adjective is low_negative THEN orientation is moderate_otn')
        self._rule33.if_('noun', low_negative).and_('adjective', low_negative).then('orientation', moderate_otn)

        self._rule34 = inferencer.Rule('IF noun is med_negative AND adjective is med_negative THEN orientation is low_otn')
        self._rule34.if_('noun', med_negative).and_('adjective', med_negative).then('orientation', low_otn)

        self._rule35 = inferencer.Rule('IF noun is high_negative AND adjective is high_negative THEN orientation is very_low_otn')
        self._rule35.if_('noun', high_negative).and_('adjective', high_negative).then('orientation', very_low_otn)

        self._rules = [ self._rule0,  self._rule1,  self._rule2,  self._rule3,  self._rule4,  self._rule5,
                        self._rule6,  self._rule7,  self._rule8,  self._rule9,  self._rule10, self._rule11,
                        self._rule12, self._rule13, self._rule14, self._rule15, self._rule16, self._rule17,
                        self._rule18, self._rule19, self._rule20, self._rule21, self._rule22, self._rule23,
                        self._rule24, self._rule25, self._rule26, self._rule27, self._rule28, self._rule29,
                        self._rule30, self._rule31, self._rule32, self._rule33, self._rule34, self._rule35 ]

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
        print 'Iterating through review json data'
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
                    valence_score = self._get_valence_score(word)
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
            print 'Percent of words found in valence dataset', word_with_valence_count / float(review_words_count) * 100

            # Append the max_valence map data to the output array
            self.output_pos_max_valence.append(pos_tag_max_valence)

        print 'Iterating through non-valence data'
        for word, count in self.unique_non_valence_words.items():
            try:
                self.output_non_valence.write(word + '=' + str(count) + '\n')
            except UnicodeEncodeError:
                print 'Encoding error - proceeding with next word'

        print 'Inferencing'
        # Iterate through the max_valence data and get inferencing!
        for review in self.output_pos_max_valence:
            inputs = dict()
            for pos_tag, tup in review.items():
                valence, _ = tup
                inputs[self._postag_to_name(pos_tag)] = valence
            output = self.review_inferencer.infer(**inputs)
            #print 'Output is ', output(5)
            defuzzifier = Defuzzifier()
            outputvalue = defuzzifier(output, 0.0, 5.0, 1e-1);
            print 'Defuzzified Value is', format(outputvalue, '.1f')

    # Valence scores from the data source lie between
    # [-5, 5]. It returns the score based on the
    # map generated by the ValenceData object.
    def _get_valence_score(self, word):
        if word in self.valence_data._data_map:
            return self.valence_data._data_map[word]
        return DOES_NOT_EXIST

    def _postag_to_name(self, postag):
        if postag == 'JJ': return 'adjective'
        if postag == 'VB': return 'verb'
        if postag == 'NN': return 'noun'
        if postag == 'RB': return 'adverb'

    def _clear_rules(self):
        for rule in self._rules: rule.clear()

############### MAIN ###############
if __name__ == '__main__':
    rv = ReviewValence()
    rv.process_reviews(int(50))
