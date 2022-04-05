from datetime import datetime, timedelta
from django.utils.functional import cached_property
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import *
from django.core.paginator import Paginator
from blog.forms import *
from blog.models import Blog
from base.functions import *
from base.const import *
# Create your views here.

@timer
def blog_post(request,user_id):
    user = User.objects.get(pk=user_id)
    if request.method == "POST":
        form = BlogForm(request.POST)
        blog = form.save(commit=False)
        blog.user = user
        blog.reg_date = timezone.now()
        blog.save()
    return redirect('index')

def dayoffset():
    result = 5 - datetime.now().timetuple()[6]
    if result < 0:
        result = 6-result
    return result-5

def daydelta(a):
    now = datetime.now()
    result:datetime = a
    c = now - result
    return c.days #+ dayoffset()

@timer
def blog_detail(request,blog_id):
    page = request.GET.get('page')
    context={}
    blog = Blog.objects.get(pk=blog_id)
    articles = Article.objects.filter(blog=blog).exclude(status=DELETED,tags__name="과제")
    tag = request.GET.get('hashtag')
    if tag:
        articles = get_hashtag_articles(articles,tag)
    grasses = articles.values('reg_date','update_date').filter(reg_date__gte=datetime.now()-timedelta(days=365))
    articles=articles.exclude(tags__name="과제")
    dates = list(map(lambda x : daydelta(x['reg_date']),grasses))    
    histories = articles.select_related('savehistories').annotate(saved_date = F('savehistories__saved_date')).values('saved_date').filter(saved_date__isnull=False)
    dates += list(map(lambda x : daydelta(x['saved_date']),histories))
    t_d = {}
    for i in dates:
        #1일전 1일전 5일전 6일전 7일전 7일전식으로 모여있음. dict로 카운트해줌.
        t = str(i)
        if not t_d.get(t):
            t_d[str(i)]=1
        else:
            t_d[str(i)]+=1
    t_list=list(t_d.items())
    pages = Paginator(articles.order_by('-reg_date'),21)
    context.update(blog=blog)
    context.update(articles=pages.get_page(page))
    context.update(dates=t_list)
    return render(request,'blog/main.html',context)

#@cached_property
def get_hashtag_articles(articles:QuerySet,name):
    return articles.filter(tags__name=name)
    
    
    # return HashTag.objects.filter(name=name).prefetch_related('articles').annotate(title=F('articles__title'),context=F('articles__context'),pk=F('articles__pk'),status=F('articles__status'),reg_date=F('articles__reg_date'),update_date=F('articles__update_date')).exclude(status=status).values()

@timer
def article_view(request,blog_id,article_id):
    context = {}
    blog = Blog.objects.get(pk=blog_id)
    article = Article.objects.get(pk=article_id)
    if article.status == DELETED:
        messages.warning(request,'삭제된 게시물입니다')
        return redirect('index')
    context.update(article=article)
    context.update(blog=blog)
    context.update(comments=article.comment.filter(parent__isnull=True))
    print(article.comment.all())
    return render(request,'blog/detail_view.html',context)

def article_edit(request,blog_id):
    context={}
    user = request.user
    blog = Blog.objects.get(pk=blog_id)
    context.update(user=user)
    context.update(blog=blog)
    action = request.GET.get('type')
    if request.method=="POST" and blog.user ==user:   
        article_id = request.GET.get('article_id')
        if action =="post":
            form:ArticleForm = ArticleForm(request.POST)
            if form.is_valid():
                article = form.save(commit=False)
                article.user = user
                article.blog = blog
                article.reg_date= timezone.now()
                article.save()
                tags_setter(request,article)
                return JsonResponse({'message':'201','type':'created','article_id':article.pk})
        elif action=="delete":
            article =Article.objects.get(pk=article_id,user=user,blog=blog)
            article.status=DELETED
            article.save()
            #article.delete()
            messages.success(request,"success")
            return redirect('blog:blog',blog_id)
        
        elif action =="update":
            article:Article =Article.objects.get(pk=article_id,user=user,blog=blog)
            form:ArticleForm = ArticleForm(request.POST,instance=article)
            if form.is_valid():
                article=form.save(commit=False)
                article.update_date=timezone.now()
                tags_setter(request,article)  
                return JsonResponse({'message':'201','type':'updated','article_id':article.pk})
            context.update(hashtags = article.tags.all())
            context.update(form=form)
            context.update(article=article)
            test = article.tags.all()
            return render(request,'blog/edit_view.html',context)
        return render(request,'blog/edit_view.html',context)
    messages.warning(request,"권한이없어요")
    return redirect('blog:blog',blog_id)
        
def tags_setter(request,article):
    article.tags.clear()
    tags = tag_joiner(request.POST.get('tags'))
    if tags:
        for i in tags:
            article.tags.add(HashTag.objects.get_or_create(name=i)[0])
    article.save()              
    
def comment_edit(request,blog_id,article_id):
    context = {}
    blog = Blog.objects.get(pk=blog_id)
    article = Article.objects.get(pk=article_id)
    action = request.GET.get('type')
    context.update(blog_id=blog_id)
    context.update(article_id=article_id)
    username = request.POST.get('username')
    password = request.POST.get('password')
    if request.method == "POST":
        if action == "post":    
            form:CommentForm = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                if request.user.is_authenticated:
                    comment.user = request.user
                else:
                    if username and password:
                        comment.username = username
                        comment.password = password
                    else:
                        messages.warning(request,"ID와 비밀번호를 입력해주세요")
                        return redirect('blog:view',blog_id,article_id)
                        
                parent = request.GET.get('parent')
                if parent:
                    print('ihaveparent',parent)
                    parent = Comment.objects.get(pk=parent)
                    comment.parent = parent
                else:
                    print("ihavenoparent")
                comment.article = article
                comment.save()
                print("valid")
        elif action == "delete":
            if request.user.is_authenticated:
                comment = Comment.objects.get(pk=request.GET.get('comment'),user=request.user)
                comment.delete()
            else:
                if username and password:
                    try:
                        comment = Comment.objects.get(username=username,password=password)
                        comment.delete()
                    except:
                        messages.warning(request,"ID와 비밀번호를 확인해주세요")
                        return redirect('blog:view',blog_id,article_id)
                
    return redirect('blog:view',blog_id,article_id)

def todo(request):
    action = request.GET.get('action')
    todo_id = request.GET.get('todo_id')
    if todo_id:
        todo = Todo.objects.get(pk=todo_id)
    if request.method=="POST":
        if action=="post":
            form = TodoForm(request.POST)
            if form.is_valid():                  
                    
                todo = form.save(commit=False)
                todo.user = request.user    
            else:
                messages.warning(request,'내용을 입력해주세요')   
                return redirect(request.META.get('HTTP_REFERER','root'))              
        elif action=="done":
            todo.status = 2
        elif action=="delete":
            todo.status = 1
        todo.save()
    return redirect(request.META.get('HTTP_REFERER','root'))