from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.authtoken import views


router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='CustomUser'),
router.register('posts', PostViewSet, basename='posts'),
router.register('allposts', AllPostViewSet, basename='posts'),
router.register('likes', LikeViewSet, basename='likes'),
router.register('comments', CommentViewSet, basename='comments'),

urlpatterns = [
    path('', include(router.urls)),
    path('user_login/', LoginAPIView.as_view(), name='user_login'),
    path('change_pass/', ChangePasswordView.as_view(), name='change_pass'),
    path('reset_pass/', ResetPasswordView.as_view(), name='reset_pass'),
    path('reset_pass/<uidb64>/<token>/', ResetConfirmPasswordView.as_view()),
    path('gettoken/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refreshtoken/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verifytoken/', TokenVerifyView.as_view(), name='token_verify'),
    path('api-token-auth/', views.obtain_auth_token),
]
