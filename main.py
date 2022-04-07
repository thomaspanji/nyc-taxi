from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    to_timestamp, 
    date_format,
    year, 
    month, 
    hour, 
    col, 
    round,
    ceil,
    floor,
    minute, 
    second,
    when
)

spark = SparkSession.builder \
    .master("local[4]") \
    .appName("NYC Green Taxi") \
    .getOrCreate()

df = spark.read \
    .format('csv') \
    .option("inferSchema", "true") \
    .option("header","true") \
    .load("/home/thomas/data/nyc_taxi/green_taxi/*2020*.csv")
df.printSchema()

df1 = df \
    .withColumn('year', year('lpep_pickup_datetime')) \
    .filter(col('year') == 2020)

df2 = df1 \
    .withColumn('lpep_pickup_datetime', to_timestamp('lpep_pickup_datetime')) \
    .withColumn('lpep_dropoff_datetime', to_timestamp('lpep_dropoff_datetime')) \
    .withColumn('pu_day', date_format('lpep_pickup_datetime', 'EEE')) \
    .withColumn('pu_time', hour('lpep_pickup_datetime')) \
    .withColumn('month', month('lpep_pickup_datetime')) \


df3 = df2 \
    .withColumn('trip_time', col('lpep_dropoff_datetime').cast('long') - col('lpep_pickup_datetime').cast('long')) \
    .withColumn('trip_time_min', round(col('trip_time')/60)) \
        .select(
        'VendorID',
        'lpep_pickup_datetime',
        'lpep_dropoff_datetime',
        'month',
        'pu_day',
        'pu_time',
        'PULocationID',
        'DOLocationID',
        'passenger_count',
        'trip_time_min',
        'trip_distance',
        'payment_type',
        'fare_amount',
        'total_amount'
    )

##############################################################
