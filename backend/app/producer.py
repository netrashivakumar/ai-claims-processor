import pika
import json

def send_to_queue(claim_data):
    # Connect to the RabbitMQ container
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='127.0.0.1') # Use 'rabbitmq' if running inside the same Docker network
    )
    channel = connection.channel()

    # Ensure the queue exists
    channel.queue_declare(queue='claims_queue', durable=True)

    # Publish the message
    channel.basic_publish(
        exchange='',
        routing_key='claims_queue',
        body=json.dumps(claim_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Makes the message persistent
        ))
    
    connection.close()
