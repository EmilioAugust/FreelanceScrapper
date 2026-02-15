from pika import ConnectionParameters, BlockingConnection
from scrappers.kwork import check_kwork
from scrappers.fl import check_fl
import json

connection_params = ConnectionParameters(
    host="localhost",
    port=5672
)

def process_fl(ch, method, properties, body):
    check_fl(body.decode())
    ch.basic_ack(delivery_tag=method.delivery_tag)

def process_kwork(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))

    if isinstance(data, dict):
        arg1 = data['arg1']
        arg2 = data['arg2']

    check_kwork(arg1, arg2)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    queue_message = input("Choose: ")
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            if queue_message.lower() == "kwork":
                ch.queue_declare(queue=queue_message)
                ch.basic_consume(
                    queue=queue_message,
                    on_message_callback=process_kwork
                )
                print("waiting for kwork...")
                ch.start_consuming()
            elif queue_message.lower() == "fl":
                ch.queue_declare(queue=queue_message)
                ch.basic_consume(
                    queue=queue_message,
                    on_message_callback=process_fl
                )
                print("waiting for fl...")
                ch.start_consuming()

if __name__ == "__main__":
    main()