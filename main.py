# -*- coding: utf-8 -*-
# Use getpass to obtain user netID
import getpass
from validated_models.ALS import CustomALS
from dataset_split.utils import readRDD
from validated_models.popularity import PopularityBaseline
from validated_models.popularity_validation import PopularityBaselineValidation
from validated_models.als_validation import ALSValidation
from pyspark.ml.recommendation import ALS
from validated_models.als_validation import CustomALS


# And pyspark.sql to get the spark session
from pyspark.sql import SparkSession
import dataset_split


#import ALS_custom


def main(spark, in_path, out_path):
    '''
    Parameters
    ----------
    spark : SparkSession object
    netID : string, netID of student to find files in HDFS
    '''
    print('LOADING....')
    print('')

    print('Splitting the ratings dataset into training, validation and test set')
    ratings_train, ratings_test, ratings_validation = dataset_split.ratingsSplit(
        spark, in_path, small=True, column_name='ratings', train_ratio=0.8, user_ratio=0.5)
    ratings_train.show()

    #movie_title_df, _ = readRDD(spark, in_path, small=True, column_name = 'movies')

    # split into training and testing sets
    # ratings_train.write.csv(f'{out_path}/ratings_train.csv')
    # ratings_validation.write.csv(f'{out_path}/ratings_validation.csv')
    # ratings_test.write.csv(f'{out_path}/ratings_test.csv')

    print("Distinct movies: ", ratings_train.select(
        "movieId").distinct().count())
    print("Distinct users: ", ratings_train.select("userId").distinct().count())
    print("Total number of ratings: ", ratings_train.count())

    X_train, X_test, X_val = ratings_train.drop('timestamp'), ratings_test.drop(
        'timestamp'), ratings_validation.drop('timestamp')
    
    '''
    ratings_per_user = ratings_train.groupby('userId').agg({"rating":"count"})
    ratings_per_user.describe().show()

    ratings_per_movie = ratings_train.groupby('movieId').agg({"rating":"count"})
    ratings_per_movie.describe().show()
 
    print("Training data size : ", X_train.count())
    print("Validation data size : ", X_val.count())
    print("Test data size : ", X_test.count())
    print("Distinct users in Training set : ", X_train[["userId"]].distinct().count())
    print("Distinct users in Test set : ", X_test[["userId"]].distinct().count())
    print("Distinct users in Validation set: ", X_val[["userId"]].distinct().count())
    
    print("Fitting Popularity baseline model")
    print("Tuning hyperparameters based on Mean Average Precision")
    damping_values = [0, 5, 10, 15, 20]
    best_baseline_model = PopularityBaselineValidation(X_train, X_val, damping_values)
    print("Evaluating best Popularity baseline model")
    baseline_metrics_train = best_baseline_model.evaluate(best_baseline_model.results, X_train)
    baseline_metrics_test = best_baseline_model.evaluate(best_baseline_model.results, X_test)
    print("MAP@100 on training set: ", baseline_metrics_train.meanAveragePrecision)
    print("MAP@100 on test set: ", baseline_metrics_test.meanAveragePrecision)
    print("NCDG@100 on training set: ", baseline_metrics_train.ndcgAt(100))
    print("NCDG@100 on test set: ", baseline_metrics_test.ndcgAt(100))
    '''
    
    
    
    print("Fitting ALS model")
    print("Tuning hyperparameters based on Mean Average Precision")
    als = CustomALS(rank = 10, regParam=0.1, maxIter=10)
    als.fit(X_train)
    als_metrics_val = als.evaluate(X_val)
    val_score = als_metrics_val.meanAveragePrecision
    print(val_score)
    
    
    '''
    rank_values = [10, 20, 30]
    regParam_values = [0.01, 0.1, 1, 10]
    maxIter_values = [10, 15]
    
    best_als_model = ALSValidation(X_train, X_val, rank_vals=rank_values, regParam_vals=regParam_values, maxIter_vals=maxIter_values)
    
    print("Evaluating best Popularity baseline model")
    als_metrics_train = best_als_model.evaluate(X_train)
    als_metrics_test = best_als_model.evaluate(X_test)
    print("MAP@100 on training set: ", als_metrics_train.meanAveragePrecision)
    print("MAP@100 on test set: ", als_metrics_test.meanAveragePrecision)
    print("NCDG@100 on training set: ", als_metrics_train.ndcgAt(100))
    print("NCDG@100 on test set: ", als_metrics_test.ndcgAt(100))
    '''
    


# Only enter this block if we're in main
if __name__ == "__main__":

    spark = SparkSession.builder.appName('project')\
        .config('spark.submit.pyFiles', 'Group26_MovieLens-0.4.2-py3-none-any.zip')\
        .config('spark.shuffle.useOldFetchProtocol', 'true')\
        .config('spark.shuffle.service.enabled', 'true')\
        .config('dynamicAllocation.enabled', 'true')\
        .getOrCreate()

    # Get user netID from the command line
    netID = getpass.getuser()

    # Get path of ratings file
    in_path = f'hdfs:/user/{netID}'  # sys.argv[1]

    # Get destination directory of training, validation and test set files
    out_path = f'hdfs:/user/{netID}'  # sys.argv[2]

    # Call our main routine
    main(spark, in_path, out_path)
