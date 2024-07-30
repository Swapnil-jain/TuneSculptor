import pika, json, os
from datetime import datetime, timezone
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
upload function first uploads file to mongo database. If successful, it puts a message in queue. 
"""
def upload(f, fs, channel, access):
    try:
        fid = fs.put(f, created_at=datetime.now(timezone.utc)) #we get a file id (fid) if file upload was successful.
    except Exception as e:
        return "internal server error-1", 500
    
    #The message to be passed in rabbitMQ.
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,   #needs to be NULL as this is during UPLOAD time.
        "username": access["username"],
    }
        
    max_retries = 5
    for attempt in range(max_retries):
        try:
            channel.basic_publish(
                exchange="", #this is blank 
                routing_key=os.environ.get("VIDEO_QUEUE"),  #name of our queue
                body=json.dumps(message),  #converts python object to json string
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE #ensures that if a kubernetes pod resets or fails, the messages persist in the queue.
                )
            )
            logger.info(f"Message published to RabbitMQ: {message}")
            return None  # Success
        except Exception as e:
            logger.error(f"Error publishing message to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    # If all retries fail, delete the uploaded file
    fs.delete(fid)
    return "internal server error-2", 500