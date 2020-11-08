from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # new
from rest_framework_simplejwt.tokens import RefreshToken
from six import text_type
from .models import User, Company
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    model = User

    class Meta:
        model = User
        fields = ('password1', 'password2', 'email', )
        extra_kwargs = {'password1': {'write_only': True}, 'password2': {'write_only': True}}

    def create(self, validated_data):
        data = {
            key: value for key, value in validated_data.items()
            if key not in ('password1', 'password2')
        }
        data['password'] = validated_data['password1']
        return self.Meta.model.objects.create_user(**data)
        
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords must match.')

        validate_password(data['password1'])
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source='uuid')
    id = serializers.CharField(source='uuid')

    class Meta:
        model = User
        fields = ['id', 'fullname', 'username', 'email', 'image']

# from django.contrib.auth.password_validation import validate_password

# class ChangePasswordSerializer(serializers.Serializer):
#     """
#     Serializer for password change endpoint.
#     """
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)

#     def validate_new_password(self, value):
#         validate_password(value)
#         return value
