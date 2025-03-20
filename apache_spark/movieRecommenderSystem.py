from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pyspark.sql.functions as func
from pyspark import SparkFiles
import sys


# did not work
# print("kl;ads;klfj;kalsjdfj;asdl;fksd;kalsjdl;fksd;jkalsdjfkljkalsadf")
# SparkFiles.get("movie_helper.py")
# sys.path.insert(0,SparkFiles.getRootDirectory())

# spark = SparkSession.builder.appName("movieslarge").getOrCreate()
spark = (
    SparkSession.builder.appName("movieslarge")
    .master("spark://spark-master:7067") # Spark stand alone
    # .master("local[*]") # if runnung local
    # .master("yarn")
    # .master("mesos://<mesos-master-url>")

    .config("spark.driver.host", "10.0.0.177")
    # .config("spark.executor.memory", "2g")
    # .config("spark.driver.memory", "2g")
    .getOrCreate()
)
sc =spark.sparkContext
sc.addPyFile('movie_helper.py')
from apache_spark.data.movie_helper import *

df = DataModel(spark)
df_pairs = df.rating.alias("df1").join(df.rating.alias("df2")).\
    where( (col("df1.userId")==col("df2.userId")) & (col("df1.movieId")<col("df2.movieId"))).\
        select( col("df1.rating").alias("rating1"),
        col("df2.rating").alias("rating2"),
       col("df1.movieId").alias("movie1"),
        col("df2.movieId").alias("movie2"))

df_pairs2 = df_pairs.withColumn("x_sq", col("rating1")*col("rating1")).\
    withColumn("y_sq", col("rating2")*col("rating2")).\
    withColumn("xy",col("rating1")*col("rating2"))
df_sim_helper = df_pairs2.groupBy("movie1","movie2").\
    agg(func.sum(col("xy")).alias("numerator"),\
        func.sqrt( func.sum(col("x_sq")) *func.sum(col("y_sq"))).alias("denominator") ,\
        func.count(col("xy")).alias("countPairs"))

df_similarity = df_sim_helper.withColumn("score", func.when(col("denominator")!=0 , col("numerator")/col("denominator")).otherwise(0))

df_similarity_cached = df_similarity.cache()

scoreThreshold = 0.97
coOccurrenceThreshold = 50.0

movie_names = spark.sparkContext.broadcast( df.name_dict )
def lookup_name(movieID):
    return movie_names.value[movieID]
# check for shawshank redemption
mId = 318
filteredResults = df_similarity_cached.filter((col("movie1")==mId) | (col("movie2")==mId) &\
    (col("score")>scoreThreshold) & (col("countPairs") > coOccurrenceThreshold))

results = filteredResults.sort(func.col("score").desc()).take(10)


print(f"top 10 similar movies to { movie_names.value[mId]} are :")
for res in results:
    similarMovie = res.movie1 if mId == res.movie2 else res.movie2 
    print(movie_names.value[similarMovie])
