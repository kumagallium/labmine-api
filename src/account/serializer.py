from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers

from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password

from .models import User, UserManager


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(max_length=32,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(min_length=8, max_length=100,write_only=True)
    confirm_password = serializers.CharField(min_length=8, max_length=100,write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password','confirm_password')

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            password=make_password(validated_data['password']))
        return user

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")
        return attrs
