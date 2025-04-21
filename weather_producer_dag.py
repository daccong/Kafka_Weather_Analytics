from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.operators.bash import BashOperator
from kafka.admin import KafkaAdminClient, NewTopic
from urllib.parse import quote
import json, time
import requests as rq
from kafka import KafkaProducer

def producer_to_topics():
    producer = KafkaProducer(
    bootstrap_servers = 'kafka:9092',
    value_serializer = lambda v : json.dumps(v).encode('utf-8')
)
    cities = {
        "Hanoi": "weather_hanoi",
        "Ho Chi Minh City": "weather_hcm",
        "Da Nang": "weather_danang"
    }

    def fetch_weather(city_name):
        API_KEY = '4MEDEDAKHLU39S7MKCHQ3FYBX'
        url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city_name}?unitGroup=us&include=hours&key={API_KEY}&contentType=json'
        repon = rq.get(url)
        if repon.status_code == 200:
            return repon.json()
        else:
            print("❌ Failed to fetch weather for")
            return None
        
    for city , weather_topic in cities.items():
        data = fetch_weather(quote(city))
        if data : 
            print(f'sending weather for {city} to topics {weather_topic}')
            producer.send(weather_topic , value = data)

    producer.flush()
    

def run_main():
    admin_kafka = KafkaAdminClient(
    bootstrap_servers = "kafka:9092",
    client_id = "weather_id"
)
    topics = [NewTopic(
        name = "weather_ha_noi", num_partitions = 1, replication_factor= 1),
            NewTopic(
        name = "weather_Ho_chi_minh" ,num_partitions = 1, replication_factor= 1
            ),
            NewTopic(
        name = "weather_da_nang", num_partitions=1 , replication_factor=1
            )]

    admin_kafka.create_topics(
        new_topics= topics, 
        validate_only= False
    )
    print("✅ Created topics successfully.")


default_args = {
    'start_date': datetime(2025 , 4,21),
    'retries': 1
}

dag = DAG(
    dag_id= 'Weather_pipeline',
    description='Run kafka weather',
    schedule_interval= '@hourly',
    catchup= False,
    default_args=default_args
)
dag_one = DAG(
    dag_id = 'create_topics',
    description='create_topics',
    schedule_interval= None,
    default_args=None,
     catchup= False
)
task_topics = PythonOperator(
    task_id = 'create_topics',
    python_callable = run_main,
    dag = dag_one
)

task_send_data = PythonOperator(
    task_id = 'Send_data_topics',
    python_callable=producer_to_topics,
    dag = dag
)

task_consumer_hn = BashOperator(
    task_id = 'weather_ha_noi',
    bash_command='docker exec spark spark-submit /app/spark/spark_consumer.py --topic weather_ha_noi',
    dag = dag
)
task_consumer_dn = BashOperator(
    task_id = 'weather_da_nang',
    bash_command='docker exec spark spark-submit /app/spark/spark_consumer.py --topic weather_da_nang',
    dag = dag
)
task_consumer_hcm = BashOperator(
    task_id = 'weather_Ho_chi_minh',
    bash_command='docker exec spark spark-submit /app/spark/spark_consumer.py --topic weather_Ho_chi_minh',
    dag = dag
)

task_topics
task_send_data >> [task_consumer_hn , task_consumer_dn, task_consumer_hcm]