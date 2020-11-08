from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, response, decorators
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import Http404
# from .serializers import LogInSerializer, UserSerializer, WorkspaceSerializer, WorkspaceInviteSerializer, WorkspaceInvitePostSerializer, WorkspaceInviteAcceptSerializer, UserProfileSerializer, ChangePasswordSerializer
# from .account_permissions import IsOwnerOrReadOnly
# from .models import Workspace, WorkspaceUser
# from .models import Workspace, WorkspaceUser, WorkspaceInvite

from django.conf import settings
from datetime import datetime, timedelta
import jwt
from django.core.mail import send_mail
from .serializers import UserSerializer, UserProfileSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import update_last_login
from django.utils import timezone


User = get_user_model()

def encoded_reset_token(email, password):
    payload = {
        'email': email,
        'password': password,
        # 'username': email,
        'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS)
    }
    encoded_data = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return  encoded_data.decode('utf-8')

def decode_reset_token(reset_token):
    try:
        decoded_data = jwt.decode(reset_token, settings.JWT_SECRET,
                                  algorithms=[settings.JWT_ALGORITHM])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None  # means expired token
    # return decoded_data['email']
    return decoded_data

class SignupView(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save(is_active=False)
            password = list( serializer.validated_data.items() )[0][1]
            token = encoded_reset_token(serializer.data['email'], password)
            send_mail(
                "Complete Registration With Leaderboard X",
                f"Hi, You're almost done. Click the link below to activate your account. \n \n" \
                f"127.0.0.1:8000/api/v1/account/activate/{token}/  \n" \
                f"This link lasts for only 5 minutes.",
                settings.EMAIL_FROM,
                [serializer.data['email']]
            )

            return response.Response( {"status": 201}, status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

# The only reason why this custom login serializer and the view below was created,
# was for the sake of updating last login by the user, else I would have
# used jwt_views.TokenObtainPairView.as_view() in urls.py straight up.
class TokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        self.user.last_login = timezone.now()
        self.user.save()
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data

class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

class ActivateUserView(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request, activation_code):
        # Decode user token
        if decode_reset_token(activation_code):
            email = decode_reset_token(activation_code)['email']
            password = decode_reset_token(activation_code)['password']

            # If user exists, return error, else create user.
            try:
                user = User.active_now.get(email=email)
                return response.Response({"status": 400, "message": "user already exists"}, status.HTTP_400_BAD_REQUEST)                
            except User.DoesNotExist:
                user = User.objects.create_user(email=email,
                                                password=password,
                                                last_login=timezone.now())

                refresh = RefreshToken.for_user(user)
                data = {
                    "status": 201,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                    }
                return response.Response(data, status.HTTP_201_CREATED)
        return response.Response({"status": 400, "message": "code expired"}, status.HTTP_400_BAD_REQUEST)

class ProfileUserView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthent, IsOwnerOrReadOnly]

    def get_object(self, uuid):
        try:
            user = User.active_now.get(uuid=uuid)
            self.check_object_permissions(self.request, user)
            return user
        except User.DoesNotExist:
            raise Http404

    def get(self, request, uuid):
        user = self.get_object(uuid)
        serializer = UserProfileSerializer(user)
        # data = serializer.data
        data = {
            "message": "ok",
            "data": serializer.data
        }
        return Response(data)


        # serializer = UserProfileSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return response.Response( {"status": 201}, status.HTTP_201_CREATED)
        # return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)