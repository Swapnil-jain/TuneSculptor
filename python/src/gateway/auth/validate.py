import os, requests

def token(request):
    #Remember this is being used for SUBSEQUENT requests AFTER the client has already authenticated. So the cookie will have JWT token.
    #We just need to ensure the JWT token is valid
    if not "jwt_token" in request.cookies:  #means no jwt_token
        return (None,("Missing credentials", 401))
    
    token = request.cookies["jwt_token"]
    if not token:  #means token not found
        return (None,("Missing credentials", 401))
    
    response = requests.post(  #Send a POST request to our auth_Service
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        cookies={"jwt_token":token}
    )
    
    if response.status_code==200:
        return response.text,None
    else:
        return None, (response.text, response.status_code)