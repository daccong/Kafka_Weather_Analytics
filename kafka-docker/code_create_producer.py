# gửi dữ liệu vào kafka Ví dụ gửi JSON thời tiết vào topic weather_hanoi.
from urllib.parse import quote
import json, time
import requests as rq
from kafka import KafkaProducer

def producer_to_topics():
    producer = KafkaProducer(
    bootstrap_servers = 'localhost:9092',
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
        

    while True:
        for city , weather_topic in cities.items():
            data = fetch_weather(quote(city))
            if data : 
                print(f'sending weather for {city} to topics {weather_topic}')
                producer.send(weather_topic , value = data)
        time.sleep(30)
        break
if __name__ == "__main__":
    producer_to_topics() 