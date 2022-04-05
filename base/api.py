import json
from datetime import datetime, timedelta
from django.db.models import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password

from ninja import NinjaAPI, Schema
from ninja.renderers import BaseRenderer

from base.serializer import converter
from base.const import *

from custommiddle.models import Token
from blog.models import *
from django.db.models import fields

from tasks import send_accounts_find_email


class ConcatSubquery(Subquery):
    """ Concat multiple rows of a subquery with only one column in one cell.
        Subquery must return only one column.
    >>> store_produts = Product.objects.filter(
                                            store=OuterRef('pk')
                                        ).values('name')
    >>> Store.objects.values('name').annotate(
                                            products=ConcatSubquery(store_produts)
                                        )
    <StoreQuerySet [{'name': 'Dog World', 'products': ''}, {'name': 'AXÉ, Ropa Deportiva
    ', 'products': 'Playera con abertura ojal'}, {'name': 'RH Cosmetiques', 'products':
    'Diabecreme,Diabecreme,Diabecreme,Caída Cabello,Intensif,Smooth,Repairing'}...
    """
    template = 'ARRAY_TO_STRING(ARRAY(%(subquery)s), %(separator)s)'
    output_field = fields.CharField()

    def __init__(self, *args, separator=', ', **kwargs):
        self.separator = separator
        super().__init__(*args, separator, **kwargs)

    def as_sql(self, compiler, connection, template=None, **extra_context):
        extra_context['separator'] = '%s'
        sql, sql_params = super().as_sql(compiler, connection, template, **extra_context)
        sql_params = sql_params + (self.separator, )
        return sql, sql_params


class Concat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s%(expressions)s)'

    def __init__(self, expression, distinct=False, **extra):
        super(Concat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            output_field=CharField(),
            **extra)


description = """
# 모의 주식 투자 시뮬레이터 API DOCS\n
### RESULT EX\n
    'json' : {\n
        'system':{\n
            'result' : 'SUCCEED' or 'FAILED'\n
        },\n
        'datas':[\n
            {'data1':'value1'},\n
            {'data2':'value2'},\n
        ],\n
    }\n
    
    CONST:
        SUCCEED = "SUCCEED"
        FAILED = "FAILED"
        NONE = "NONE"

        BUY = 1
        SELL = 2

        NORMAL = 1
        COMPLETE = 2
        CANCELED = 3
"""


class MyRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        if data:
            return json.dumps(converter(data))
        else:
            return json.dumps([])


api = NinjaAPI(description=description, csrf=False, renderer=MyRenderer())


