from django.db.models import *
from blog.models import Todo

def todolist(request):
    if request.user.is_authenticated:
        todolist = Todo.objects.filter(user=request.user,status=0)
    else:
        todolist=None
    return {'todolist':todolist}
def commentlist(request):
    if request.user.is_authenticated:
        try:
            result = request.user.blog.first().articles.all()
            result= result.prefetch_related('comment').annotate(
                c_context=F("comment__context")
                )
            result = result.filter(c_context__isnull=False,comment__deleted_at__isnull=True)
        except:
            result = None
    else:
        result = None
    return {'commentlist':result}