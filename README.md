# ECE457B
** Please ensure that a stable version of Python is installed on your machine. These programs 
   were tested with Python version 2.7.5 on MacOS 10.9.5**

To run the Fuzzy Logic System
1. Change directory to 'src'
2. Run the db.py script as ./db.py --store. 
   This will create tables for the 'review', 'business' and 'user' models
   by reading from the json files stored under the 'data' directory.
   Please ensure that 'yelp_academic_dataset_review.json', 'yelp_academic_dataset_user.json'
   and 'yelp_academic_dataset_business.json' are found under the 'data' directory.
   **This script can take up to a few minutes to run**.
   **Ensure that Peewee is installed on your machine. For MacOS - Pip may be used to install it.** 
   **Ensure that NLTK is installed on your machine. For MacOS - Pip may be used to install it. 
     In addition these links may be helpful - 
      http://www.nltk.org/install.html
      http://stackoverflow.com/questions/8590370/how-to-do-pos-tagging-using-nlp-pos-tagger-in-python
   **
NOTE: Only run step 3 once Step 2 has run successfully! 
      If it is desired to create a local database - then go to Step 4.
3. Run the main.py script as ./main.py -b <numBusiness> -r <numReviews>
   - Here numBusiness is an option to specify the number of businesses
     for which to run the Fuzzy Logic System. 
   - numReviews is an option to specify the number of reviews 
     to be used when predicting a rating for each business.
   Ensure that main.py has executable privileges on your machine.
   ** If step 2 was not run successfully for some reason - It is likely that one will receive an
       OperationalError 'no such table': business at this point. Please go back to Step 2.**

  If the main script runs successfully then the following output is seen:

  Input number of businesses <numBusiness>
  Input number of reviews <numReviews>
  Starting Fuzzy Logic System

  <BusinessName> x Reviews Found

  Running Maximum Valence Method
  Rating Errors Average  0.58 Median  0.4 Std   0.312    # Stats on the error associated with Review rating. 'Average' error : 'Median' error ..
  Defuzd Rating  Average  2.74 Median  3.0 Std  0.571    # Stats on the Defuzzified Rating. 'Average' review rating : 'Median' review rating ..
  ***** Business Rating*****  2.496                      # This is weighted average across <numReviews> for <businessName>
  Error in Business Rating  1.0035443038                 # This is the prediction error in the business rating.

  **Similar results are also shown for the Average Valence method and the Max-Average method**

4. Run the reviewvalence.py script ./reviewvalence.py -n <numreviews>
   This will enable the user to run the Fuzzy Logic System on <numreviews>. Note that there is no notion 
   of a business when using this script. 
   It is possible to view the various error metrics associated with 
   review ratings. The Defuzzified Rating metrics, such as the 'Average', 'Median' ratings given to reviews
   can also be seen.

