from rest_framework import serializers

from .models import Post

class PostSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source='contentFileExtension')
    class Meta:
        model = Post
        fields = ['title', 'content', 'content_type']
