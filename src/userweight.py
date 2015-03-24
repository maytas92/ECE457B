from db import DbReader

MAX_RATING = 5.0

class UserWeight:
    # Returns a user weight that may be
    # used to give importance to reviews
    # based on the profile of the Yelp 
    # user.
    @staticmethod
    def get_user_weights(business_reviews):
        user_weights = []
        db_reader = DbReader()
        for br in business_reviews:
            user = db_reader.getUser(br['user_id'])
            review_rating = br['stars']
            user_avg_rating = user['average_stars']
            user_weights.append(abs(review_rating - user_avg_rating) / MAX_RATING)
        
        return user_weights