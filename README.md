# Data Lake Project

## Introduction

A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. The data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app. The objective of the project is to build an ETL pipeline that extracts the data from S3, processes them using Spark, and loads the data back into S3 as a set of dimensional tables. This will allow the analytics team to continue finding insights in what songs their users are listening to.

## Datasets

There are 2 datasets in the S3 buckets which needs to be transformed.
* Song Data which resides in `s3://udacity-dend/song_data`. This is a subset of the [milllion song dataset](http://millionsongdataset.com/). Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset.

* Log Data which resides in `s3://udacity-dend/log_data`. It consists of files in JSON format partitioned by year and month. 

## ETL Process

The ETL pipeline consists of the following steps.

* Read data from S3 buckets.

* Data processing using Spark.

This step is used to create a star schema optimized for queries on song play analysis. 
The new tables are described below.

** Fact Table

`songplays` - records in log data associated with song plays i.e. records with page NextSong. The columns are songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location and user_agent.

** Dimension Tables

`users` - users in the app. The columns are user_id, first_name, last_name, gender and level.
`songs` - songs in music database. The columns are song_id, title, artist_id, year, duration.
`artists` - artists in music database. The columns are artist_id, name, location, lattitude and longitude.
`time` - timestamps of records in songplays broken down into specific units. The columns are start_time, hour, day, week, month, year, weekday.

* Load the transformed data to S3 buckets.

## How to Run

* Fill in the AWS KEY and AWS access key in `dl.cfg` file. 
* Create a new S3 bucket to store the output. Update the output_data variable in `etl.py` so that it points to the new S3 bucket created. 
* Run `etl.py` script.


