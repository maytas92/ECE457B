from numpy import mean, median, std, percentile

class StatAnalysis:
    @staticmethod
    def get_review_rating_accuracy(target_ratings, defuzzied_ratings):
        if len(target_ratings) != len(defuzzied_ratings):
            raise Exception('The size of the target ratings and defuzzied_ratings \
                             is not equal')
        error_arr = []
        for tr, dr in zip(target_ratings, defuzzied_ratings):
            error_arr.append(tr - dr)
        avg_error = mean(error_arr)
        median_error = median(error_arr)
        std_err = std(error_arr)

        print 'Average error ', avg_error
        print 'Median error ', median_error
        print 'Std error ', std_err
        print 'IQR ', percentile(error_arr, 75) - percentile(error_arr, 25)

    @staticmethod
    def get_review_rating_stats(ratings):
        print 'Average rating ', mean(ratings)
        print 'Median rating ', median(ratings)
        print 'Std rating ', std(ratings)


if __name__ == '__main__':
    StatAnalysis.get_review_rating_accuracy([1, 3, 5, 2, 4], [2, 3, 4.5, 2, 3.75])
    StatAnalysis.get_review_rating_stats([1, 2, 3, 4, 5])