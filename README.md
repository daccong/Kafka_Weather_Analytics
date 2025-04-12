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
  ### Bước 1 setup
  ```
  mkdir kafka-docker
  cd kafka-docker
  ```
  
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

  - Tham khảo thêm tại đây - [ kafka](https://hub.docker.com/r/bitnami/kafka)  - [Spark](https://hub.docker.com/r/bitnami/spark)
  - Vì do chạy trên docker và spark cũng chạy trên docker nên chúng ta để `- KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092`

  - Chạy file docker-compose.yml bằng cách `docker-compose up -d` với -d là detach chạy nền (không hiển thị log ra terminal )
### 2. Tạo topics 
Tạo các topics riêng lẻ như các luồng dữ liệu khác nhau cho các nhiệm vụ khác nhau `code_create_topic.py`
 * Với 3 Topics:
    * Topics_1: Weather_Hà_Nội
    * Topics_2: Weather_Hồ_Chí_Minh
    * Topics_3: Weather_Đà_Nẵng
 * Chạy file `python code_create_topics.py`

   ![image](https://github.com/user-attachments/assets/33dedf6f-ee1a-4a9e-b0ad-0cd23c9534f2)

### 3. Tạo producer
Producer có nhiệm vụ là gửi dữ liệu thời tiết theo từng khu vực vào topic đã tạo bước 2 `code_create_producer.py`

![image](https://github.com/user-attachments/assets/77503783-66c6-491b-bea1-2da322995a2e)

gửi dữ liệu vào các topics bằng producer mỗi 30s gọi đến API 1 lần 
Chạy file để đưa dữ liệu vào luồng dữ liệu topics 
### 4. Tạo Consumer với Spark
Kafka Consumer là một client application, subscribe một hoặc nhiều Kafka topics và đọc bản ghi theo thứ tự nó được tạo ra 
Tạo file `code_create_consumer.py`

![image](https://github.com/user-attachments/assets/416c0e37-4d13-4a01-bafd-e86024c4d805)

![image](https://github.com/user-attachments/assets/e8173a89-161c-4917-a386-2ab00a05a5d0)

với Consumer được tạo với Spark và được chạy trên Spark docker [tài liệu](https://hub.docker.com/r/bitnami/spark)

File `code_create_consumer.py` được đẩy lên docker trong container spark
![image](https://github.com/user-attachments/assets/9b3d7ad8-8d87-4c5f-ac9f-4c46ea6df335)
![image](https://github.com/user-attachments/assets/78d1a9e9-6009-46ed-ba37-ce26db6e42cc)
![image](https://github.com/user-attachments/assets/b5b3df51-4873-437e-aa07-63b632afd522)
![image](https://github.com/user-attachments/assets/62757f79-c21a-4322-a02d-56fc7d1668fe)

Log data
![image](https://github.com/user-attachments/assets/86bc0558-6ca8-4566-a0fa-17dc1ee04ccb)

### 5. Trực quan hóa
![image](https://github.com/user-attachments/assets/11288d90-7b62-465f-9fec-acd0c04ebb5c)
biểu đồ demo 
![image](https://github.com/user-attachments/assets/39c23a1e-eb79-48d1-a217-5474d6799beb)





