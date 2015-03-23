#!/usr/bin/python
from statanalysis import StatAnalysis
from jsonreader import ReviewJsonReader as ReviewJsonReader
from valencedata import ValenceData as ValenceData
from generalmembershipfunctions import \
    InputMembershipFunction, OutputMembershipFunction
import json
from collections import OrderedDict
from inferencer import Rule, Inferencer
from defuzzifier import Defuzzifier as Defuzzifier
from math import exp
from collections import OrderedDict, defaultdict
from defuzzifier import Defuzzifier
import abc
import getopt, sys

_DEBUG = 0

# constant that denotes that
# a word is not found in the
# valence data set
DOES_NOT_EXIST = 10

# a constant that denotes that
# a 'pos' tag did not have
# a word with a 'max' valence
INIT_MAX_VALENCE = 0

# This abstract class acts as a wrapper around the
# ReviewJsonReader and the ValenceData. Base class for writing
# classification method classes to score words based on the
# valence data set.
class ReviewClassificationMethod(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.review_json = ReviewJsonReader(
                 '../data/yelp_academic_dataset_review.json',
                 '../output/yelp_review_output.json')
        self.review_json.open_input_file()
        self.review_json.read_input_file()
        self.valencedata = ValenceData('../data/valence.txt')
        self.valencedata.process_data()
        self.input_mem_functions = InputMembershipFunction()
        self.output_mem_functions = OutputMembershipFunction()
        self.unique_non_valence_words = defaultdict(int)
        self.output_non_valence = open('../data/output_non_valence.txt', 'w+')
        self.defuzzied_review_ratings = []
        self._build_inferencer()


    def _build_inferencer(self):
        low_positive  = self.input_mem_functions.get_low_positive_membership
        med_positive  = self.input_mem_functions.get_moderate_positive_membership
        high_positive = self.input_mem_functions.get_high_positive_membership

        low_negative  = self.input_mem_functions.get_low_negative_membership
        med_negative  = self.input_mem_functions.get_moderate_negative_membership
        high_negative = self.input_mem_functions.get_high_negative_membership

        low_otn  = self.output_mem_functions.get_low_rating
        high_otn = self.output_mem_functions.get_high_rating
        very_low_otn  = self.output_mem_functions.get_very_low_rating
        moderate_otn  = self.output_mem_functions.get_moderate_rating
        very_high_otn = self.output_mem_functions.get_very_high_rating
        very_moderate_otn = self.output_mem_functions.get_very_moderate_rating

        # Only verbs
        self._rule0 = Rule('IF verb is low_positive THEN orientation is moderate_otn')
        self._rule0.if_('verb', low_positive).then('orientation', moderate_otn)

        self._rule1 = Rule('IF verb is med_positive THEN orientation is high_otn')
        self._rule1.if_('verb', med_positive).then('orientation', very_moderate_otn)

        self._rule2 = Rule('IF verb is high_positive THEN orientation is very_high_otn')
        self._rule2.if_('verb', high_positive).then('orientation', high_otn)

        self._rule3 = Rule('IF verb is low_negative THEN orientation is moderate_otn')
        self._rule3.if_('verb', low_negative).then('orientation', moderate_otn)

        self._rule4 = Rule('IF verb is med_negative THEN orientation is low_otn')
        self._rule4.if_('verb', med_negative).then('orientation', low_otn)

        self._rule5 = Rule('IF verb is high_negative THEN orientation is very_low_otn')
        self._rule5.if_('verb', high_negative).then('orientation', very_low_otn)

        # Only adjectives
        self._rule6 = Rule('IF adjective is low_positive THEN orientation is moderate_otn')
        self._rule6.if_('adjective', low_positive).then('orientation', moderate_otn)

        self._rule7 = Rule('IF adjective is med_positive THEN orientation is high_otn')
        self._rule7.if_('adjective', med_positive).then('orientation', very_moderate_otn)

        self._rule8 = Rule('IF adjective is high_positive THEN orientation is very_high_otn')
        self._rule8.if_('adjective', high_positive).then('orientation', high_otn)

        self._rule9 = Rule('IF adjective is low_negative THEN orientation is moderate_otn')
        self._rule9.if_('adjective', low_negative).then('orientation', moderate_otn)

        self._rule10 = Rule('IF adjective is med_negative THEN orientation is low_otn')
        self._rule10.if_('adjective', med_negative).then('orientation', low_otn)

        self._rule11 = Rule('IF adjective is high_negative THEN orientation is very_low_otn')
        self._rule11.if_('adjective', high_negative).then('orientation', very_low_otn)

        # Only adverbs
        self._rule12 = Rule('IF adverb is low_positive THEN orientation is moderate_otn')
        self._rule12.if_('adverb', low_positive).then('orientation', moderate_otn)

        self._rule13 = Rule('IF adverb is med_positive THEN orientation is high_otn')
        self._rule13.if_('adverb', med_positive).then('orientation', very_moderate_otn)

        self._rule14 = Rule('IF adverb is high_positive THEN orientation is very_high_otn')
        self._rule14.if_('adverb', high_positive).then('orientation', high_otn)

        self._rule15 = Rule('IF adverb is low_negative THEN orientation is moderate_otn')
        self._rule15.if_('adverb', low_negative).then('orientation', moderate_otn)

        self._rule16 = Rule('IF adverb is med_negative THEN orientation is low_otn')
        self._rule16.if_('adverb', med_negative).then('orientation', low_otn)

        self._rule17 = Rule('IF adverb is high_negative THEN orientation is very_low_otn')
        self._rule17.if_('adverb', high_negative).then('orientation', very_low_otn)

        # Only nouns
        self._rule18 = Rule('IF noun is low_positive THEN orientation is moderate_otn')
        self._rule18.if_('noun', low_positive).then('orientation', moderate_otn)

        self._rule19 = Rule('IF noun is med_positive THEN orientation is high_otn')
        self._rule19.if_('noun', med_positive).then('orientation', very_moderate_otn)

        self._rule20 = Rule('IF noun is high_positive THEN orientation is very_high_otn')
        self._rule20.if_('noun', high_positive).then('orientation', very_high_otn)

        self._rule21 = Rule('IF noun is low_negative THEN orientation is moderate_otn')
        self._rule21.if_('noun', low_negative).then('orientation', moderate_otn)

        self._rule22 = Rule('IF noun is med_negative THEN orientation is low_otn')
        self._rule22.if_('noun', med_negative).then('orientation', low_otn)

        self._rule23 = Rule('IF noun is high_negative THEN orientation is very_low_otn')
        self._rule23.if_('noun', high_negative).then('orientation', very_low_otn)

        # Here f2 may be a function such that f2 = sqrt(f1)
        # This is because two POS TAGs are being fired in conjunction -> so the consequent membership
        # function may be made less fuzzy?
        # Verbs and adverbs
        self._rule24 = Rule('IF verb is low_positive AND adverb is low_positive THEN orientation is moderate_otn')
        self._rule24.if_('verb', low_positive).and_('adverb', low_positive).then('orientation', moderate_otn)

        self._rule25 = Rule('IF verb is med_positive AND adverb is med_positive THEN orientation is high_otn')
        self._rule25.if_('verb', med_positive).and_('adverb', med_positive).then('orientation', high_otn)

        self._rule26 = Rule('IF verb is high_positive AND adverb is high_positive THEN orientation is very_high_otn')
        self._rule26.if_('verb', high_positive).and_('adverb', high_positive).then('orientation', very_high_otn)

        self._rule27 = Rule('IF verb is low_negative AND adverb is low_negative THEN orientation is moderate_otn')
        self._rule27.if_('verb', low_negative).and_('adverb', low_negative).then('orientation', moderate_otn)

        self._rule28 = Rule('IF verb is med_negative AND adverb is med_negative THEN orientation is low_otn')
        self._rule28.if_('verb', med_negative).and_('adverb', med_negative).then('orientation', low_otn)

        self._rule29 = Rule('IF verb is high_negative AND adverb is high_negative THEN orientation is very_low_otn')
        self._rule29.if_('verb', high_negative).and_('adverb', high_negative).then('orientation', very_low_otn)

        # Nouns and adjectives
        self._rule30 = Rule('IF noun is low_positive AND adjective is low_positive THEN orientation is moderate_otn')
        self._rule30.if_('noun', low_positive).and_('adjective', low_positive).then('orientation', moderate_otn)

        self._rule31 = Rule('IF noun is med_positive AND adjective is med_positive THEN orientation is high_otn')
        self._rule31.if_('noun', med_positive).and_('adjective', med_positive).then('orientation', high_otn)

        self._rule32 = Rule('IF noun is high_positive AND adjective is high_positive THEN orientation is very_high_otn')
        self._rule32.if_('noun', high_positive).and_('adjective', high_positive).then('orientation', very_high_otn)

        self._rule33 = Rule('IF noun is low_negative AND adjective is low_negative THEN orientation is moderate_otn')
        self._rule33.if_('noun', low_negative).and_('adjective', low_negative).then('orientation', moderate_otn)

        self._rule34 = Rule('IF noun is med_negative AND adjective is med_negative THEN orientation is low_otn')
        self._rule34.if_('noun', med_negative).and_('adjective', med_negative).then('orientation', low_otn)

        self._rule35 = Rule('IF noun is high_negative AND adjective is high_negative THEN orientation is very_low_otn')
        self._rule35.if_('noun', high_negative).and_('adjective', high_negative).then('orientation', very_low_otn)

        # Nouns and Verbs
        # Handles positive/negative sentiment
        self._rule36 = Rule('IF noun is low_positive AND verb is low_negative THEN orientation is moderate_otn')
        self._rule36.if_('noun', low_positive).and_('adjective', med_positive).then('orientation', moderate_otn)

        self._rule37 = Rule('IF noun is med_positive AND verb is med_negative THEN orientation is moderate_otn')
        self._rule37.if_('noun', med_positive).and_('verb', high_positive).then('orientation', moderate_otn)

        self._rule38 = Rule('IF noun is high_positive AND verb is high_negative THEN orientation is moderate_otn')
        self._rule38.if_('noun', high_positive).and_('verb', high_positive).then('orientation', moderate_otn)

        # Adjectives and adverbs
        self._rule39 = Rule('IF adjective is low_positive AND adverb is low_negative THEN orientation is moderate_otn')
        self._rule39.if_('adjective', low_positive).and_('adverb', low_negative).then('orientation', moderate_otn)

        self._rule40 = Rule('IF adjective is med_positive AND adverb is med_negative THEN orientation is moderate_otn')
        self._rule40.if_('adjective', med_positive).and_('adverb', med_negative).then('orientation', moderate_otn)

        self._rule41 = Rule('IF adjective is high_positive AND adverb is high_negative THEN orientation is moderate_otn')
        self._rule41.if_('adjective', high_positive).and_('adverb', high_negative).then('orientation', moderate_otn) 

        # Adverbs and Adjectives
        self._rule42 = Rule('IF adverb is low_positive AND adjective is low_negative THEN orientation is moderate_otn')
        self._rule42.if_('adverb', low_positive).and_('adjective', low_negative).then('orientation', moderate_otn)

        self._rule43 = Rule('IF adverb is med_positive AND adjective is med_negative THEN orientation is moderate_otn')
        self._rule43.if_('adverb', med_positive).and_('adjective', med_negative).then('orientation', moderate_otn)

        self._rule44 = Rule('IF adverb is high_positive AND adjective is high_negative THEN orientation is moderate_otn')
        self._rule44.if_('adverb', high_positive).and_('adjective', high_negative).then('orientation', moderate_otn) 

        # Nouns and Verbs
        self._rule45 = Rule('IF noun is low_negative AND verb is low_positive THEN orientation is moderate_otn')
        self._rule45.if_('noun', low_negative).and_('verb', low_positive).then('orientation', moderate_otn)

        self._rule46 = Rule('IF noun is med_negative AND verb is med_positive THEN orientation is moderate_otn')
        self._rule46.if_('noun', med_negative).and_('verb', med_negative).then('orientation', moderate_otn)

        self._rule47 = Rule('IF noun is high_negative AND verb is high_positive THEN orientation is moderate_otn')
        self._rule47.if_('noun', high_negative).and_('verb', high_positive).then('orientation', moderate_otn)  

        # High with Lows
        # Adverbs/Adjectives
        self._rule48 = Rule('IF adverb is high_positive AND adjective is low_positive THEN orientation is very_moderate_otn')
        self._rule48.if_('adverb', high_positive).and_('adjective', low_positive).then('orientation', very_moderate_otn)

        self._rule49 = Rule('IF adverb is high_positive AND adjective is med_positive THEN orientation is high_otn')
        self._rule49.if_('adverb', high_positive).and_('adjective', med_negative).then('orientation', high_otn)

        self._rule50 = Rule('IF adverb is high_positive AND adjective is high_positive THEN orientation is very_high_otn')
        self._rule50.if_('adverb', high_positive).and_('adjective', high_positive).then('orientation', very_high_otn)  

        #Nouns/Verbs
        self._rule51 = Rule('IF noun is high_positive AND verb is low_positive THEN orientation is very_moderate_otn')
        self._rule51.if_('noun', high_positive).and_('verb', low_positive).then('orientation', high_otn)

        self._rule52 = Rule('IF noun is high_positive AND verb is med_positive THEN orientation is high_otn')
        self._rule52.if_('noun', high_positive).and_('verb', med_negative).then('orientation', moderate_otn)

        self._rule53 = Rule('IF noun is high_positive AND verb is high_positive THEN orientation is very_high_otn')
        self._rule53.if_('noun', high_positive).and_('verb', high_positive).then('orientation', very_high_otn)                

        # Recency based rules


        self._rules = [ self._rule0,  self._rule1,  self._rule2,  self._rule3,  self._rule4,  self._rule5,
                        self._rule6,  self._rule7,  self._rule8,  self._rule9,  self._rule10, self._rule11,
                        self._rule12, self._rule13, self._rule14, self._rule15, self._rule16, self._rule17,
                        self._rule18, self._rule19, self._rule20, self._rule21, self._rule22, self._rule23,
                        self._rule24, self._rule25, self._rule26, self._rule27, self._rule28, self._rule29,
                        self._rule30, self._rule31, self._rule32, self._rule33, self._rule34, self._rule35,
                        self._rule36, self._rule37, self._rule38, self._rule39, self._rule40, self._rule41,
                        self._rule42, self._rule43, self._rule44, self._rule45, self._rule46, self._rule47,
                        self._rule48, self._rule49, self._rule50, self._rule51, self._rule52, self._rule53 ]

        self.review_inferencer = Inferencer(*self._rules)

    # Valence scores from the data source lie between
    # [-5, 5]. It returns the score based on the
    # map generated by the ValenceData object.
    def _get_valence_score(self, word):
        if word in self.valencedata._data_map:
            return self.valencedata._data_map[word]
        return DOES_NOT_EXIST

    def _postag_to_name(self, postag):
        if postag == 'JJ': return 'adjective'
        if postag == 'VB': return 'verb'
        if postag == 'NN': return 'noun'
        if postag == 'RB': return 'adverb'

    @abc.abstractmethod
    def process_reviews(self, N):
        """Retrieves and scores N reviews from the dataset"""
        return

# Scores reviews based on the max valance of
# each POS.
class MaxPOSValenceMethod(ReviewClassificationMethod):

    def __init__(self):
        ReviewClassificationMethod.__init__(self)

        # An array of review elements. Each review element contains
        # a map with a key for each 'POS tag' and its corresponding
        # value to be the 'max' valence.
        # The 'max' valence is simply the maximum of the valences of
        # the words for each 'POS tag'.
        self.output_pos_max_valence = []

    # Iterates through the first 'num_reviews'
    # For each review it looks up the valence
    # score for each word across all POS tags.
    def process_reviews(self, num_reviews):
        counter = 0
        # Should return the first num_reviews records
        for i in range(num_reviews):
            if counter % 100 == 0:
                print '.',
            counter += 1    
            self.review_json.process_record()

        # review_output is a map with the key being a POS Tag
        # and the value an array of words falling into that
        # POS Tag category.
        print '\nIterating through review json data'
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
                        self.unique_non_valence_words[word] += 1
            #print 'Percent of words found in valence dataset', word_with_valence_count / float(review_words_count) * 100

            # Append the max_valence map data to the output array
            self.output_pos_max_valence.append(pos_tag_max_valence)

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
            outputvalue = defuzzifier(output, 0.0, 5.0, 1e-1)
            self.defuzzied_review_ratings.append(round(outputvalue, 1))

            if _DEBUG:
                print 'Defuzzified Value is', format(outputvalue, '.1f')

        StatAnalysis.get_review_rating_accuracy(self.review_json.review_star_rating, self.defuzzied_review_ratings)
        StatAnalysis.get_review_rating_stats(self.defuzzied_review_ratings)
    # Valence scores from the data source lie between
    # [-5, 5]. It returns the score based on the
    # map generated by the ValenceData object.
    def _get_valence_score(self, word):
        if word in self.valencedata._data_map:
            return self.valencedata._data_map[word]
        return DOES_NOT_EXIST

# Scores reviews based on the average valance of
# each POS.
class AveragePOSValenceMethod(ReviewClassificationMethod):

    def __init__(self):
        ReviewClassificationMethod.__init__(self)

        # An array of review elements. Each review element contains
        # a map with a key for each 'POS tag' and its corresponding
        # value to be the 'average' valence.
        # The 'average' valence is simply the average of the valences of
        # the words for each 'POS tag'.
        self._output_pos_average_valences = []

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
            pos_tag_average_valence = dict()
            for pos_tag, words in review_output.items():
                if not words: continue
                cummulative_valence = sum(map(self._get_valence_score, words))
                postage_name = self._postag_to_name(pos_tag)
                pos_tag_average_valence[postage_name] = cummulative_valence / len(words)
            #print pos_tag_average_valence
            self._output_pos_average_valences.append(pos_tag_average_valence)

        print 'Inferencing'
        # Iterate through the average valence data and get inferencing!
        for review in self._output_pos_average_valences:
            output = self.review_inferencer.infer(**review)
            defuzzifier = Defuzzifier()
            outputvalue = defuzzifier(output, 0.0, 5.0, 1e-1);
            self.defuzzied_review_ratings.append(round(outputvalue, 1))
            if _DEBUG:
                print 'Defuzzified Value is', format(outputvalue, '.1f')

        StatAnalysis.get_review_rating_accuracy(self.review_json.review_star_rating, self.defuzzied_review_ratings)
        StatAnalysis.get_review_rating_stats(self.defuzzied_review_ratings)

    def _get_valence_score(self, word):
        if word in self.valencedata._data_map:
            return int(self.valencedata._data_map[word])

        if word not in self.unique_non_valence_words:
            self.unique_non_valence_words[word] += 1
        return 0

############### MAIN ###############
if __name__ == '__main__':
    if len(sys.argv[1:]) < 1:
        print 'reviewvalence.py -n <numreviews>'
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hn:",["numreviews="])
    except getopt.GetoptError:
        print 'reviewvalence.py -n <numreviews>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'reviewvalence.py -n <numreviews>'
            sys.exit()
        elif opt in ("-n", "--numreviews"):
            numreviews = arg
    print 'Number of Reviews ', numreviews
    print 'Running Max Valence method'
    max_pos_method = MaxPOSValenceMethod()
    max_pos_method.process_reviews(int(numreviews))

    print '\n\nRunning Average Valence'
    average_pos_method = AveragePOSValenceMethod()
    average_pos_method.process_reviews(int(numreviews))
