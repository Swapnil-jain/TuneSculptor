import pika, json

"""
upload function first uploads file to mongo database. If successful, it puts a message in queue. 
"""
def upload(f, fs, channel, access):
    try:
        fid = fs.put(f) #we get a file id (fid) if file upload was successful.
    except Exception as e:
            return "internal server error", 500
    
    #The message to be passed in rabbitMQ.
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,   #needs to be NULL as this is during UPLOAD time.
        "username": access["username"],
    }
    
    
    #Passing the message to rabbitMQ.
    try:
        channel.basic_publish(
            exchange="", #this is blank 
            routing_key="video",  #name of our queue
            body=json.dumps(message),  #converts python object to json string
            properties=pika.BasicProperties(
                delivery_MODE=pika.spec.PERSISTENT_DELIVERY_MODE #ensures that if a kubernetes pod resets or fails, the messages persist in the queue.
            ),
        )
    except:
        fs.delete(fid)  #cuz file which was uploaded now has no purpose.
        return "internal server error", 500