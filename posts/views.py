from rest_framework.views import APIView
from .serializers import PostSerializer, TagSerializer, UpdatePostSerializer
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count

import json

from .models import Post, Tag, Like
from .permissions import IsPostAuthorOrAdmin

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
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        print(request.user)
        copy = request.data.copy()
        tags_list = copy.getlist("tags")
        copy.pop("tags")
        copy = copy.dict()
        tags_list = [{"name":tag} for tag in tags_list]
        copy["tags"] = tags_list
        print(f"copy is {copy}")
        print(f"tags_list is {tags_list}")
        serializer = PostSerializer(data=copy)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = [IsPostAuthorOrAdmin]
    parser_classes = [FormParser, MultiPartParser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(data="Post not found", status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        print(f"===REQUEST_DATA:  {request.data}")

        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(data="Post not found", status=status.HTTP_404_NOT_FOUND)
        print(self.request)
        tags_dict = [{"name":tag} for tag in request.data.getlist("tags")]
        data = {
            "title": request.data['title'],
            "tags": tags_dict
         }
        print(data)
        serializer = UpdatePostSerializer(instance=post, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePost(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk'


class TagDetail(APIView):
    permission_classes = [AllowAny]

    def get(self, request, name):
        try:
            tag = Tag.objects.get(name=name)
        except Tag.DoesNotExist:
            return Response(data="Tag not found", status=status.HTTP_400_BAD_REQUEST)

        tag_posts_counter = Post.objects.filter(tags__name=name).count()

        tag_detail = {
            "name": name,
            "count": tag_posts_counter
        }

        return Response(tag_detail, status=status.HTTP_200_OK)


class GetPostsWithGivenTag(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tag_name):
        try:
            posts_with_given_tag = Post.objects.filter(tags__name=tag_name)
        except posts_with_given_tag == []:
            return Response(data="Posts with that tag not found", status=status.HTTP_404_NOT_FOUND)

        posts_serializer = PostSerializer(posts_with_given_tag, many=True, context = {'request':request})

        return Response(data=posts_serializer.data, status=status.HTTP_200_OK)


class PostsList(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostsNewest(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Post.objects.all().order_by('-date_created')
    serializer_class = PostSerializer


class PostLike(APIView):
    """
    Если пользователь аутентицифирован и не оставлял лайк, то добавляем к посту лайк.
    Иначе выкидываем соответствующую ошибку
    """
    permission_classes = [IsAuthenticated]

    def get_post(self, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(data="Post not found", status=status.HTTP_404_NOT_FOUND)
        return post

    def post(self, request, pk):
        post = self.get_post(pk)
        try:
            Like.objects.get(author=request.user, post=post)
        except Like.DoesNotExist:
            Like.objects.create(author=request.user, post=post)
            return Response(data=f"Like added for {post} by the {request.user.username}",
                            status=status.HTTP_201_CREATED)
        return Response(data="Like for tihs post by this author already exists",
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_post(pk)
        like_to_delete = Like.objects.get(post=post)
        Like.objects.delete(like_to_delete)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PostsByLoggedUser(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class PostsMostLiked(ListAPIView):
    queryset = Post.objects.annotate(
        num_of_likes=Count('like')).order_by("num_of_likes")
    serializer_class = PostSerializer
