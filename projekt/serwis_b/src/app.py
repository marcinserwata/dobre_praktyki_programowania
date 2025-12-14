from flask import Flask, request, jsonify
import pika
import json
import os

app = Flask(__name__)

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
QUEUE_NAME = 'image_analysis_queue'


def get_rabbitmq_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    return connection


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    if 'image_url' not in data:
        return jsonify({'error': 'Brakuje pola image_url'}), 400
    
    image_url = data['image_url']
    
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        message = json.dumps({'image_url': image_url})
        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        
        connection.close()
        
        return jsonify({
            'message': 'Zadanie zostało dodane do kolejki',
            'image_url': image_url
        }), 202
        
    except Exception as e:
        return jsonify({'error': f'Błąd kolejkowania: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
