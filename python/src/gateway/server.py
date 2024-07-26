import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler

#custom modules
from auth import validate   
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server= Flask(__name__)

#Configures the Flask server to use a MongoDB 
mongo_user = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
mongo_host = os.environ.get("MONGO_HOST")

mongo_video = PyMongo(
    server, uri=f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/videos?authSource=admin"
)
mongo_mp3 = PyMongo(
    server, uri=f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/mp3s?authSource=admin"
)

fs_videos=gridfs.GridFS(mongo_video.db) #GridFS is used to store files greater than BSON limit of 16 MB.
fs_mp3s = gridfs.GridFS(mongo_mp3.db) 

"""
1.Establishes a connection to a RabbitMQ message broker.
2.Creates a channel on the RabbitMQ connection.
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host="rabbitmq-service",
    port=5673,  # 5673 because we changed the default.
))
channel = connection.channel() 
channel.queue_declare(queue=os.environ.get("VIDEO_QUEUE"))  #makes our queue if they don't already exist.
channel.queue_declare(queue=os.environ.get("MP3_QUEUE"))

scheduler = BackgroundScheduler()


#deleting old videos and mp3 files (>24 hours) from mongoDB.
def delete_old_files():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=1)

    old_videos = mongo_video.db.fs.files.find({"created_at": {"$lt": cutoff}})
    for video in old_videos:
        fs_videos.delete(video["_id"])

    old_mp3s = mongo_mp3.db.fs.files.find({"created_at": {"$lt": cutoff}})
    for mp3 in old_mp3s:
        fs_mp3s.delete(mp3["_id"])

scheduler.add_job(delete_old_files, 'interval', hours=24) #runs every 24 hours.
scheduler.start()


@server.route("/login", methods=["POST"])
def login():
    token, err= access.login(request)
    if not err:
        return token
    else:
        return err

@server.route("/upload", methods=["POST"])
def upload():
    access, err= validate.token(request)  #ensure user authentication before upload.
    if err:
        return err
    access=json.loads(access) #converting JSON string to python object
    if access["admin"] == True: #user has admin rights as only admins can upload files for now.
        if len(request.files) > 1 or len(request.files) < 1:  #ensures user has uploaded exactly one file.
            return ("Exactly one file required", 400)
        
        for _,f in request.files.items():
            err=util.upload(f, fs_videos, channel, access)
            if err:
                return err
        return ("Successfully uploaded file.", 200)

    else:
        return ("Not authorized",401)

@server.route("/download", methods=["GET"])
def download():
    access, err= validate.token(request)  #ensure user authentication before upload.
    if err:
        return err
    access=json.loads(access) #converting JSON string to python object
    
    if access["admin"] == True: #user has admin rights as only admins can upload files for now.
        fid_string = request.args.get("fid")
        if not fid_string:
            return "file id (fid) is required", 400
        try:
            out = fs_mp3s.get(ObjectId(fid_string)) #convert fid_string to mongo Object.
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500
    else: 
        return "Not authorized", 401

if __name__ == "__main__":
    server.run(host='0.0.0.0', port=8080)