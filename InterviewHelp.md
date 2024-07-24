Some commonly asked questions about these tech stacks in interviews as well as resources on where to study them from.

### About Docker:
1. Every new line is executed sequentially and each line creates a new layer. This helps in caching as if eg. something is changed in line 4, only lines after line 4 are ran again and lines before line 4 are just taken from the cache.
2. A Docker image is a lightweight, standalone, and executable software package that includes everything needed to run a piece of software, including the code, runtime, libraries, environment variables, and configuration files. Docker image is like a blueprint for the container. 
3. A container is a runnning instance of a Docker image.
4. By tagging a Docker image, it becomes easier for identifcation and management instead of using the long image ID everytime.
5. Container vs Virtual machine: A virtual machine has a OS on it and it virtualises the hardware via something called 'hypervisor'. A container only virtualises the base OS.
6. RUN executes commands during the image build process to modify the image itself. CMD specifies the default command to run when a container is launched from the image.
7. How MongoDB works with kubernetes: https://www.youtube.com/watch?v=LPy6Q-q1MVQ&list=PLrMP04WSdCjrkNYSFvFeiHrfpsSVDFMDR&index=10

### About Kubernetes
1. It is used to automate the handling/orchestration of the containers. Eg. when to spin up, spin down, what happens when load increases etc.
2. A Kubernetes object is a "record of intent"--once you create the object, the Kubernetes system will constantly work to ensure that the object exists. By creating an object, you're effectively telling the Kubernetes system what you want your cluster's workload to look like; this is your cluster's desired state. We do this via the yaml file.
3. Stateful apps are those which don't depend on previous data (state) to function. Eg. Nodejs. They use a 'deployment' component in kubernetes, which creates multiple pods.
Stateless apps depend on previous data (state) to function. Eg. Databases, queues.
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
5. Have a look at what competing consumers pattern is in rabbitMQ docs.