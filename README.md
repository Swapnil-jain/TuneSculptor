
# TuneSculptor
Converting videos (in almost all common formats) to mp3 format in a microservices architecture. 
Tech Stack Used: Python, Flask, RabbitMQ, Docker, Kubernetes, MongoDB, MySQL.

## Architecture

![image](https://github.com/user-attachments/assets/8c4ba34d-2fad-41e8-98e0-b9de6d0b8250)

A user is first intended to hit the `gateway` which will redirect user to `/login` which will ask the user for credentials. These credentials will then be stored in an MySQL database. The user will then be returned with a JWT token which will be used for authentication in all subsequent requests. The user will then be redirected to the `/upload` where they will be asked for a video file to be uploaded and an email address which will be used to send the converted file's download link. The file uploaded by the user is stored in MongoDB and it's data is pushed to a rabbitMQ queue called `video`. Now, the `converter` service will retrieve the mp4 file from monogDB using the message, convert the file to mp3, and push the resulting converted file's data to `mp3` queue and the file itself is again stored in MongoDB. The `notification` service then pulls the message from `mp3` queue and sends the user an email containing the link which has the file Id associated. Upon clicking the link, the user is redirected to the `/download` where they can then download the file which is served by the  MongoDB.

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
2. Run `minikube delete; minikube start --memory 3072 --cpus 4`. This is important because minikube runs with 2 cpu cores and 2 gb ram by default, which is pretty less to run our cluster locally. You may increase the memory further to 4096 if you have more RAM available.
3. Run `minikube addons enable ingress` to enable the ingress add-on. This will allow minikube to work with our ingress properly.
4. Run `minikube tunnel`.
5. Use `sudo vim /etc/hosts` to open up a file which helps map the domain-name we have specified that is mp3converter.com to our localhost. You also need to map rabbitmq-manager.com to your localhost to access the rabbitmq manager UI. So, add these 2 lines in the file:
```
127.0.0.1 mp3converter.com 
127.0.0.1 rabbitmq-manager.com
```
6. Navigate into each directory, example `cd python/src/auth`, and then run `kubectl apply -f ./k8s`. Do this for all the directories.
7. Use `k9s` command to visualise the k8s cluster.
8. If you are using MongoDB compass, run `kubectl port-forward <mongodb-pod-name> 27017:27017` to connect to MongoDB instance running on the k8s cluster using port forwarding. Also remember to use default credentials specified in `mongodb-secret.yaml`. The URI for connection should look like `mongodb://root:password123@localhost:27017/`.

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

### Mongo Configuration
We need to setup mechanism for replication and authentication.
1. Run `kubectl exec --namespace <namespace> -it <name of pod> -- mongosh` to run bash inside one of our mongodb pods.
2. Now run
`
rs.initiate(
   {
      _id: "res0",
      version: 1,
      members: [
         { _id: 0, host : "mongodb-statefulset-0.mongodb-headless:27017" },
         { _id: 1, host : "mongodb-statefulset-1.mongodb-headless:27017" },
      ]
   }
)
`
to initialize the replicaset.
3. Run `use admin` followed by 
`
db.createUser(
   {
     user: "swapnil",
     pwd: "password123",
     roles: [ { role: "root", db: "admin" } ],
     mechanisms: [ "SCRAM-SHA-256" ]
   }
)
`
to create a admin user.
to initialise our cluster with 2 members. 2 because that is what the the number of replicas is.
4. Our replicas and authentication is ready !

If you want to need to checkout the mondoDB database/cluster:
1. Run `kubectl exec --namespace <namespace> -it <name of pod> -- /bin/bash` to run bash inside one of our mongodb pods.
2. Run either 
`mongosh mongodb://<username>:<password>@<nameofanypod>.<headless-servicename>:27017/?replicaSet=<replicasetname>` 
or 
`mongosh mongodb://<username>:<password>@<nameofpod-0>.<headless-servicename>:27017,<nameofpod-1>.<headless-servicename>:27017,<nameofpod-2>.mongodb-headless:27017/`
Both of these commands are basically the same. Note the 2nd command is technically a little worse as you would need to include name of every pod. I have used 3 replicas, and hence 3 names. So stick to the first command. In our case, the first command becomes `mongosh mongodb://swapnil:password123@mongodb-statefulset-0.mongodb-headless:27017/?replicaSet=res0`
3. Run `rs.status()` to ensure all pods are connected in the cluster and see cluster status.
4. If you ever need to go inside the database itself, run `show dbs` and go inside videos and mp3s using `use videos` and `use mp3s`.

**Some additional notes**: 
1. If you need to add more nodes to our cluster, you need to do use rs.add() to add them manually in the cluster.
2. In MongoDB, each database has its own user roles and you can create user for a specific database. In our case, we choose the 'admin' database to create our user. We need to then specify this admin database everytime we connect to mongo for authentication, however since this is the default authentication database, it can be skipped.
3. If you need to connect from outside the cluster to the database, example using mongo compass, you may use `mongodb://<username>:<password>@127.0.0.1:27017/?directConnection=true&authSource=admin` to connect.

### MySQL Configuration
MySQL is already configured if you have a look in mysql-cm.yaml. To access the database, you need to run `kubectl exec --namespace <namespace> -it <name of pod> -- /bin/bash` followed by `mysql -u <username> -p` and then enter password. Note that the default username is `root` and password we have setup is `Auth123`. The database we are using is `auth`.

## API Definition
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


## Useful information
1. If you change anything within a pod and start getting Internal server errors, the first thing to do is run `kubectl delete pods --all -A`. This will simply restart all the pods, and might very often fix the problem.
2. Another useful command is `kubectl scale deploy -n <namespace> --replicas=0 --all` to scale down all the deployments and `kubectl scale statefulsets -n <namespace> --replicas=0 --all` to scale down all the statefulsets.
3. The `resources` inside deployments and statefulsets need to be increased when in production. The current limit are just enough for testing purposes in a minikube single-node environment.
4. You can run `docker stats` to monitor the minikube resource consumption and limits. If you are experiencing erros or 'TLS Handshake' failures, check to ensure consumption is within the limits.
5. Sometimes `storage-provisioner` which is part of the kube-system stops working and due to that our databases stop working and gateway throws internal server erros. To fix this, simply restart minikube using `minikube stop` and `minikube start`.