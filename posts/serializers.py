from rest_framework import serializers
from django.db.models import Count

from .models import Post, Tag, Like


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Like
        fields = ['author']


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Tag
        fields = ['name']


class PostSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(
        source='contentFileExtension', read_only=True)
    tags = TagSerializer(many=True)
    num_likes = serializers.SerializerMethodField()

    def get_num_likes(self, obj):
        return obj.like_set.count()
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'content_type',
                  'tags', 'date_created', 'date_edited', 'num_likes']

    """
    Проверка на количество тэгов в запросе. Если меньше 0 или больше 10,
    то выдаем ошибку.
    Вызываем метод родителя, чтобы проверить остальные данные, прежде чем
    проверять тэги
    
    """

    def validate(self, data):
        super().validate(data)

        tags = data[tags]
        if len(tags) == 0:
            raise serializers.ValidationError(
                "Post must contain at least one tag")
        if len(tags) > 10:
            raise serializers.ValidationError(
                f"Exceeded maximum amount of tags (10). Given: {len(tags)} tags")

    """Переопределяем метод для создания постов. 
       Проверяем, существует ли тэг. Если да, то 
       связываем пост с существующим тэгом, а не
       создаем кучу одинаковых тэгов.
       
       ЗАМЕТКА:ПЕРЕСМОТРЕТЬ НУЖНО ЛИ ВООБЩЕ ЭТО ДЕЛАТЬ
    """

    def create(self, validated_data):
        tags_list = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in tags_list:
            try:
                found_tag = Tag.objects.get(name__iexact=tag)
            except Tag.DoesNotExist:
                found_tag = None

            if found_tag is None:
                post.tags.add(tag)
            else:
                post.tags.add(found_tag)

        return post
