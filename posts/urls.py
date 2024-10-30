from django.urls import path
from .views import *

urlpatterns = [
    path('posts/add/', PostCreate.as_view()),
    path('posts/all/', PostsList.as_view()),
    path('posts/new/', PostsNewest.as_view()),
    path('posts/logged-user/', PostsByLoggedUser.as_view()),
    path('posts/most-liked/', PostsMostLiked.as_view()),
    path('posts/<int:pk>/', PostDetail.as_view()),
    path('posts/<int:pk>/delete/', DeletePost.as_view()),
    path('posts/with-tag/<str:tag_name>/', GetPostsWithGivenTag.as_view()),
    path('posts/<int:pk>/like/', PostLike.as_view()),
    path('tags/detail/<str:name>/', TagDetail.as_view()),

]