import json

import pika

RABBITMQ_HOST = "localhost"
RABBITMQ_QUEUE = "video_tasks"
RABBITMQ_USER = "admin"
RABBITMQ_PASS = "admin"


def push_message(message: dict):
    """Push the message to the RabbitMQ queue."""

    json_message = json.dumps(message)

    channel = get_channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=False)
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=json_message,
        properties=pika.BasicProperties(delivery_mode=2),
    )


def get_channel():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )

    return connection.channel()


if __name__ == "__main__":
    push_message(
        {
            "media_duration": 1440.0,
            "media_uuid": "4c985256-c283-4898-aefa-72ebaeb995a4",
            "cmd": [
                "-i",
                "/Users/ernestas/Downloads/media/Anime series FHD/Jujutsu Kaisen E28 copy 2.mkv",
                "-f",
                "matroska",
                "-ab",
                "128k",
                "-ac",
                "2",
                "-acodec",
                "libopus",
                "-ar",
                "48000",
                "-crf",
                "22",
                "-metadata",
                "media_uuid=4c985256-c283-4898-aefa-72ebaeb995a4",
                "-preset",
                "slow",
                "-vcodec",
                "libx265",
                "-vf",
                "scale=1920:1080",
                "-y",
                "/Users/ernestas/Downloads/media/Anime series FHD/.temp/encodes/Jujutsu Kaisen E28 copy 2.mkv",
            ],
        }
    )
