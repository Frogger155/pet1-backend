from rest_framework.views import APIView
from .serializers import PostSerializer, TagSerializer
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.db.models import Count

from .models import Post, Tag, Like


"""
Основной функционал

1. CRUD для постов (+-)
2. Отбор постов с определенным тэгом (+)
3. Отбор постов по новизне (+)
4. Отображение числа постов с данным тэгом, например [Мемы про котов 10000 постов] (+)
5. [Опционально] Добавить лайки к постам, сделать view для отбора постов с наибольшим количеством лайков
6. [Опционально] При создании поста проверять, существует ли тэг. Если да, то связывать новый пост с уже 
   созданным тэгом, а не создавать новый (+)

Авторизация

1. Только автор поста или админ может редактировать или удалять пост 
2. Только зарегистрированные пользователи могут создавать посты
3. Только зарегистрированные пользователи могут оставлять лайк
"""

# CRUD
class PostCreate(APIView):
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetail(APIView):
    
    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(data="Post not found", status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        try:
           post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(data="Post not found", status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
           post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(data="Post not found", status=status.HTTP_404_NOT_FOUND)
        
        post.delete()
        return Response(data="Post deleted", status=status.HTTP_204_NO_CONTENT)

class TagDetail(APIView):
    
    def get(self, request, name):
        try:
            tag = Tag.objects.get(name=name)
        except Tag.DoesNotExist:
            return Response(data="Tag not found", status=status.HTTP_400_BAD_REQUEST)
        
        tag_posts_counter = Post.objects.filter(tags__name=name).count()

        tag_detail = {
            "name": name,
            "posts_with_this_tag": tag_posts_counter
        }

        return Response(tag_detail, status=status.HTTP_200_OK)

class GetPostsWithGivenTag(APIView):
    def get(self, request, tag_name):
        try:
            posts_with_given_tag = Post.objects.filter(tags__name=tag_name)
        except posts_with_given_tag == []:
            return Response(data="Posts with that tag not found", status=status.HTTP_404_NOT_FOUND)

        posts_serializer = PostSerializer(posts_with_given_tag, many=True)

        return Response(data=posts_serializer.data, status=status.HTTP_200_OK)    

    
class PostsList(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostsNewest(ListAPIView):
    queryset = Post.objects.all().order_by('-date_created')
    serializer_class = PostSerializer

class PostLike(APIView):
    """
    Если пользователь аутентицифирован и не оставлял лайк, то добавляем к посту лайк.
    Иначе выкидываем соответствующую ошибку
    """
    def get_post(self, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(data="Post not found", status=status.HTTP_404_NOT_FOUND)
        return post
    
    def post(self, request, pk):
        post = self.get_post(pk)
        Like.objects.create(post=post)

        return Response(status=status.HTTP_201_CREATED)
    
    def delete(self, request, pk):
        post = self.get_post(pk)
        like_to_delete = Like.objects.get(post=post)
        Like.objects.delete(like_to_delete)
 

        return Response(status=status.HTTP_204_NO_CONTENT)


class PostsMostLiked(ListAPIView):
    queryset = Post.objects.annotate(num_of_likes=Count('like')).order_by("num_of_likes")
    serializer_class = PostSerializer
 