class TokenSchema(Schema):
    token: str = "token"

    def __init__(schema: Schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if schema.dict().get("token"):
            del schema.token


class UserForm(Schema):
    username: str = ""
    password: str = ""


@api.post('signin', url_name="signin")
def signin(request, user: UserForm = None):
    username = user.username.strip()
    password = user.password.strip()
    token = login(username, password)
    print(f"로그인 이벤트 발생 // {token}")
    if token:
        return token
    return HttpResponseForbidden(request)


def login(username, password):
    token = ""
    if username and password:
        user = get_user_model().objects.filter(username=username).first()
        if user and check_password(password, user.password):
            token = Token.get_valid_token(user.pk)
    return token


class UserSignupForm(UserForm):
    email: str = ""


@api.post('signup')
def signup(request, form: UserSignupForm):
    if User.objects.filter(email=form.email).exists():
        return HttpResponseBadRequest("")
    if User.objects.filter(username=form.username).exists():
        return HttpResponseBadRequest("")
    User.objects.create(
        username=form.username,
        email=form.email,
        password=make_password(form.password)
    )
    return HttpResponse('success')


class InfoForm(TokenSchema):
    pass


@api.post('userinfo')
def get_user_info(request, form: InfoForm):
    user = User.objects.filter(pk=request.user.pk).prefetch_related('blog').values(
        'username', 'user_id', 'email', 'blog__id', 'blog__name')
    return user


@api.post('test')
def get_all_user_info(request):
    user = User.objects.all().prefetch_related('blog').values(
        'username', 'user_id', 'email', 'blog__id', 'blog__name')
    return user

# 블로그 start


@api.get('blogs')
def get_blogs(request):
    blog = Blog.objects.all()
    return blog


class BlogNameForm(TokenSchema):
    blog_id: int
    blog_name: str


@api.post('blog/edit')
def post_blog_name_change(request, form: BlogNameForm):
    blog = Blog.objects.filter(user=request.user, pk=form.blog_id)
    try:
        target: Blog = blog.first()
        target.name = form.blog_name
        target.save()
    except:
        pass
    return blog


@api.get('blog/{blog_id}')
def get_blog_by_id(request, blog_id: int):
    return Blog.objects.filter(pk=blog_id)


# 블로그 end


@api.get('articles/random')
def get_random_articles(request, tag: str = ""):
    target = target = Article.objects.annotate(
        taglist=Concat('tags__name')).exclude(tags__name="과제")
    if tag:
        target = target.filter(tags__name__icontains=tag)
    target = target.order_by("?")[:10]
    return target


@api.get('articles/{blog_id}')
def get_articles(request, blog_id, page: int = 1, perPage: int = 10, tagName: str = ""):
    startPage = (page-1)*perPage
    endPage = (page)*perPage
    context = {}
    blog = Blog.objects.get(pk=blog_id)
    articles = Article.objects.filter(blog=blog).exclude(
        status=DELETED, tags__name="과제").order_by('-reg_date')
    articles = articles.annotate(taglist=Concat('tags__name'))
    length = articles.count()
    if tagName:
        articles = get_hashtag_articles(articles, tagName)
    articles = articles.exclude(tags__name="과제").values(
        'id', 'reg_date', 'update_date', 'user_id', 'blog_id', 'title', 'context', 'taglist')
    pages = articles  # [startPage:endPage]
    return pages


@api.get('blogs/{blog_id}/tags')
def get_tags(request, blog_id: int):
    result = HashTag.objects.prefetch_related('articles').annotate(count=Count('articles'), blog_id=F('articles__blog_id'), status=F(
        'articles__status'))
    if blog_id >= 1:
        result = result.filter(blog_id=blog_id)
    result = result.exclude(status=DELETED).values(
        'name', 'count').exclude(name='과제').exclude(name='test').order_by('-count')
    return result


@api.get('article/{article_id}')
def get_article(request, article_id: int):
    article = Article.objects.filter(pk=article_id)
    article = article.annotate(hashtags=Concat('tags__name')).values(
        'id', 'reg_date', 'update_date', 'title', 'context', 'hashtags', 'blog_id')
    try:
        pass
    except:
        article = None
    return article


@api.post('article/{article_id}/delete')
def delete_article(request, article_id: int, form: TokenSchema):
    article = Article.objects.filter(pk=article_id, user=request.user).first()
    if article:
        article.delete()
        return HttpResponse("success")
    else:
        return HttpResponseBadRequest("failed")


class ArticleForm(TokenSchema):
    title: str
    tags: str
    context: str


@api.post("article/{articleId}/edit")
def editArticle(request, articleId: int, form: ArticleForm, action: str = "write"):
    user = request.user
    blog = user.blog.all().first()
    if action == "write":
        article = Article(user=user, blog=blog,
                          title=form.title, context=form.context)
        article.save()
        tags_setter(article, form.tags)
    elif action == "edit":
        article = Article.objects.filter(pk=articleId).first()
        article.title = form.title
        article.context = form.context
        tags_setter(article, form.tags)
        pass
    else:
        article = None
    return Article.objects.filter(pk=article.pk)


@api.get("accounts/find/mail")
def mail_send(request, useremail: str):
    target = User.objects.filter(email=useremail)
    if target:
        result = send_accounts_find_email.delay(useremail)
        if result:
            return {"message": "성공"}
        else:
            return {"message": "실패"}
    else:
        return {"message": "유저가 존재하지 않습니다"}


def tags_setter(article: Article, rawtags: str):
    article.tags.clear()
    tags = tag_joiner(rawtags)
    if tags:
        for i in tags:
            article.tags.add(HashTag.objects.get_or_create(name=i)[0])
    article.save()


def tag_joiner(words: str):
    return ''.join(words.split()).split('#')[1:]


def get_hashtag_articles(articles: QuerySet, name):
    return articles.filter(tags__name=name)
