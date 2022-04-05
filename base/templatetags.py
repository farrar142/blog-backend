from datetime import datetime, timedelta
from django import template
from django.utils.safestring import mark_safe
from django.core import serializers
from django.db.models import *
import json
from base.const import *
from accounts.models import User
from blog.models import *

register = template.Library()

@register.filter
def get_count(waiting):
    return waiting.count()
    
@register.filter
def show_articles(user):
    result = user.blog.all().first().articles.all()
    return result


@register.filter
def get_tags(blog_id):
    result =  HashTag.objects.prefetch_related('articles').annotate(count=Count('articles'),blog_id = F('articles__blog_id'),status=F('articles__status')).filter(blog_id=blog_id).exclude(status=DELETED).values('name','count').exclude(name='과제').order_by('-count')
    return result
@register.filter
def get_valid_articles(blog):
    return blog.articles.exclude(status=DELETED,tags__name="과제").count()


@register.filter
def authen(blog,user):
    if blog.user == user:
        return True
    else:
        return False
    
@register.filter
def rfirst(a):
    return a[0]

@register.filter
def rsecond(a):
    return a[1]

@register.filter
def reverse_ranges(count):
    return range(count,0,-1)

@register.filter
def ranges(count):
    return range(1,count+1)

@register.filter
def days(a):
    return (a)*7

@register.filter
def weeks(a,b):
    target = datetime.now()#+timedelta(days=1)
    idx = 6- target.timetuple()[6]#day in week
    return 364 - a+b -idx

months =['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
@register.filter
def monthdelta(a):
    count = datetime.now().month-a
    if count >=12:
        count = count-12
    result = months[count]
    return result

@register.filter 
def match(a,b):
    b = b
    for i in range(0,len(b)):
        if str(a) == b[i][0]:
            if b[i][1]<=5:
                return b[i][1]
            else:                
                return 5            
    return 0

@register.filter 
def contribute(a,b):
    b = b
    for i in range(0,len(b)):
        if str(a) == b[i][0]:
            return b[i][1]        
    return 0
@register.filter
def grass_day(a):
    days = ['SAT','FRI','THU','WED','TUE','MON','SUN']
    return days[a-1]
@register.filter
def get_date(a):
    now = datetime.now()+timedelta()
    # return now.strftime('%Y-%m-%d')
    return (now-timedelta(days=a)).strftime('%Y-%m-%d')
"""
현재 3월3일,
3월3일 - 1-6-3일


"""


@register.filter
def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Make sure it's unicode
    # value = unicode(value)

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    # Break into words and remove the last
    words = value.split(' ')[:-1]

    # Join the words and return
    return ' '.join(words) + '...'