from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DecimalType, LongType
from pyspark.sql.types import *
import code_create_producer as crp

# gọi data API đưa vào topics 
crp.producer_to_topics()

# Pyspark để lấy data từ topic_name
spark = SparkSession.builder.appName("KafkaWeatherconsumer") \
    .master('local[*]') \
    .config('spark.jars.packages' , 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0') \
    .getOrCreate()

weather_schema = StructType([
    StructField("latitude", DoubleType()),
    StructField("longitude", DoubleType()),
    StructField("resolvedAddress", StringType()),
    StructField("address", StringType()),
    StructField("timezone", StringType()),

    StructField("days", ArrayType(
        StructType([
            StructField("datetime", StringType()),
            StructField("tempmax", DoubleType()),
            StructField("tempmin", DoubleType()),
            StructField("temp", DoubleType()),
            StructField("feelslikemax", DoubleType()),
            StructField("feelslikemin", DoubleType()),
            StructField("feelslike", DoubleType()),
            StructField("dew", DoubleType()),
            StructField("humidity", DoubleType()),
            StructField("precip", DoubleType()),
            StructField("precipprob", DoubleType()),
            StructField("precipcover", DoubleType()),
            StructField("snow", DoubleType()),
            StructField("snowdepth", DoubleType()),
            StructField("windgust", DoubleType()),
            StructField("windspeed", DoubleType()),
            StructField("winddir", DoubleType()),
            StructField("pressure", DoubleType()),
            StructField("cloudcover", DoubleType()),
            StructField("visibility", DoubleType()),
            StructField("solarradiation", DoubleType()),
            StructField("solarenergy", DoubleType()),
            StructField("uvindex", DoubleType()),
            StructField("severerisk", DoubleType()),
            StructField("sunrise", StringType()),
            StructField("sunriseEpoch", LongType()),
            StructField("sunset", StringType()),
            StructField("sunsetEpoch", LongType()),
            StructField("moonphase", DoubleType()),
            StructField("conditions", StringType()),
            StructField("description", StringType()),
        ])
    ))
])

def city(topic_name):
    df_raw = spark.readStream \
        .format('kafka') \
        .option('kafka.bootstrap.servers', 'kafka:9092')\
        .option("subscribe", topic_name) \
        .load()
    spark.conf.set("spark.sql.debug.maxToStringFields", "1000")

    df_json = df_raw.selectExpr("CAST(value AS STRING)")\
            .select(from_json(col('value') , weather_schema).alias('weather_data'))
    print("đã hoàn thành 📂🤖")
    print("--->🌲", df_json)
    return df_json['weather_data']

#city('weather_ha_noi')
#spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /app/spark_consumer.py
