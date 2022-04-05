from django.urls import path
from . import views

app_name = "blog"

urlpatterns =[
    path('<int:user_id>/post/',views.blog_post,name="post_blog"),
    path('<int:blog_id>/detail/',views.blog_detail,name="blog"),
    path("<int:blog_id>/article/<int:article_id>/view",views.article_view,name="view"),
    path("<int:blog_id>/article/edit",views.article_edit,name="edit"),
    path("<int:blog_id>/article/<int:article_id>/comment",views.comment_edit,name="comment"),
    path("todo/",views.todo,name="todo"),
]