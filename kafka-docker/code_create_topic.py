from kafka.admin import KafkaAdminClient, NewTopic
# tạo luồng pipline topics python 
def run_main():
    admin_kafka = KafkaAdminClient(
    bootstrap_servers = "localhost:9092",
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

if __name__ =="__main__":
    run_main()