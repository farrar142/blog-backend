from django.shortcuts import redirect, render
from django.contrib import messages
from base.functions import auto_login
from blog.models import Blog
from base.functions import timer
@timer#
def index(request):
    blogs = Blog.objects.all()
    context={"blogs":blogs}
    if request.user.is_authenticated:
        if request.user.blog.all().exists():
            context.update(blog=Blog.objects.get(user=request.user))
    return render(request,'index.html',context)
