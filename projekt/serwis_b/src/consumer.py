import pika
import json
import requests
import os
import time
from io import BytesIO
from PIL import Image
from ultralytics import YOLO

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
SERWIS_A_URL = os.environ.get('SERWIS_A_URL', 'http://localhost:5000')
QUEUE_NAME = 'image_analysis_queue'

model = YOLO('yolov8n.pt')


def count_people(image_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(image_url, timeout=10, headers=headers)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        
        results = model(image)
        
        people_count = 0
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == 0:
                    people_count += 1
        
        return people_count
    
    except Exception as e:
        print(f"Błąd podczas analizy obrazu: {e}")
        return -1


def send_to_serwis_a(image_url, people_count, channel, method):
    try:
        response = requests.post(
            f'{SERWIS_A_URL}/results',
            json={
                'image_url': image_url,
                'people_count': people_count
            },
            timeout=5
        )
        response.raise_for_status()
        print(f"Wysłano wynik do serwisu A: {people_count} osób")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"Błąd wysyłania do serwisu A: {e}")
        return False


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        image_url = data['image_url']
        
        print(f"Analizuję obraz: {image_url}")
        
        people_count = count_people(image_url)
        
        if people_count < 0:
            print("Nie udało się przeanalizować obrazu")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return
        
        print(f"Wykryto {people_count} osób")
        
        success = send_to_serwis_a(image_url, people_count, ch, method)
        
        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("Nie udało się wysłać do serwisu A, wiadomość wróci do kolejki")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(5)  # Czekamy przed retry
            
    except Exception as e:
        print(f"Błąd przetwarzania: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    print("Uruchamiam konsumera...")
    
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            break
        except pika.exceptions.AMQPConnectionError:
            print("Czekam na RabbitMQ...")
            time.sleep(5)
    
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False
    )
    
    print("Czekam na wiadomości...")
    channel.start_consuming()


if __name__ == '__main__':
    main()
