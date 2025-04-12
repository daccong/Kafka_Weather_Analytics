# 🌤️ Weather-Kafka-Pipeline
Dự án sử dụng Apache Kafka để thu thập dữ liệu thời tiết theo thời gian thực từ nhiều thành phố khác nhau thông qua API, xử lý dữ liệu với PySpark và trực quan hóa bằng Pandas và Matplotlib.
## 📌 Mục tiêu
- Tạo các Kafka topics tương ứng với từng thành phố.
- Gọi API thời tiết cho từng thành phố và publish dữ liệu vào Kafka topics tương ứng.
- Sử dụng PySpark để xử lý dữ liệu từ Kafka và phân tích.
- Chuyển đổi dữ liệu thành Pandas DataFrame để trực quan hóa bằng Matplotlib real-time.
- Có thể tích hợp thêm Machine Learning để dự đoán thời tiết và gửi thông báo cảnh báo đến mọi người
## 🛠️ Công nghệ sử dụng
- [Apache Kafka](https://kafka.apache.org/) - Streaming platform
- [PySpark](https://spark.apache.org/docs/latest/api/python/) - Xử lý dữ liệu phân tán
- [Pandas](https://pandas.pydata.org/) - Phân tích dữ liệu
- [Matplotlib](https://matplotlib.org/) - Trực quan hóa
- [OpenWeatherMap API](https://openweathermap.org/api) (hoặc API thời tiết tương tự)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ( triển khai ) 
- 
## Cấu trúc file 
```
weather-kafka-pipeline/
│
├── producer/                # Gửi dữ liệu thời tiết đến Kafka
│   └── weather_producer.py
│
├── consumer/                # Lấy dữ liệu từ Kafka bằng PySpark
│   └── spark_weather_consumer.py
│
├── visualization/           # Vẽ biểu đồ bằng Pandas + Matplotlib
│   └── plot_weather_data.py
│
├── config/                  # Chứa config như API keys, Kafka settings
│   └── settings.json
│
├── requirements.txt         # Thư viện cần cài
└── README.md
```
## ▶️ Hướng dẫn chạy
Cài đặt Docker Desktop trên máy [tại đây](https://www.docker.com/products/docker-desktop/)
- Thiết lập cài đặt đảm bảo máy đã có docker:
![image](https://github.com/user-attachments/assets/f1213917-a15d-4f30-b5d2-f7774fbe9da9)
- tạo thư mục mới
  `
  mkdir kafka-docker
  
  cd kafka-docker
  `
- Tạo file `docker-compose.yml`
  
```
version: '3.8'

services:
  kafka:
    image: bitnami/kafka:latest
    ports:
      - '9092:9092'
    environment:
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
      - KAFKA_CFG_LISTENER_INTERFACES=PLAINTEXT://0.0.0.0:9092

  spark:
    image: bitnami/spark:latest
    container_name: spark
    ports:
      - '8080:8080'
    environment:
      - SPARK_MODE=master
    volumes:
      - ./spark_consumer.py:/app/spark_consumer.py
    working_dir: /app
    command: sleep infinity
```

  - Tham khảo thêm [tại đây kafka](https://hub.docker.com/r/bitnami/kafka) [Spark](https://hub.docker.com/r/bitnami/spark)
  - Vì do chạy trên docker và spark cũng chạy trên docker nên chúng ta để `- KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092`
  


