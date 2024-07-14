import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3

def main():    
    mongo_user = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
    mongo_host = os.environ.get("MONGO_HOST")
    
    client = MongoClient(
        f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017") #Note that flask is not involved here. So we set mongodb up like this.
    db_videos= client.videos  
    db_mp3s= client.mp3s
    
    #gridfs
    fs_videos=gridfs.GridFS(db_videos)
    fs_mp3s=gridfs.GridFS(db_mp3s)
    
    #rabbitmq
    connection= pika.BlockingConnection(pika.ConnectionParameters(
        host="rabbitmq-service",
        port=5673,  
    ))
    channel = connection.channel()
     
    def callback(ch,method,properties,body):
        err=to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)  #send a negative acknowledgement so message is not removed from the queue.
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag) 
        
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"),
        on_message_callback=callback
    )
    
    print("Waiting for messages. To exit, press Ctrl+C")
    channel.start_consuming()
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted. Exiting..")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
            
#Note no port is exposed. This is cuz this is a consumer, and not a service that we are making requests to.