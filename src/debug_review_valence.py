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
		self.input_mem_functions = general_membership_functions.InputMembershipFunctions()
		self.output_mem_functions = general_membership_functions.OutputMembershipFunctions()
		self.unique_non_valence_words = {}
		self.output_non_valence = open('./data/output_non_valence.txt', 'w+')
		# An array of review elements. Each review element contains
		# a map with a key for each 'POS tag' and its corresponding 
		# value to be the 'max' valence.
		# The 'max' valence is simply the maximum of the valences of
		# the words for each 'POS tag'. 
		self.output_pos_max_valence = []

		self.init_rules()

		self.input_dict_inferencer = {}

	def init_rules(self):
		self._rule1 = inferencer.Rule('IF verb is low_pos AND adjective is low_pos THEN orientation is f1')
		self._rule2 = inferencer.Rule('IF verb is med_pos AND adjective is med_pos THEN orientation is f1')
		self._rule3 = inferencer.Rule('IF verb is high_pos AND adjective is high_pos THEN orientation is f1')
		self._rule4 = inferencer.Rule('IF verb is low_neg AND adjective is low_neg THEN orientation is f1')
		self._rule5 = inferencer.Rule('IF verb is med_neg AND adjective is med_neg THEN orientation is f1')
		self._rule6 = inferencer.Rule('IF verb is high_neg AND adjective is high_neg THEN orientation is f1')
		self._rule7 = inferencer.Rule('IF verb is low_pos AND noun is low_pos THEN orientation is f1')
		self._rule8 = inferencer.Rule('IF verb is med_pos AND noun is med_pos THEN orientation is f1')
		self._rule9 = inferencer.Rule('IF verb is high_pos AND noun is high_pos THEN orientation is f1')
		self._rule10 = inferencer.Rule('IF verb is low_neg AND noun is low_neg THEN orientation is f1')
		self._rule11 = inferencer.Rule('IF verb is med_neg AND noun is med_neg THEN orientation is f1')
		self._rule12 = inferencer.Rule('IF verb is high_neg AND noun is high_neg THEN orientation is f1')


		self.review_inferencer = inferencer.Inferencer(self._rule1, self._rule2, self._rule3, self._rule4, 
																									 self._rule5, self._rule6, self._rule7, self._rule8,
																									 self._rule9, self._rule10, self._rule11, self._rule12)

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
						#print abs_valence_score
						if abs_valence_score > max_valence:
							max_valence = abs_valence_score
							pos_tag_max_valence[pos_tag] = (int(valence_score), word)
							#print pos_tag_max_valence
						word_with_valence_count += 1
					else:
						if word not in self.unique_non_valence_words:
							self.unique_non_valence_words[word] = 1
						else:
							self.unique_non_valence_words[word] += 1
			print "Percent of words found in valence dataset ", word_with_valence_count / float(review_words_count)	* 100

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
				#print pos_tag
				self.map_inputs_membership_function(pos_tag, tup[0], tup[1])
				self.map_outputs_membership_function()
			output = self.review_inferencer.infer(**(self.input_dict_inferencer))
			
			print "Final output", output(5)
			self.clear_rules()
			#print "pos_tag=", pos_tag, " max_valence=", max_valence

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
			#print "Adj"
			self.input_dict_inferencer['adjective'] = word
			self._rule1.and_('adjective', valence_lp_lambda)
			self._rule2.and_('adjective', valence_mp_lambda)
			self._rule3.and_('adjective', valence_hp_lambda)
			self._rule4.and_('adjective', valence_ln_lambda)
			self._rule5.and_('adjective', valence_mn_lambda)
			self._rule6.and_('adjective', valence_hn_lambda)
			#self._rule2.and_('adjective', valence_lambda)
		elif pos_tag == 'VB':
			#print "Verb"
			self.input_dict_inferencer['verb'] = word
			self._rule1.if_('verb', valence_lp_lambda)
			self._rule2.if_('verb', valence_mp_lambda)
			self._rule3.if_('verb', valence_hp_lambda)
			self._rule4.if_('verb', valence_ln_lambda)
			self._rule5.if_('verb', valence_mn_lambda)
			self._rule6.if_('verb', valence_hn_lambda)

			self._rule7.if_('verb', valence_lp_lambda)
			self._rule8.if_('verb', valence_mp_lambda)
			self._rule9.if_('verb', valence_hp_lambda)
			self._rule10.if_('verb', valence_ln_lambda)
			self._rule11.if_('verb', valence_mn_lambda)
			self._rule12.if_('verb', valence_hn_lambda)
		elif pos_tag == 'NN':
			#print "Noun"
			self.input_dict_inferencer['noun'] = word

			self._rule7.and_('noun', valence_lp_lambda)
			self._rule8.and_('noun', valence_mp_lambda)
			self._rule9.and_('noun', valence_hp_lambda)
			self._rule10.and_('noun', valence_ln_lambda)
			self._rule11.and_('noun', valence_mn_lambda)
			self._rule12.and_('noun', valence_hn_lambda)
		elif pos_tag == 'RB':
			#print "Adverb"

			self.input_dict_inferencer['adverb'] = word 

	def map_outputs_membership_function(self):
		#output_lambda = lambda word : self.output_mem_functions.get_low_rating(2)
		output_lambda = lambda x : x
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

	def clear_rules(self):
		self._rule1.clear()
		self._rule2.clear()
		self._rule3.clear()
		self._rule4.clear()
		self._rule5.clear()
		self._rule6.clear()
		self._rule7.clear()
		self._rule8.clear()
		self._rule9.clear()
		self._rule10.clear()
		self._rule11.clear()
		self._rule12.clear()

############### MAIN ###############
rv = ReviewValence()
rv.process_reviews(int(25))
