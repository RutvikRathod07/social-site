import os
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from blogapp.models import *


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','password','first_name','last_name','city','phone','user_img']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = CustomUser
        fields =['email','password']


class PostSerializer(serializers.ModelSerializer):
    postby_first_name = serializers.CharField(source='postby.first_name', read_only=True)

    class Meta:
        model = Post
        fields = ['id','title','desc','img','publish_date','postby','postby_first_name']


class LikeSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Like
        fields = ['id','post','user','user_first_name']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','password']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255)
    new_password = serializers.CharField(max_length=255)
    new_password1 = serializers.CharField(max_length=255)

    def validate(self, validate_data):
        user = self.context.get('user')
        new_password = validate_data.get('new_password')
        new_password1 = validate_data.get('new_password1')
        if new_password != new_password1:
            raise serializers.ValidationError('Both Password Not Matching.')
        user.set_password(new_password)
        user.save()
        return validate_data


class SendResetLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        user = CustomUser.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        url = f'http://localhost:8000/api/reset_pass/{uid}/{token}/'
        body = f'Click on following link for Reset Your Password {url}.'
        email = EmailMessage(subject='Reset your password', body=body, to=[user.email],
                             from_email=os.environ.get('HOST_USER'))
        email.send()
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)
    password1 = serializers.CharField(max_length=255)

    def validate(self, validate_data):
        try:
            uid = self.context.get('uid')
            token = self.context.get('token')
            password = validate_data.get('password')
            password1 = validate_data.get('password1')
            if password != password1:
                raise serializers.ValidationError('Both Password Not Matching.')
            id = smart_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.filter(id=id).first()
            if not user:
                raise serializers.ValidationError('Uid is Not Valid')
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not valid or Expired')
            user.set_password(password)
            user.save()
            return validate_data
        except DjangoUnicodeDecodeError as identifier:
            raise serializers.ValidationError('Token is not Valid or Expired')