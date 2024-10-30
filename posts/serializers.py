from rest_framework import serializers
from django.db.models import Count

from .models import Post, Tag, Like
from accounts.models import CustomUser


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Like
        fields = ['author']


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ['name', 'posts_count']


class UpdatePostSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(
         source='contentFileExtension', read_only=True)
    author_name = serializers.CharField(
        source='author.username', read_only=True
    )
    author_id = serializers.CharField(
        source='author.id', read_only=True
    )
    tags = TagSerializer(many=True)

    def validate(self, data):
        if len(data['tags']) == 0:
            raise serializers.ValidationError(
                "Post must contain at least one tag")
        if len(data['tags']) > 10:
            raise serializers.ValidationError(
                f"Exceeded maximum amount of tags (10)")
        if len(data["title"]) < 1 or len(data["title"]) > 200:
            raise serializers.ValidationError(
                f"Title len error (must be between 2 or 200 characters long)"
            )
        return super(UpdatePostSerializer, self).validate(data)
    
    def update(self, instance, validated_data):
        print(instance.title)
        instance.title = validated_data["title"]
        print(instance.title)

        #получим список всех тэгов поста
        instance_tags_list = Tag.objects.filter(post__id=instance.id)
        
        #Сначала проверяем, существует ли отправленный тэг в объекте поста
        #если существует - то ничего делать не нужно, это значит, что пользователь
        #либо не изменял тэг, либо отправил с таким же именем
        #если тэг не существовал в объекте поста, то проверяем, существует ли тэг
        #в целом, во всей БД. Если да - то добавляем пост к этому новому тэгу
        #если тэг не существует в БД, то создаем объект тэга, затем добавляем
        # объект редактируемого поста к созданному тэгу
        # в конце сохраняем получившийся инстанс в БД
        # П.С проверить потом, возможно слишком много query делаю, место для оптимизации? 
        for tag in validated_data["tags"]:

            if tag["name"] in instance_tags_list:
                pass
            try:
                already_existing_tag = Tag.objects.get(name__iexact=tag["name"])
            except Tag.DoesNotExist:
                new_tag = Tag.objects.create(name=tag["name"])
                instance.tags.add(new_tag)
            else:
                instance.tags.add(already_existing_tag)    

        instance.save()        

   

        return instance

    class Meta:
        model = Post
        fields = ['id', 'title', 'author_name', 'author_id', 'content', 'content_type',
                  'tags', 'date_created', 'date_edited']


class PostSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(
        source='contentFileExtension', read_only=True)
    author_name = serializers.CharField(
        source='author.username', read_only=True
    )
    author_id = serializers.CharField(
        source='author.id', read_only=True
    )
    tags = TagSerializer(many=True)
    num_likes = serializers.SerializerMethodField()

    def get_num_likes(self, obj):
        return obj.like_set.count()

    class Meta:
        model = Post
        fields = ['id', 'title', 'author_name', 'author_id', 'content', 'content_type',
                  'tags', 'date_created', 'date_edited', 'num_likes']

    """
    Проверка на количество тэгов в запросе. Если меньше 0 или больше 10,
    то выдаем ошибку.
    Вызываем метод родителя, чтобы проверить остальные данные, прежде чем
    проверять тэги

    """

    def validate(self, data):
        print("Before validation")
        super().validate(data)
        print(f"VALIDATE {data}")
        if len(data["tags"]) == 0:
            raise serializers.ValidationError(
                "Post must contain at least one tag")
        if len(data["tags"]) > 10:
            raise serializers.ValidationError(
                f"Exceeded maximum amount of tags (10)")
        return data

    def create(self, validated_data):
        print(f"VALIDATED DATA: {validated_data}")
        post = Post.objects.create(
            author=CustomUser.objects.get(id=validated_data["user_id"]),
            title=validated_data["title"],
            content=validated_data["content"]
        )
        for tag in validated_data["tags"]:
            print(f"Given tag_name is {tag['name']}")
            try:
                found_tag = Tag.objects.get(name__iexact=tag["name"])
            except Tag.DoesNotExist:
                found_tag = None

            if found_tag is None:
                new_tag = Tag.objects.create(
                    name=tag["name"]
                )
                post.tags.add(new_tag)
            else:
                post.tags.add(found_tag)

        return post
