import logging

import pika

from encoder import on_message_receive

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Connect to RabbitMQ
credentials = pika.PlainCredentials("admin", "admin")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", credentials=credentials)
)

channel = connection.channel()
channel.queue_declare(queue="video_tasks")
channel.basic_qos(prefetch_count=1)

# Setup Consumer
channel.basic_consume(queue="video_tasks", on_message_callback=on_message_receive)

# Start consuming messages
logging.info("FFmpeg Worker started. Waiting for tasks...")
channel.start_consuming()
