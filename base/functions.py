from django.contrib.auth import login
from accounts.models import User

from django.contrib.auth.hashers import make_password
def auto_login(cb):
    
    
    def wrap(request,*args, **kwargs):
        try:
            user = User.objects.all()[0]
        except:
            user = User.objects.create(username="sandring",email="gksdjf1690@gmail.com",password=make_password("gksdjf452@"))
            
        login(request,user)
        result = cb(request,*args,**kwargs)
        
        return result
        
    return wrap

from time import time as dt
def timer(cb):
    def wrap(*args,**kwargs):
        
        start = dt()
        
        result = cb(*args,**kwargs)
        
        end = dt()
        print(f"{cb.__name__} : ellapsed {end-start:0.5f}sec")
        return result
    
    return wrap

def tag_joiner(words:str):
    return ''.join(words.split()).split('#')[1:]