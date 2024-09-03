import os, requests

"""
The 'request' inside login IS DIFFERENT from 'requests' which are importing.
"""
def login(request):
    auth = request.authorization
    if not auth:
        return(None, ("Missing credentials", 401)) #Note this is a tuple.
    
    basicAuth= (auth.username, auth.password)
    response = requests.post(  #Will make a POST request to our auth service.
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth
    )
    
    if response.status_code==200:
        return (response.text,None)
    else:
        return (None, (response.text, response.status_code))
    
def register(request):
    auth = request.authorization
    if not auth:
        return ("Missing credentials", 401) #Note this is a tuple.
    
    basicAuth= (auth.username, auth.password)
    response = requests.post(  #Will make a POST request to our auth service.
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/register",
        auth=basicAuth
    )
    return response