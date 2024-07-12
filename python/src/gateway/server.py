import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo

#custom modules
from auth import validate   
from auth_svc import access
from storage import util

server= Flask(__name__)

#Configures the Flask server to use a MongoDB instance located at host.minikube.internal on port 27017 with the database videos.
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server) #Initializes the PyMongo extension with the Flask server.

fs=gridfs.GridFS(mongo.db) #GridFS is used to store files greater than BSON limit of 16 MB.

"""
1.Establishes a connection to a RabbitMQ message broker.
2.Creates a channel on the RabbitMQ connection.
"""
connection= pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

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
    access=json.loads(access) #converting JSON string to python object
    if access["admin"] == True: #user has admin rights as only admins can upload files for now.
        if len(request.files) > 1 or len(request.files) < 1:  #ensures user has uploaded exactly one file.
            return ("exactly one file required", 400)
        
        for _,f in request.files.items():
            err=util.upload(f, fs, channel, access)
            if err:
                return err
        return ("Success",200)
    else:
        return ("Not authorized",401)

@server.route("/download", methods=["GET"])
def download():
    pass #template for now

if __name__ == "__main__":
    server.run(host='0.0.0.0', port=8080)