Some commonly asked questions about these tech stacks in interviews as well as resources on where to study them from. Towards the end are various design desigins I had to make and the rationale behind them.

### About Docker:
1. Every new line is executed sequentially and each line creates a new layer. This helps in caching as if eg. something is changed in line 4, only lines after line 4 are ran again and lines before line 4 are just taken from the cache.
2. A Docker image is a lightweight, standalone, and executable software package that includes everything needed to run a piece of software, including the code, runtime, libraries, environment variables, and configuration files. Docker image is like a blueprint for the container. 
3. A container is a runnning instance of a Docker image.
4. By tagging a Docker image, it becomes easier for identifcation and management instead of using the long image ID everytime.
5. Container vs Virtual machine: A virtual machine has a full OS on it, including the kernel and it virtualises the underlying hardware via something called 'hypervisor'. A container only virtualises the software layers above the OS level, and each container run in its own isolated user space. 
6. RUN executes commands during the image build process to modify the image itself. CMD specifies the default command to run when a container is launched from the image.
7. How MongoDB works with kubernetes: https://www.youtube.com/watch?v=LPy6Q-q1MVQ&list=PLrMP04WSdCjrkNYSFvFeiHrfpsSVDFMDR&index=10

### About Kubernetes
1. It is used to automate the handling/orchestration of the containers. Eg. when to spin up, spin down, what happens when load increases etc.
2. A Kubernetes object is a "record of intent"--once you create the object, the Kubernetes system will constantly work to ensure that the object exists. By creating an object, you're effectively telling the Kubernetes system what you want your cluster's workload to look like; this is your cluster's desired state. We do this via the yaml file.
3. Stateless apps are those which don't depend on previous data (state) to function. Eg. Nodejs. They use a 'deployment' component in kubernetes, which creates multiple pods.
Stateful apps depend on previous data (state) to function. Eg. Databases, queues.
They use a 'StatefulSet' component in kubernetes. Refer https://www.youtube.com/watch?v=pPQKAR1pA9U&t=52s
4. What 'services' components are: https://www.youtube.com/watch?v=T4Z7visMM4E. 
- Since pods are frequently destoyed n created, it doesn't makes sense to use the pod's IP address. Services give our pods a static IP address. Services also do load balancing.
5. What 'Ingress' component is: https://www.youtube.com/watch?v=80Ew_fsV4rM
6. Volumes: https://www.youtube.com/watch?v=0swOh5C3OVM&t=313s
7. Difference between using the configmap/secret in envFrom and Volume: https://www.youtube.com/watch?v=FAnQTgr04mU&t=33s. Also see

### About rabbitMQ:
1. Synchronous Interservice communication means a client sending a request to a server is essentially blocked from doing anything else until server gives back the response. Eg. Gateway communicates with auth service synchronously. This also makes auth service and gateway tightly coupled.
2. Asynchronous Interservice communication means client need not await the server response. This is achieved in our case by using a queue (i.e RabbitMQ, Kafka, etc). So, we are using queue cuz the conversion of video may take time and we don't want our gateway to be blocked until then for other requests. This also makes gateway and videotomp3 service loosely coupled. 
3. Read also about strong consistency vs eventual consistency. We are using eventual consistency route.
4. RabbitMQ can have multiple queues inside and therefore we have something called an 'exchange' which is an entity which passes our messages to the correct queue.
5. Have a look at what 'competing consumers pattern' is in rabbitMQ docs.

### About JWT
Unlike the cookie+session based method of authentication, we are using JWT authentication. 
More info: Watch first 3 mins of https://www.youtube.com/watch?v=_3NKBHYcpyg&t=176s

# Decision-making
- From the start of the project, my aim was to make this application highly scalable. I wanted to implement all the industry best practices regarding system design which I had been reading theortically (I was reading book called 'Web Scalibilty for Startup Engineers').

## Microservices architecture
Microservices architecture was chosen as opposed to monolithic architecture. The rationale was:
1. 
2. Lastly, I had never worked with microservices before. This meant a whole new learning experience as I had to dive deep into learning containeraization (used Docker) and orchestration of those containers (used Kubernetes)

## CAP Theorem
CAP theorem meant I had to choose 2 between consistency, availability and partition tolerance.
For the authentication service, I chose consistency due to obvious reasons. 
For converter service, notification service and gateway service, I chose availability as users should be able to upload/download their data without any problems. Eventual consistency is fine for these services in contrast to strong consistency.

## Choosing databases
### MySQL (RDBMS)
For my user authentication service, I chose a mySQL RBDMS database over noSQL.
Why RDBMS over NoSQL ?
1. User authentication data is highly structured (e.g., usernames, passwords, email addresses). MySQL, being schema-based, efficiently handles this structured data with predefined relationships and constraints.
2. MySQL, being a RDBMS, supports ACID (Atomicity, Consistency, Isolation, Durability) properties, essential for handling transactional data such as user authentication.
3. MySQL is optimized for read-heavy operations and provides excellent performance for transactional workflows.
4. mySQL is a CA database, meaning it compromises on partition tolerance (). This was okay for authentication usecase as consistency and availability are a priority in these scenarios.

To support scalibility, I added **replication** feature. I want to add **sharding** in the future. 
I initially wanted to use mySQL operator to assist in managing the scaling of this database.
What is an Operator ? Definition from mySQL docs: The Kubernetes system uses Controllers to manage the life-cycle of containerized workloads by running them as Pods in the Kubernetes system. Controllers are general-purpose tools that provide capabilities for a broad range of services, but complex services require additional components and this includes operators. An Operator is software running inside the Kubernetes cluster, and the operator interacts with the Kubernetes API to observe resources and services to assist Kubernetes with the life-cycle management.
However, hardware limitations on my system were preventing me from using the SQL operator. I was getting an unexplanined bugs. So I decided to do it manually without an operator. I followed the docs on 'Run a Replicated Stateful Application' on k8s website.


