import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
#custom modules
from auth import validate   
from auth_svc import access
from storage import util
import logging

# Configure logging settings
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO (or DEBUG for more details)

server= Flask(__name__)

#Configures the Flask server to use a MongoDB 
mongo_user = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
mongo_host = os.environ.get("MONGO_HOST")

#server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo_video = PyMongo(
    server, uri=f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/videos?authSource=admin"
)

fs_videos=gridfs.GridFS(mongo_video.db) #GridFS is used to store files greater than BSON limit of 16 MB.

"""
1.Establishes a connection to a RabbitMQ message broker.
2.Creates a channel on the RabbitMQ connection.
"""
def establish_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host="rabbitmq-service",
        port=5673,  # Port for HTTP requests to RabbitMQ. 5673 because we changed the default one.
    ))
    return connection


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
        try:
            connection = establish_rabbitmq_connection()
            channel = connection.channel() 
            for _,f in request.files.items():
                err=util.upload(f, fs_videos, channel, access)
                if err:
                    return err
            return ("Successfully uploaded file.", 200)
    
        finally:
            connection.close()
    else:
        return ("Not authorized",401)

@server.route("/download", methods=["GET"])
def download():
    pass #template for now

if __name__ == "__main__":
    server.run(host='0.0.0.0', port=8080)