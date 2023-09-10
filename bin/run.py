import argparse
import logging
import pika

from worker.config import (
    RABBITMQ_ENCODE_QUEUE,
    RABBITMQ_PROBE_QUEUE,
    RABBITMQ_HOST,
    RABBITMQ_PASS,
    RABBITMQ_USER,
)
from worker.encoder import on_message_receive as encode_on_message_receive
from worker.probe import on_message_receive as probe_on_message_receive
from worker.logging import configure_logging


def main(queue: str, callback):
    configure_logging()

    # Connect to RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )

    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)

    # Setup Consumer
    channel.basic_consume(queue=queue, on_message_callback=callback)

    # Start consuming messages
    logging.info(f"Waiting for messages on {queue}")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info(f"Stopping consumer on {queue}")
        channel.stop_consuming()
    except Exception as e:
        logging.error(f"Error consuming messages: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RabbitMQ Consumer CLI")

    parser.add_argument(
        "job_type",
        choices=["encode", "probe"],
        help="Type of job to process. Choices are 'encode' or 'probe'.",
    )

    args = parser.parse_args()
    job_type = args.job_type

    job_mappings = {
        "encode": (RABBITMQ_ENCODE_QUEUE, encode_on_message_receive),
        "probe": (RABBITMQ_PROBE_QUEUE, probe_on_message_receive),
    }

    queue, callback = job_mappings[job_type]
    main(queue, callback)