### MongoDB (NoSQL)
I had to choose a noSQL database suitable for scalability for unstructured data like video and audio files.

For my video and audio files, I chose mongoDB, a noSQL database. 
Why noSQL ?
1. NoSQL databases are ideal for storing unstructured data such as media files. Its schema-less design allows for flexibility and ease-of-use.
2. MongoDB supports GridFS for storing large binary files, such as videos and MP3s, which can exceed the BSON-document size limit. This GridFS stores files in small chunks.
3. MongoDB's architecture allows for easy horizontal scaling. Sharding enables the distribution of large datasets across multiple servers, improving performance and storage capacity. 
4. Replica sets in MongoDB ensure high availability and automatic failover, crucial for a robust media storage system.
5. Following the CAP theorem, mongoDB is a CP database which is perfect for my needs. Availability can be compromised in favour of highly consistent data. This was the primary reason for not choosing cassandra as cassandra is AP database aiming for eventual consistency. 

# Some Challenges Faced
## Handling JWT
Handling JWT was challenging. Here is my current flow: User logs in, gets back a jwt token. The frontend js will save it to localstroage by name of 'token'. When uploading a file, a js function will fetch the 'token' from localstorage and then send it as a header along with the file. So far so good. The problem is when the link to download is being sent, and when I click on that, I was getting missing credentials. The reason was, since this request directly goes to the backend, there was no intermediary in between to include the Authorization header.
The solution suggested was to store the JWT as a cookie instead of local storage. This would eliminate the need to manually set the header everytime. This solution worked. The problem with this solution was that cookie have an attribute called 'httpOnly' which mean the cookies can be accessed by servers only and not by the frontend. This is a problem cuz my frontend is a separate microservice. To solve this, I had to add a new route to my backend called 'validate_token', which I use to confirm if the token is valid in the backend.

## RabbitMQ Clustering
RabbitMQ clustering is a lot more complicated than what I thought. You can't just increase the number of replicas to more than one and hope everything works. I referred to these resources:
https://www.rabbitmq.com/docs/cluster-formation (very confusing and intimidating)
https://www.rabbitmq.com/docs/clustering (very confusing and intimidating)
https://www.rabbitmq.com/blog/2020/08/10/deploying-rabbitmq-to-kubernetes-whats-involved (extremely helpful)
https://youtu.be/FzqjtU2x6YA?si=0_Rjam_xCGT4tPmE (extremely helpful)
https://youtu.be/_lpDfMkxccc?si=Lhet7sVd1cY8hfmv (extremely helpful)

### Things I learnt:
a. 'Erlang cookie' is something which is used by rabbitmq pods for authentication before adding the pods to the cluster. I need to make sure each pod has the same erlang cookie. 
b. Whenever joining a cluster, each pod loses it data and needs to be reset.
c. Joining a cluster, pods simply share the necessary information in order to communicate with each other. They do not share queues by default. So, if I have 3 pods: a,b and c as part of a cluster, and a message is pushed into 'a', but somehow a dies, that message is simply lost. This is where 'mirroring' queues concept is introduced. Basically, simply making a 'quorum' (as opposed to classic) queue solves this problem.
d. We need to have rbac.yml file used to used to create service accounts, roles, and role bindings to manage permissions for RabbitMQ within the Kubernetes cluster.
e. Some other config needs to be done in the statefulset file and configmap file.
f. Learnt about what an 'operator' is, and apparently it can automate all the problems I was facing.
g. Things and strategies that I learnt here made me realised I will need similar config for my mongo and mysql databases too.

## MongoDB clustering and replication
https://www.youtube.com/watch?v=7pUeN-BeGBs&t=593s (goldmine)
https://www.youtube.com/watch?v=DE83o7SR0xY 
https://www.youtube.com/watch?v=W-lJX3_uE5I&t=810s (goldmine)

This was the most time-consuming part of the project (~1 week) as I simply couldn't get replicaset+authentication to work. After trying countless combinations, I discovered that for some reason, running my monodb in a different namespace is preventing DNS resolution and therefore my other apps within the cluster are unable to connect to the mongodb replicaset. I decided to run it in default namespace for now. 
Getting authentication to work was challenging as I had to use a custom modified mongodb container which had some configuration in a 'keyFile' which is used by replicas to authenticate each other. I had to also use mongod and a bunch of commands to allow replication and authentication to work properly

## Static and Dynamic Provisioning
Referred:
https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/create-a-persistentvolume
https://minikube.sigs.k8s.io/docs/handbook/persistent_volumes/
https://www.youtube.com/watch?v=eFpiRzdIFgc

Dynamic provisioning is basically a way to ensure whenever a developer makes a PVC, a corresponding PV is automatically created without manual intervention.

### Things I leant:
1. Kubernetes supports hostPath for development and testing on a single-node cluster. A hostPath PersistentVolume uses a file or directory on the Node to **emulate** network-attached storage. In a production cluster, you would not use hostPath. Since I have no way of deploying my thing to production, I have to keep using hostPath for now.
2. A PV can have a class, which is specified by setting the `storageClassName` attribute to the name of a valid StorageClass. A PV of a particular class can only be bound to PVCs requesting that class. 
3. The flow is to first create a storage class, followed by a PV then a PVC. I can skip creating a PV if I go via the dynamic provisioning route. If I go via the dynamic provisioning route, I need to use `volumeClaimTemplates` in the statefulset itself, which functions like a PVC.