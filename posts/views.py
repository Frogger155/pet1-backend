from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Post
from .serializers import PostSerializer


@csrf_exempt
def posts_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)

        return JsonResponse(serializer.data, safe=False)
    
