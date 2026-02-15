from pika import ConnectionParameters, BlockingConnection
import json

connection_params = ConnectionParameters(
    host="localhost",
    port=5672
)

def main():
    queue_message = input("Choose (Kwork or FL): ")

    message = {
        "arg1": "50",
        "arg2": "Разработка и IT",
    }

    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            if queue_message.lower() == "kwork":
                ch.queue_declare(queue=queue_message)
                ch.basic_publish(
                    exchange="",
                    routing_key=queue_message,
                    body=json.dumps(message).encode('utf-8')
                )
                print("Message about kwork sent")
            elif queue_message.lower() == "fl":
                ch.queue_declare(queue=queue_message)
                ch.basic_publish(
                    exchange="",
                    routing_key=queue_message,
                    body="Программирование"
                )
                print("Message about fl sent")

if __name__ == "__main__":
    main()