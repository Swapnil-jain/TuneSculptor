import jwt, datetime, os #for auth
from flask import Flask, request
from flask_mysqldb import MySQL

server= Flask(__name__)

#config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

mysql=MySQL(server) #instance of MySQL

@server.route("/login", methods=["POST"])
def login():
    auth=request.authorization  #auth should have authenticated header.
    if not auth:
        return("Missing credentials", 401) #in case doesnt have authorization header
    
    #check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT email, password FROM user WHERE email = %s AND password = %s", (
        auth.username, auth.password, )
    )
    
    if res > 0: #means result exists in database
        return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return("Invalid credentials", 401)

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt=request.headers["Authorization"]
    if not encoded_jwt:
        return("Missing credentials", 401)
    encoded_jwt=encoded_jwt.split(" ")[1] #Remember authorization token look like "Authorization: Bearer" so, we can split it based on the space.
    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithm=["HS256"]
        )
    except:
        return("Not authorized", 403)
    
    return (decoded,200)
    
    
def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow()
 + datetime.timedelta(days=1), #token expires in 24 hours
            "iat": datetime.datetime.utcnow()
,  #when token was issued.
            "admin": authz, #whether user is admin or not
        },
        secret,
        algorithm="HS256",
    )
    
if __name__ == "__main__": #resolves __name__ variable to __main__  
    server.run(host="0.0.0.0", port=5000) #host="0.0.0.0" tells the server to listen on all available IP addresses, making it accessible from other machines on the network. In this case, it will listen to all of the docker container's IP addresses.