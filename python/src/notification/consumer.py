import pika
import sys
import os
from send import email


def main():
    #rabbitmq
    connection= pika.BlockingConnection(pika.ConnectionParameters(
        host=os.environ.get("RABBIT_HOST"),
        port=5672,  
    ))
    channel = connection.channel()

    def callback(chan, method, properties, body):
        err = email.notify(body)
        if err:
            chan.basic_nack(delivery_tag=method.delivery_tag)
        else:
            chan.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"),
        on_message_callback=callback
    )

    print("Waiting for messages. To leave: CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted. Exiting..")
        # Graceful exit
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

#Note no port is exposed. This is cuz this is a consumer, and not a service that we are making requests to.