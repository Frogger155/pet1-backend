from rest_framework import serializers
from .models import CustomUser

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ["id", "username", "password1", "password2"]

    def validate(self, data):
        username_exist = CustomUser.objects.filter(username__iexact=data["username"]).exists()

        if username_exist:
            raise serializers.ValidationError("This username is already taken!")

        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords doesn't match!")        
   
        password = data["password1"]
        data.pop("password1")
        data.pop("password2")
        data["password"] = password

        return data

    def create(self, validated_data):
        new_user = CustomUser.objects.create(username=validated_data["username"])
        new_user.set_password(validated_data["password"])
        new_user.save()

        return new_user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token    