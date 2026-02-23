import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE = "sentiment_logs"

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"LOG: {data}")
        with open("/logs/sentiment.log", "a") as f:
            f.write(f"{data}\n")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def main():
    while True:
        try:
            conn = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
                )
            )
            ch = conn.channel()
            ch.queue_declare(queue=QUEUE, durable=True)
            ch.basic_consume(queue=QUEUE, on_message_callback=callback)
            print("Logger started - waiting for messages...")
            ch.start_consuming()
        except Exception as e:
            print(f"Connection error: {e}. Reconnecting in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    main()