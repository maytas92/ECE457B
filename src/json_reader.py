#!/usr/bin/python
import json
import re
from nltk import pos_tag, word_tokenize
from collections import OrderedDict

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
  def openInputFile(self):
    self.i_file_object = open(self.inputFile, 'r')

  def openOutputFile(self):
    self.o_file_object = open(self.outputFile, 'w+')

  # Finally close the inputFile after done 
  # reading/processing.
  def closeInputFile(self):
    self.i_file_object.close()
   
  def closeOutputFile(self):
    self.o_file_object.close()

  # Returns generator objects 
  # Ensure that the object calls openInputFile()
  # This is useful for large files because it prevents
  # loading the entire json file
  # into memory at once.
  def readInputFile(self):
    for line in self.i_file_object:
      yield json.loads(line)

  # Returns the next 'numLines' of json records
  # from the json file being read.
  # Ensure that the object calls readInputFile()
  # first.
  def iterateInputFile(self, numLines=1):
    if numLines < 1:
      return

    counter = 0
    for line in self.readInputFile():
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

  def __init__(self, inputFile, outputFile):
    self.inputFile = inputFile
    self.outputFile = outputFile
    self.posTagReviewOutput = []
    self.reviewStarRating = []
    JsonReader.__init__(self, inputFile, outputFile)

  def processRecord(self, numRecords=1):
    record = JsonReader.iterateInputFile(self, numRecords)

    reviewBusinessId = record['business_id']
    reviewText = record['text']
    reviewStars = record['stars']

    # NLTK Tokenization and Tagging
    tokenizedReviewText = word_tokenize(reviewText)
    posTagReview = pos_tag(tokenizedReviewText)

    # {"somePOSTag" ->  ['someWord1', 'someWord2' ..], 
    #  "somePOSTag2" -> ['someOtherWord2, 'someOtherWord2']
    #   ..
    #  "somePOSTagn" -> [ .. ]"}
    # Ensure that keys are ordered based on POSTAGS
    posTagReviewMap = OrderedDict()

    for pt in self.POSTAGS:
      posTagReviewMap[pt] = []
    
    # posTagReview is a list
    # Each list item is a tuple of two items
    # (u'someWord', 'somePOSTag')
    for item in posTagReview:
      token = item[0]
      posTag = item[1]
      for idx, ele in enumerate(self.POSTAGS_REGEX):
        if re.match(ele, posTag):
          posTagReviewMap[self.POSTAGS[idx]].append(token)
          break

    # Adding necessary attributes to the output arrays
    # These are written back to the output file
    self.posTagReviewOutput.append(posTagReviewMap)
    self.reviewStarRating.append(reviewStars)

    print posTagReviewMap

  def writeToOutputFile(self):
    # The object written is a nested array
    # Each element of the nested array comprises of two 
    # elements. The first is an 'Ordered Dict' with 
    # four keys 'JJ', 'RB', 'VB' and 'NN'.
    # The second element is the review star rating.
    self.o_file_object.write(json.dumps(
                            zip(self.posTagReviewOutput,
                                self.reviewStarRating)
                            ))

# Perhaps, use a similar pattern for other files 
# class UserJsonReader(JsonReader):
#


# TODO: Satyam - Should not hardcode the inputs here
# Gather from command line
NUM_RECORDS = 10
reviewJsonReader = ReviewJsonReader(
                 './data/yelp_academic_dataset_review.json',
                 './output/yelp_review_output.json')

################ Tests #################
reviewJsonReader.openInputFile()
reviewJsonReader.readInputFile()

# Should return the first ten json records
for i in range(NUM_RECORDS):
  reviewJsonReader.processRecord()

reviewJsonReader.closeInputFile()

##### DONE WITH INPUT FILE ######

###### START OUTPUT FILE ########
reviewJsonReader.openOutputFile()
reviewJsonReader.writeToOutputFile()

########################################