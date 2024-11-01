from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from .serializers import CustomUserSerializer
from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .permissions import IsUserAccountOwnerOrAdmin

class UserCreate(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data="User created!")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class UserDelete(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = (IsUserAccountOwnerOrAdmin,)

    def delete(self, request, pk):
        try:
            user_to_delete = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="User not found!")
        
        self.check_object_permissions(self.request, user_to_delete)
        user_to_delete.delete()

        return Response(status=status.HTTP_204_NO_CONTENT, data="User deleted!")
    
