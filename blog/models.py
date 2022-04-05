from django.db import models
from django.urls import reverse
from accounts.models import User
from base.models import *


class Blog(TimeMixin):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blog')
    name = models.CharField('블로그이름',max_length=50)
# Create your models here.
    
class HashTag(models.Model):
    name = models.CharField('해시태그',max_length=20)
    
class Article(TimeMixin):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='articles')
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,related_name='articles')
    title = models.CharField('제목',max_length=50)
    context = models.TextField('내용')
    image = models.ImageField('이미지',upload_to="article/img/%Y/%m/%d",blank=True,null=True)
    tags = models.ManyToManyField(HashTag,related_name="articles",blank=True)
    status = models.SmallIntegerField('상태',default=0,null=True,blank=True)
    @classmethod
    def get_articles(cls,**kwargs):
        result = cls.objects.filter()
        return result
    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)
        SaveHistory.objects.create(article=self)
    def __str__(self):
        return self.title
    @property
    def get_absolute_url(self):
        return reverse('blog:view',kwargs={'blog_id':self.blog_id,'article_id':self.pk})
class SaveHistory(models.Model):
    saved_date = models.DateTimeField(auto_now=True)
    article = models.ForeignKey(Article,on_delete=models.CASCADE,related_name='savehistories')
class Comment(TimeMixin):
    username = models.CharField('게시자',max_length=20,null=True,blank=True)
    password = models.CharField('비밀번호', max_length=128,null=True,blank=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,related_name='childs',null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comment',null=True,blank=True)
    article = models.ForeignKey(Article,on_delete=models.CASCADE,related_name="comment")
    context = models.TextField('내용')
    
    @property
    def get_absolute_url(self):
        return reverse('blog:view',kwargs={'blog_id':self.article.blog_id,'article_id':self.article_id})
class Todo(TimeMixin):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='todo')
    context = models.CharField('할일',max_length=50)