import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor
from datetime import datetime, timezone

def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message) #converts json to python object.

    tf_path = None
    try:
        #empty temp file
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            #video contents
            out=fs_videos.get(ObjectId(message["video_fid"])) #convert the string video_fid to mongo object and then pass it to fs_vidoes.get()

            #add video contents to empty file
            tf.write(out.read())
            tf_name = tf.name

        #create audio from temp video file
        audio = moviepy.editor.VideoFileClip(tf_name).audio
        os.remove(tf_name) #delete the temp video file.

        #write audio to the file
        tf_path=tempfile.gettempdir() + f"/{message['video_fid']}.mp3"  #We are first taking the path to the temp directory and then appending the filename to the path.

        audio.write_audiofile(tf_path)

        #save file to mongo
        with open(tf_path, "rb") as f:
            data = f.read()
            fid = fs_mp3s.put(data, created_at=datetime.now(timezone.utc), username=message["username"])
    finally:
        #always clean up temp files even if an exception occurs
        if tf_path and os.path.exists(tf_path):
            os.remove(tf_path)

    #update the message
    message['mp3_fid']=str(fid) #mp3 file's id.

    try:
        channel.basic_publish(
            exchange="", #this is blank
            routing_key=os.environ.get("MP3_QUEUE"),  #name of our queue
            body=json.dumps(message),  #converts python object to json string
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE #ensures that if a kubernetes pod resets or fails, the messages persist in the queue.
            ),
        )
    except Exception as e:
        fs_mp3s.delete(fid)  #cuz mp3 which was uploaded now has no purpose.
        return "Failed to publish message" #will be returned. Hence go n see what happens if something is returned in consumer.py by this function.