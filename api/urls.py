from django.urls import path, re_path, include 
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_swagger.views import get_swagger_view
from rest_framework_simplejwt import views as jwt_views
from account import views

VER_ = 'v1'
account = 'account'

urlpatterns = [
	# account
	path(f'{VER_}/{account}/token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(f'{VER_}/{account}/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path(f'{VER_}/{account}/signup/', views.SignupView.as_view(), name='signup'),
    path(f'{VER_}/{account}/activate/<str:activation_code>/', views.ActivateUserView.as_view(), name='activate'),
    path(f'{VER_}/{account}/profile/<uuid:uuid>/', views.ProfileUserView.as_view(), name='profile'),


 	# path('api/signup/', views.registration, name='signup'),
]