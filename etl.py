import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, dayofweek, date_format
from pyspark.sql.functions import monotonically_increasing_id

config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['KEY']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['KEY']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    # get filepath to song data file
    input_song_path = input_data + 'song_data/*/*/*/*.json'
    
    # read song data file
    song_data =  spark.read.json(input_song_path)

    # extract columns to create songs table
    songs_table = song_data.select('song_id', 'title', 'artist_id', 'year', 'duration').drop_duplicates()
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.parquet(output_data + "songs/", mode="overwrite", partitionBy=["year","artist_id"])

    # extract columns to create artists table
    artists_table = song_data.select('artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude').drop_duplicates()
    
    # write artists table to parquet files
    artists_table.write.parquet(output_data + "artists/", mode="overwrite")


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    input_log_path = input_data + 'log_data/*/*/*.json'
    
    # read log data file
    log_data =  spark.read.json(input_log_path)

    
    # filter by actions for song plays
    log_data = log_data.filter(log_data['page'] == 'NextSong')

    # extract columns for users table    
    users_table = log_data.select('userId', 'firstName', 'lastName', 'gender', 'level').drop_duplicates() 
    
    # write users table to parquet files
    users_table.write.parquet(output_data + "users/", mode="overwrite")

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: datetime.utcfromtimestamp(int(x)/1000), TimestampType())
    log_data = log_data.withColumn("start_time", get_timestamp("ts"))
    
    # extract columns to create time table
    time_table = log_data.withColumn("hour",hour("start_time"))\
                .withColumn("day",dayofmonth("start_time"))\
                .withColumn("week",weekofyear("start_time"))\
                .withColumn("month",month("start_time"))\
                .withColumn("year",year("start_time"))\
                .withColumn("weekday",dayofweek("start_time"))\
                .select("start_time","hour", "day", "week", "month", "year", "weekday").drop_duplicates()
    
    # write time table to parquet files partitioned by year and month
    time_table.write.parquet(output_data + "time/", mode="overwrite", partitionBy=["year","month"])

    # read in song data to use for songplays table
    song_df = spark.read\
                .format("parquet")\
                .option("basePath", os.path.join(output_data, "songs/"))\
                .load(os.path.join(output_data, "songs/*/*/"))  
    
    

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = song_df.join(log_data, log_data.song == song_df.title, how='inner')\
                        .select(monotonically_increasing_id().alias("songplay_id"),col("start_time"),col("userId").alias("user_id"),"level","song_id","artist_id", col("sessionId").alias("session_id"), "location", col("userAgent").alias("user_agent"))
    
    songplays_table = songplays_table.join(time_table, songplays_table.start_time == time_table.start_time, how="inner")\
                        .select("songplay_id", songplays_table.start_time, "user_id", "level", "song_id", "artist_id", "session_id", "location", "user_agent", "year", "month")
    

    # write songplays table to parquet files partitioned by year and month
    songplays_table.drop_duplicates().write.parquet(os.path.join(output_data, "songplays/"), mode="overwrite", partitionBy=["year","month"])

def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3a://sparkify-data-lake-bucket-01/output/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
