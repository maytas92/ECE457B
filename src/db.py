#!/usr/bin/python
import json
import re
from nltk import pos_tag, word_tokenize
from collections import OrderedDict
from peewee import *

_DEBUG = 0

db = SqliteDatabase('../data/yelp_dataset2.db')
class Business(Model):
    business_id = CharField(primary_key=True)
    stars = FloatField()
    review_count = IntegerField()
    business_name = TextField()
    class Meta:
        database = db

class User(Model):
    user_id = CharField(primary_key=True)
    name = CharField()
    review_count = IntegerField()
    average_stars = FloatField()
    class Meta:
        database = db

class Review(Model):    
    business_id = ForeignKeyField(Business, related_name="reviews" )
    user_id = ForeignKeyField(User,related_name="review")
    stars = FloatField()
    text = TextField()
    date = CharField()
    #parsed_text = BlobField()
    
    class Meta:
        database = db
        primary_key = CompositeKey( 'business_id' , 'user_id', 'date' )


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
    list_ = []
    for line in self.read_input_file():
      if counter < numLines:
        list_.append( line )
      else:
        break
      counter += 1
    return list_

class DbReader:
    # Adjectives, Adverbs, verbs, Nouns
    POSTAGS_REGEX = ['JJ.*', 'RB.*', 'VB.*', 'NN.*']
    POSTAGS = ['JJ', 'RB', 'VB', 'NN']
    def __init__(self):
        pass

    def parseReviewData(self,q, reviewList):
        review_business_id = q.business_id
        review_text = q.text
        review_stars = q.stars
        review_date = q.date
        review_user = q.user_id
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
                        
        # Adding necessary attributes to the output map
        # These are written back to the output file
        reviewList.append({ \
                                 'business_id':review_business_id,
                                 'user_id':review_user,
                                 'stars':review_stars,
                                 'date':review_date,
                                 'tagged_text':pos_tag_review_map
                                 })
        
    def getBusinessReviews(self,business_id,num_reviews=1):
        business = Business.get(Business.business_id==business_id)
        reviewList = []
        with db.transaction():
            query = (Review
                          .select()
                          .where(Review.business_id==business)
                          .limit(num_reviews)
            )
            #reviewList = [q for q in query]
            for q in query:
                self.parseReviewData( q, reviewList )
        return reviewList

    def getUserReviews(self,user_id,num_reviews=1):
        user = User.get(User.user_id==user_id)
        reviewList = []
        with db.transaction():
            query = (Review
                          .select()
                          .where(Review.user_id==user)
                          .limit(num_reviews))
            #reviewList = [q for q in query]
            for q in query:
                self.parseReviewData( q , reviewList )
                
        return reviewList

    def parseBusinessData( self, q, reviewList ):
        business_id = q.business_id
        stars = q.stars
        business_name = q.business_name
        review_count = q.review_count
        reviewList.append({ \
                            'business_id':business_id,
                            'stars':stars,
                            'business_name':business_name,
                            'review_count':review_count
                        })
        
    def getBusinesses(self,num_businesses):
        reviewList = []
        with db.transaction():
            query = (Business
                     .select(Business.business_id,Business.business_name,Business.stars, fn.Count(Business.business_id).alias('review_count'))
                     .join(Review)
                     .group_by(Business)
                     .limit(num_businesses)
                     )
            # query = (Business
            #          .select()
            #          .limit(num_businesses)
            #          )
            for q in query:
                self.parseBusinessData( q, reviewList )

        return reviewList

    def getUser(self, user_id):
        user = User.get(User.user_id==user_id)
        return {'name':user.name, 
                'review_count':user.review_count,
                'average_stars':user.average_stars
                }

    def getBusinessesByReviewCount(self, num_businesses, review_count ):
        reviewList = []
        with db.transaction():
            query = (Business
                     .select(Business.business_id,Business.business_name,Business.stars, fn.Count(Business.business_id).alias('review_count'))
                     .join(Review)
                     .group_by(Business)
                     .having( fn.Count(Business.business_id) > review_count )
                     .limit(num_businesses)
                     )
            for q in query:
                self.parseBusinessData( q, reviewList )

        return reviewList
        
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
        self.count = 0
        JsonReader.__init__(self, input_file, output_file)
      
    def process_record(self, num_records=1):
        entrys = []
        ret = True
        for i in xrange(num_records):
            records = JsonReader.iterate_input_file(self, 1)
            for record in records:
                if not record:
                    ret = False
                    break
                review_business_id = record['business_id']
                review_text = record['text']
                review_stars = record['stars']
                review_date = record['date']
                review_user = record['user_id']
                business = None
                user = None
                skip = False
                try:
                    business = Business.get(Business.business_id==review_business_id)
                    user = User.get(User.user_id==review_user)
                except:
                    skip = True
                
                if skip :
                    continue
                entrys.append({ \
                                'business_id':business,
                                'user_id':user,
                                'stars':review_stars,
                                'text':review_text,
                                'date':review_date
                            })
            if ret == False:
                break
        
        if( len(entrys) == 0 ):
            return False
        self.count += 1
        print self.count
        with db.transaction():
            Review.insert_many(entrys).execute()

        return ret

