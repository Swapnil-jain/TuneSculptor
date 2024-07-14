import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor

def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message) #converts json to python object.
    
    #empty temp file
    tf= tempfile.NamedTemporaryFile()
    
    #video contents
    out=fs_videos.get(ObjectId(message["video_fid"])) #convert the string video_fid to ID object and then pass it to fs_vidoes.get()
    
    #add video contents to empty file
    tf.write(out.read())
    
    #create audio from temp video file
    audio =moviepy.editor.VideoFileClip(tf.name).audio
    
    tf.close() #delete the temp file.
    
    #write audio to the file
    tf_path=tempfile.gettempdir() + f"/{message['video_fid']}.mp3"  #We are first taking the path to the temp directory and then appending the filename to the path.
    audio.write_audiofile(tf_path)
    
    #save file to mongo
    f=open(tf_path, "rb")
    data=f.read()
    fid=fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)
    
    #update the message
    message['mp3_fid']=str(fid) #mp3 file's id.
    
    try:
        channel.basic_publish(
            exchange="", #this is blank 
            routing_key=os.environ.get("MP3_QUEUE"),  #name of our queue
            body=json.dumps(message),  #converts python object to json string
            properties=pika.BasicProperties(
                delivery_MODE=pika.spec.PERSISTENT_DELIVERY_MODE #ensures that if a kubernetes pod resets or fails, the messages persist in the queue.
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid)  #cuz mp3 which was uploaded now has no purpose.
        return "Failed to publish message" #will be returned. Hence go n see what happens if something is returned in consumer.py by this function.