from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(postby=user)
        return queryset


class AllPostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    authentication_classes = []
    permission_classes = []


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token': token})
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        change_password_serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if change_password_serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Change Password Successfully.'}, status=status.HTTP_200_OK)
        return Response({'errors': change_password_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        restlinkserailizer = SendResetLinkSerializer(data=request.data)
        if restlinkserailizer.is_valid():
            return Response({'msg': 'Reset Link is Sent To Your Email.'}, status=status.HTTP_200_OK)
        return Response({'errors': restlinkserailizer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetConfirmPasswordView(APIView):
    def post(self, request, uidb64, token):
        resetserializer = PasswordResetConfirmSerializer(data=request.data, context={'uid': uidb64, 'token': token})
        if resetserializer.is_valid():
            return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
        return Response({'errors': resetserializer.errors}, status=status.HTTP_400_BAD_REQUEST)
