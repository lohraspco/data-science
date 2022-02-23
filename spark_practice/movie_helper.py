
from dataclasses import dataclass
from pyspark.sql.types import StructField, IntegerType, DoubleType, StringType, StructType

class DataModel:
    def __init__(self,spark, movie_case="ml-1m") -> None:
        schemaMovies = StructType([
            StructField("id", IntegerType(), True),
            StructField("title", StringType(), True),
            StructField("genre", StringType(), True)
        ])
        df_movies = spark.read.schema(schemaMovies).csv(f"hdfs:///user/hadoop/moviesdb/{movie_case}/movies.dat", sep="::")
        self.name_dict = {x.id:x.title for x in df_movies.select(['id','title']).collect()}
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("gender", StringType(), True),
            StructField("occupation", IntegerType(), True),
            StructField("zip", IntegerType(), True)
        ])
        self.user = spark.read.schema(schema=schema).csv(
            f"hdfs:///user/hadoop/moviesdb/{movie_case}/users.dat", sep="::")

        schema = StructType([
            StructField("userId", IntegerType(), True),
            StructField("movieId", IntegerType(), True),
            StructField("rating", IntegerType(), True),
            StructField("timestamp", IntegerType(), True),
        ])
        self.rating = spark.read.schema(schema).csv(
            f"hdfs:///user/hadoop/moviesdb/{movie_case}/ratings.dat", sep="::")