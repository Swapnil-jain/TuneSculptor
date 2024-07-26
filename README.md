
# TuneSculptor
Converting videos (in almost all common formats) to mp3 format in a microservices architecture. 
Tech Stack Used: Python, Flask, RabbitMQ, Docker, Kubernetes, MongoDB, MySQL.

## Architecture

![image](https://github.com/user-attachments/assets/8c4ba34d-2fad-41e8-98e0-b9de6d0b8250)

A user is first intended to hit the `gateway` which will redirect user to `/login` which will ask the user for credentials. These credentials will then be stored in an MySQL database. The user will then be returned with a JWT token which will be used for authentication in all subsequent requests. The user will then be redirected to the `/upload` where they will be asked for a video file to be uploaded and an email address which will be used to send the converted file's download link. The file uploaded by the user is stored in MongoDB and it's data is pushed to a rabbitMQ queue called `video`. Now, the `converter` service will retrieve the mp4 file from monogDB using the message, convert the file to mp3, and push the resulting converted file's data to `mp3` queue and the file itself is again stored in MongoDB. The `notification` service then pulls the message from `mp3` queue and sends the user an email containing the link which has the file Id associated. Upon clicking the link, the user is redirected to the `/download` where they can then download the file which is served by the  MongoDB.

### Introduction

## Prerequisites

Before you begin, ensure that the following prerequisites are met:

If you directly intend to use the app using existing containers, all you need is:
1. **Docker Desktop**
2. **kubectl**
3. **minikube**
4. **k9s**: optional; used to visualise the k8s cluster better.
5. **Postman**: optional; to test the application. Otherwise use curl.
6. **mongodb compass*: optional; to visualise the database better.

If you need to make everything from scratch, in addition to above, you will need:
1. **Python**: Ideally create a virtual environment.
2. That's it !

### High Level Flow of Application Deployment

Follow these steps to deploy your microservice application:

1. Ensure Docker desktop is running with minikube on it. 
2. Run `minikube tunnel`.
3. Use `sudo vim /etc/hosts` to open up a file which helps map the domain-name we have specified that is mp3converter.com to our localhost. You also need to map rabbitmq-manager.com to your localhost to access the rabbitmq manager UI. So, add these 2 lines in the file:
```
127.0.0.1 mp3converter.com 
127.0.0.1 rabbitmq-manager.com
```
4. Navigate into each directory, example `cd python/src/auth`, and then run `kubectl apply -f ./k8s`. Do this for all the directories.
5. Use `k9s` command to visualise the k8s cluster.
6. If you are using MongoDB compass, run `kubectl port-forward <mongodb-pod-name> 27017:27017` to connect to MongoDB instance running on the k8s cluster using port forwarding. Also remember to use default credentials specified in `mongodb-secret.yaml`. The URI for connection should look like `mongodb://root:password123@localhost:27017/`.

### Notification Configuration

For configuring email notifications and two-factor authentication (2FA), follow these steps:

1. Go to your Gmail account and click on your profile.

2. Click on "Manage Your Google Account."

3. Navigate to the "Security" tab on the left side panel.

4. Enable "2-Step Verification."

5. Search for the application-specific passwords. You will find it in the settings.

6. Click on "Other" and provide your name.

7. Click on "Generate" and copy the generated password.

8. Paste this generated password in `notification/k8s/notification-secret.yaml` along with your email.


# API Definition
Run the application through the following API calls:

- **Login Endpoint**
`POST http://mp3converter.com/login`
Use Postman for selecting 'Basic Auth' and give username and password, the default being: personalprojectsample@gmail.com and Admin123

  Expected output: success! and a JWT token.

- **Upload Endpoint**
`POST http://mp3converter.com/upload` along with headers in format of `Authorization: Bearer <insert JWT Token>` and a body containing the mp4 file.

  Check if you received the ID on your email.

- **Download Endpoint**
  `GET http://mp3converter.com/download?fid=<Generated file identifier>`
