#!/usr/bin/python
import json
import re
from nltk import pos_tag, word_tokenize
from collections import OrderedDict

_DEBUG = 0

# Class that provides basic functionality
# to open, close, read and iterate
# through json files [1 input, 1 output].
# For e.g. the user.json file may be opened,
# read and then written to an output file.
# This output file may contain any useful 
# processed output for later stages of the ANN.
class JsonReader:

  def __init__(self, inputFile, outputFile):
    self.inputFile = inputFile
    self.outputFile = outputFile

  # First must open the inputFile
  def open_input_file(self):
    self.i_file_object = open(self.inputFile, 'r')

  def open_output_file(self):
    self.o_file_object = open(self.outputFile, 'w+')

  # Finally close the inputFile after done 
  # reading/processing.
  def close_input_file(self):
    self.i_file_object.close()
   
  def close_output_file(self):
    self.o_file_object.close()

  # Returns generator objects 
  # Ensure that the object calls openInputFile()
  # This is useful for large files because it prevents
  # loading the entire json file
  # into memory at once.
  def read_input_file(self):
    for line in self.i_file_object:
      yield json.loads(line)

  # Returns the next 'numLines' of json records
  # from the json file being read.
  # Ensure that the object calls readInputFile()
  # first.
  def iterate_input_file(self, numLines=1):
    if numLines < 1:
      return

    counter = 0
    for line in self.read_input_file():
      if counter < numLines:
        return line
      else:
        break
      counter += 1
 
# Review Json Reader inherits the 
# functionality of a Json Reader
# but may add additional methods 
# for custom processing of a review 
# json object        
class ReviewJsonReader(JsonReader):

  # Adjectives, Adverbs, verbs, Nouns
  POSTAGS_REGEX = ['JJ.*', 'RB.*', 'VB.*', 'NN.*']
  POSTAGS = ['JJ', 'RB', 'VB', 'NN']

  def __init__(self, input_file, output_file):
    self.input_file = input_file
    self.output_file = output_file
    self.pos_tag_review_output = []
    self.review_star_rating = []
    JsonReader.__init__(self, input_file, output_file)

  def process_record(self, num_records=1):
    record = JsonReader.iterate_input_file(self, num_records)

    review_business_id = record['business_id']
    review_text = record['text']
    review_stars = record['stars']

    # NLTK Tokenization and Tagging
    tokenized_review_text = word_tokenize(review_text)
    pos_tag_review = pos_tag(tokenized_review_text)

    # {"somePOSTag" ->  ['someWord1', 'someWord2' ..], 
    #  "somePOSTag2" -> ['someOtherWord2, 'someOtherWord2']
    #   ..
    #  "somePOSTagn" -> [ .. ]"}
    # Ensure that keys are ordered based on POSTAGS
    pos_tag_review_map = OrderedDict()

    for pt in self.POSTAGS:
      pos_tag_review_map[pt] = []
    
    # posTagReview is a list
    # Each list item is a tuple of two items
    # (u'someWord', 'somePOSTag')
    for item in pos_tag_review:
      token = item[0]
      posTag = item[1]
      for idx, ele in enumerate(self.POSTAGS_REGEX):
        if re.match(ele, posTag):
          pos_tag_review_map[self.POSTAGS[idx]].append(token)
          break

    # Adding necessary attributes to the output arrays
    # These are written back to the output file
    self.pos_tag_review_output.append(pos_tag_review_map)
    self.review_star_rating.append(review_stars)

    #print pos_tag_review_map

  def write_to_output_file(self):
    # The object written is a nested array
    # Each element of the nested array comprises of two 
    # elements. The first is an 'Ordered Dict' with 
    # four keys 'JJ', 'RB', 'VB' and 'NN'.
    # The second element is the review star rating.
    self.o_file_object.write(json.dumps(
                            zip(self.pos_tag_review_output,
                                self.review_star_rating)
                            ))

# Perhaps, use a similar pattern for other files 
# class UserJsonReader(JsonReader):
#


# TODO: Satyam - Should not hardcode the inputs here
# Gather from command line
if _DEBUG:
  NUM_RECORDS = 100
  review_json_reader = ReviewJsonReader(
                   './data/yelp_academic_dataset_review.json',
                   './output/yelp_review_output.json')

  ################ Tests #################
  review_json_reader.open_input_file()
  review_json_reader.read_input_file()

  # Should return the first ten json records
  for i in range(NUM_RECORDS):
    review_json_reader.process_record()

  review_json_reader.close_input_file()

  ##### DONE WITH INPUT FILE ######

  ###### START OUTPUT FILE ########
  review_json_reader.open_output_file()
  review_json_reader.write_to_output_file()
  review_json_reader.close_output_file()

########################################