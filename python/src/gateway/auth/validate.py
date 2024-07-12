import os, requests

def token(request):
    #Remember this is being used for SUBSEQUENT requests AFTER the client has already authenticated. So the header will have JWT token.
    #We just need to ensure the JWT token is valid
    if not "Authorization" in request.headers:  #means No authorization header
        return (None,("missing credentials", 401))
    
    token = request.headers["Authorization"]
    if not token:  #means token not found
        return (None,("missing credentials", 401))
    
    response = requests.post(  #Send a POST request to our auth_Service
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization":token},
    )
    
    if response.status_code==200:
        return response.txt,None
    else:
        return None, (response.txt, response.status_code)