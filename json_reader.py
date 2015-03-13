#!/usr/bin/python
import json

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
    self.i_file_object = open(self.inputFile)

  def openOutputFile(self):
    self.o_file_object = open(self.outputFile)

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
        print line
      else:
        break
      counter += 1
 
# Review Json Reader inherits the 
# functionality of a Json Reader
# but may add additional methods 
# for custom processing of a review 
# json object        
class ReviewJsonReader(JsonReader):
  def __init__(self, inputFile, outputFile):
    self.inputFile = inputFile
    self.outputFile = outputFile
    JsonReader.__init__(self, inputFile, outputFile)

# Perhaps, use a similar pattern for other files 
# class UserJsonReader(JsonReader):
#


# TODO: Satyam - Should not hardcode the inputs here
# Gather from command line
reviewJsonReader = ReviewJsonReader(
                 './data/yelp_academic_dataset_review.json',
                 './output/yelp_review_output.txt')

################ Tests #################
reviewJsonReader.openInputFile()
reviewJsonReader.readInputFile()

# Should return the first four json records
reviewJsonReader.iterateInputFile(2)
reviewJsonReader.iterateInputFile()
reviewJsonReader.iterateInputFile()

reviewJsonReader.closeInputFile()
########################################