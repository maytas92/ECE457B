#!/usr/bin/python
import sys, getopt
from db import DbReader
from util import avg
from reviewvalence import MaxPOSValenceMethod, \
                          AveragePOSValenceMethod, \
                          MaxAveragePOSValenceMethod

def run_analysis(num_businesses, num_reviews):
    db_reader = DbReader()
    businesses = db_reader.getBusinesses(num_businesses)

    for business in businesses:
        businessReviews = db_reader.getBusinessReviews(business['business_id'], num_reviews)
        if len(businessReviews) < num_reviews:
            continue

        print '\n', business['business_name'], ' ', len(businessReviews), ' Reviews found\n'

        print 'Running Maximum Valence Method'
        max_pos_method = MaxPOSValenceMethod()
        max_pos_method.process_db_reviews(businessReviews)

        print 'Running Average Valence Method'
        average_pos_method = AveragePOSValenceMethod()
        average_pos_method.process_db_reviews(businessReviews)

        print 'Running Maximum Average Valence Method'
        max_average_pos_method = MaxAveragePOSValenceMethod()
        max_average_pos_method.process_db_reviews(businessReviews)


if __name__ == '__main__':
    # Default values 
    num_businesses = 1
    num_reviews = 10

    if len(sys.argv[1:]) < 3:
        print 'Missing arguments ./main -b <numbusinesses> -r <numreviews>'
        print 'Running default FLS with default arguments'        
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hb:r:", ["numbusinesses=", "numreviews="])
    except:
        print './main -b <numbusinesses> -r <numreviews>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':  
            print './main -b <numbusinesses> -r <numreviews>'
            sys.exit()
        elif opt in ("-b", "--numbusinesses"):
            num_businesses = int(arg)
        elif opt in ("-r", "--numreviews"):
            num_reviews = int(arg)

    print 'Input number of businesses ', num_businesses
    print 'Input number of reviews ', num_reviews  

    print 'Starting Fuzzy Logic System\n'
    run_analysis(num_businesses, num_reviews)

