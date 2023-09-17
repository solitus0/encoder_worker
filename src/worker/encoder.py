import json
import logging
import re
import subprocess
import time
from worker.config import (
    PROGRESS_UPDATE_INTERVAL,
    RABBITMQ_ENCODE_PROGRESS_QUEUE,
    RABBITMQ_ENCODE_RESULTS_QUEUE,
)


def on_message_receive(ch, method, properties, body):
    data = decode_body(body)
    logging.info(f"Starting to encode video with data: {data}")
    cmd = ["ffmpeg"] + data["command"]

    try:
        encode_started_at = time.time()

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )

        last_line = monitor_progress(process, data, ch)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            error_message = stderr or last_line
            logging.error(
                f"ffmpeg exited with code {process.returncode}. Error: {error_message}"
            )

            return

        duration = time.time() - encode_started_at
        duration = round(duration, 2)
        logging.info(f"Video encoded successfully, encoding duration: {duration}")
        send_result(ch, data["id"], duration)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logging.error(f"Error encoding video: {str(e)}")


def decode_body(body):
    decoded_data = body.decode()
    return json.loads(decoded_data)


def monitor_progress(process, data, ch):
    media_duration = data["duration_in_seconds"]
    last_update_time = time.time()
    last_line = None  # Store the last line read from stderr

    while True:
        current_time = time.time()
        if current_time - last_update_time > PROGRESS_UPDATE_INTERVAL:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            if "time=" in line:
                progress = parse_progress(line, media_duration)
                send_progress_to_rabbitmq(ch, progress, data)
                last_update_time = current_time
            last_line = line  # Update the last line read
        else:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            last_line = line  # Update the last line read

    return last_line  # Return the last line read from stderr


def send_progress_to_rabbitmq(ch, progress, data):
    ch.basic_publish(
        exchange="",
        routing_key=RABBITMQ_ENCODE_PROGRESS_QUEUE,
        body=json.dumps(
            {
                "progress": progress,
                "media_uuid": data["media_uuid"],
                "source_path": data["source_path"],
                "created_at": data["created_at"],
            }
        ),
    )


def send_result(ch, id, duration):
    ch.basic_publish(
        exchange="",
        routing_key=RABBITMQ_ENCODE_RESULTS_QUEUE,
        body=json.dumps(
            {
                "id": id,
                "duration": duration,
            }
        ),
    )


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
