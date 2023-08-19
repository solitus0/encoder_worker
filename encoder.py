import json
import logging
import re
import subprocess


def on_message_receive(ch, method, properties, body):
    data = decode_body(body)
    cmd = ["ffmpeg"] + data["cmd"]

    try:
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
        monitor_progress(process, data["media_duration"])
        process.communicate()

        logging.info("Video encoded successfully")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # Notify completion (can be another message to RabbitMQ or an API call)
        # ...

    except Exception as e:
        logging.error(f"Error encoding video: {str(e)}")
        # Error handling: retry, alert, etc.


def decode_body(body):
    decoded_data = body.decode()
    return json.loads(decoded_data)


def monitor_progress(process, media_duration):
    while True:
        line = process.stderr.readline()
        if not line and process.poll() is not None:
            break
        if "time=" in line:
            progress = parse_progress(line, media_duration)
            print(progress)


def parse_progress(line, media_duration):
    regex = re.compile(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})")
    match = regex.search(line)

    if match:
        elapsed_time = time_str_to_seconds(match.group(1))
        return round((elapsed_time / media_duration) * 100, 2)


def time_str_to_seconds(time_str):
    parts = list(map(float, time_str.split(":")))

    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    else:
        raise ValueError(f"Unexpected time format: {time_str}")
