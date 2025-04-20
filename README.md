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
- [MongoDB atlast]

```
+----------------+        +-------------------+        +-------------------+
|                |        |                   |        |                   |
|  Airflow       |        |     Kafka         |        |     Spark         |
| (Scheduler &   |        |   (Topics Broker) |        |   (Streaming Job) |
|  Webserver)    |        |                   |        |                   |
+-------+--------+        +--------+----------+        +---------+---------+
        |                          |                             |
        |  Gọi API định kỳ         |                             |
        |  (theo DAG schedule)     |                             |
        +------------------------->                             |
                                   |     Dữ liệu API được       |
                                   |     publish vào topic      |
                                   +--------------------------->|
                                                                 |
                                                                 | Xử lý dữ liệu
                                                                 | (filter, transform, etc.)
                                                                 |
                                      +--------------------------+-----------------------+
                                      |                                                  |
                                      v                                                  v
                            +------------------+                             +------------------+
                            |      MongoDB      |                             |  Visualization   |
                            | (Lưu trữ dài hạn) |                             |  (BI / Web App)  |
                            +------------------+                             +------------------+

```
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
x-airflow-common:
  &airflow-common

  build:
    context: .
    dockerfile : Dockerfile
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'true'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session'

    AIRFLOW__SCHEDULER__ENABLE_HEALTH_CHECK: 'true'

    _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:-}

  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./config:/opt/airflow/config
    - ./plugins:/opt/airflow/plugins
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    &airflow-common-depends-on
    redis:
      condition: service_healthy
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5
      start_period: 5s
    restart: always


  redis:
    # Redis is limited to 7.2-bookworm due to licencing change
    # https://redis.io/blog/redis-adopts-dual-source-available-licensing/
    image: redis:7.2-bookworm
    expose:
      - 6379
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 30s
      retries: 50
      start_period: 30s
    restart: always

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "3103:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:3103/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully



  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8974/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully



  airflow-worker:
    <<: *airflow-common
    command: celery worker
    healthcheck:
      # yamllint disable rule:line-length
      test:
        - "CMD-SHELL"
        - 'celery --app airflow.providers.celery.executors.celery_executor.app inspect ping -d "celery@$${HOSTNAME}" || celery --app airflow.executors.celery_executor.app inspect ping -d "celery@$${HOSTNAME}"'
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    environment:
      <<: *airflow-common-env
      # Required to handle warm shutdown of the celery workers properly
      # See https://airflow.apache.org/docs/docker-stack/entrypoint.html#signal-propagation
      DUMB_INIT_SETSID: "0"
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully



  airflow-triggerer:
    <<: *airflow-common
    command: triggerer
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type TriggererJob --hostname "$${HOSTNAME}"']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully


  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    # yamllint disable rule:line-length
    command:
      - -c
      - |
        if [[ -z "${AIRFLOW_UID}" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: AIRFLOW_UID not set!\e[0m"
          echo "If you are on Linux, you SHOULD follow the instructions below to set "
          echo "AIRFLOW_UID environment variable, otherwise files will be owned by root."
          echo "For other operating systems you can get rid of the warning with manually created .env file:"
          echo "    See: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#setting-the-right-airflow-user"
          echo
        fi
        one_meg=1048576
        mem_available=$$(($$(getconf _PHYS_PAGES) * $$(getconf PAGE_SIZE) / one_meg))
        cpus_available=$$(grep -cE 'cpu[0-9]+' /proc/stat)
        disk_available=$$(df / | tail -1 | awk '{print $$4}')
        warning_resources="false"
        if (( mem_available < 4000 )) ; then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough memory available for Docker.\e[0m"
          echo "At least 4GB of memory required. You have $$(numfmt --to iec $$((mem_available * one_meg)))"
          echo
          warning_resources="true"
        fi
        if (( cpus_available < 2 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough CPUS available for Docker.\e[0m"
          echo "At least 2 CPUs recommended. You have $${cpus_available}"
          echo
          warning_resources="true"
        fi
        if (( disk_available < one_meg * 10 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough Disk space available for Docker.\e[0m"
          echo "At least 10 GBs recommended. You have $$(numfmt --to iec $$((disk_available * 1024 )))"
          echo
          warning_resources="true"
        fi
        if [[ $${warning_resources} == "true" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: You have not enough resources to run Airflow (see above)!\e[0m"
          echo "Please follow the instructions to increase amount of resources available:"
          echo "   https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#before-you-begin"
          echo
        fi
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins}
        exec /entrypoint airflow version
    # yamllint enable rule:line-length
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_MIGRATE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow}
    user: "0:0"
    volumes:
      - ${AIRFLOW_PROJ_DIR:-.}:/sources

  airflow-cli:
    <<: *airflow-common
    profiles:
      - debug
    environment:
      <<: *airflow-common-env
      CONNECTION_CHECK_MAX_COUNT: "0"
    # Workaround for entrypoint issue. See: https://github.com/apache/airflow/issues/16252
    command:
      - bash
      - -c
      - airflow

  # You can enable flower by adding "--profile flower" option e.g. docker-compose --profile flower up
  # or by explicitly targeted on the command line e.g. docker-compose up flower.
  # See: https://docs.docker.com/compose/profiles/
  flower:
    <<: *airflow-common
    command: celery flower
    profiles:
      - flower
    ports:
      - "5555:5555"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:5555/"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully
  kafka:
    image: 'bitnami/kafka:latest'
    container_name: kafka
    ports:
      - '9092:9092'
    environment:
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=controller, broker
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
      - KAFKA_CFG_LISTENER_INTERFACES=PLAINTEXT://0.0.0.0:9092
    networks:
      - airflow_default
  spark:
    image: bitnami/spark:latest
    container_name: spark
    ports:
      - "2005:2005"
    environment:
      - SPARK_MODE=master
    volumes:
      - ./spark/spark_consumer.py:/app/spark/spark_consumer.py
    working_dir: /app
    command: sleep infinity
    networks:
      - airflow_default
volumes:
  postgres-db-volume:

networks:
  airflow_default:
    external: true
```

  - Tham khảo thêm tại đây - [ kafka](https://hub.docker.com/r/bitnami/kafka)  - [Spark](https://hub.docker.com/r/bitnami/spark)
  - Vì do chạy trên docker và spark cũng chạy trên docker nên chúng ta để `- KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092`
  - chú ý thiết lập chung mạng giữa các containers trong dockers
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