class BusinessJsonReader( JsonReader ):
  
  def __init__(self, input_file, output_file):
    self.input_file = input_file
    self.output_file = output_file
    JsonReader.__init__(self, input_file, output_file)

  def process_record(self, num_records=1):
        entrys = []
        count = 0
        ret = True
        for i in xrange(num_records):
            records = JsonReader.iterate_input_file(self, 1)
            for record in records:
                if not record:
                    ret = False
                    break
                count += 1
                business_id = record['business_id']
                stars = record['stars']
                business_name = record['name']
                review_count = record['review_count']
                entrys.append({ \
                                'business_id':business_id,
                                'stars':stars,
                                'business_name':business_name,
                                'review_count':review_count
                            })
            if ret == False:
                break
        if( count < 1 ):
            return False
        
        with db.transaction():
            Business.insert_many(entrys).execute()

        return ret


class UserJsonReader( JsonReader ):
    
  def __init__(self,input_file,output_file):
    self.input_file = input_file
    self.output_file = output_file
    JsonReader.__init__(self, input_file, output_file)

  def process_record(self, num_records=1):
        entrys = []
        count = 0
        ret = True

        for i in xrange(num_records):
            records = JsonReader.iterate_input_file(self, 1)
            for record in records:
                if not record:
                    ret = False
                    break
                count += 1
                user_id = record['user_id']
                user_name = record['name']
                review_count = record['review_count']
                average_stars = record['average_stars']
                entrys.append({ \
                                'user_id':user_id,
                                'name':user_name,
                                'review_count':review_count,
                                'average_stars':average_stars
                            })
            if ret == False:
                break

        if( count < 1 ):
            return False
        
        with db.transaction():
            User.insert_many(entrys).execute()
    
        return ret
                          
# Perhaps, use a similar pattern for other files
# class UserJsonReader(JsonReader):
#


# TODO: Satyam - Should not hardcode the inputs here
# Gather from command line
# Reads NUM_RECORDS count of reviews belonging to 
# a particular business. 
# For each business review found, it will find 'NUM_RECORDS'
# count of reviews by the user. This may help to assign
# a weight to that particular business review.
def readDb():
    NUM_RECORDS = 10
    db_reader = DbReader()
    business_id = '-1bOb2izeJBZjHC7NWxiPA'

    #businesses = db_reader.getBusinesses(10)
    businesses = db_reader.getBusinessesByReviewCount(10,10)

    for business in businesses:
        businessReviews = db_reader.getBusinessReviews(business['business_id'],NUM_RECORDS)
        print "*********Business Reviews*************\n"
        business_count = 0
        for reviewb in businessReviews:
            business_count += 1
            print "%d." % business_count, reviewb['business_id'].business_id,reviewb['business_id'].business_name , reviewb['user_id'].user_id, reviewb['user_id'].name , reviewb['stars'], reviewb['date']
            print reviewb['tagged_text'], "\n"
            
            print "********User Reviews**********\n"
            user_count = 0
            userReviews = db_reader.getUserReviews(reviewb['user_id'],NUM_RECORDS)
            for reviewu in userReviews:
                user_count += 1
                print "%d.%d." % (business_count, user_count), reviewu['business_id'].business_id,reviewu['business_id'].business_name , reviewu['user_id'].user_id, reviewu['user_id'].name , reviewu['stars'], reviewu['date']
                print reviewu['tagged_text'], "\n"

def storeBusinessJson(NUM_RECORDS):
    business_json_reader = BusinessJsonReader(
        '../data/yelp_academic_dataset_business.json',
        '../output/yelp_review_output_business.json'    
    )

    ################ Tests #################
    business_json_reader.open_input_file()
    business_json_reader.read_input_file()
    
    # Should return the first ten json records
    #for i in range(NUM_RECORDS):
    while business_json_reader.process_record(NUM_RECORDS):
        pass
    business_json_reader.close_input_file()

def storeUserJson(NUM_RECORDS):
    user_json_reader = UserJsonReader(
        '../data/yelp_academic_dataset_user.json',
        '../output/yelp_review_output_user.json'
        )

    ################ Tests #################
    user_json_reader.open_input_file()
    user_json_reader.read_input_file()
    
    # Should return the first ten json records
    #for i in range(NUM_RECORDS):
    while user_json_reader.process_record(NUM_RECORDS):
        pass
        
    user_json_reader.close_input_file()

def storeReviewJson(NUM_RECORDS):
    review_json_reader = ReviewJsonReader(
        '../data/yelp_academic_dataset_review.json',
        '../output/yelp_review_output.json')

    ################ Tests #################
    review_json_reader.open_input_file()
    review_json_reader.read_input_file()
    
    # Should return the first ten json records
    # for i in range(NUM_RECORDS):
    while review_json_reader.process_record(NUM_RECORDS):
        pass
        
    review_json_reader.close_input_file()

def storeJsonToDb():
    db.connect()
    db.drop_tables([Business, Review, User],safe=True)
    db.create_tables([Business, Review, User],safe=True)
    #db.drop_tables([Review],safe=True)
    #db.create_tables([Review],safe=True)
    NUM_RECORDS = 500
    storeBusinessJson(NUM_RECORDS)
    storeUserJson(NUM_RECORDS)
    storeReviewJson(NUM_RECORDS)


    db.close()

import sys
if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == '--store':
        print "Storing Data"
        storeJsonToDb()
    else :
        print "Reading Data"
        readDb()
