from django import forms
from .models import CustomUser,Post,Comment
from django.contrib.auth.forms import PasswordChangeForm


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    phone = forms.CharField(widget=forms.NumberInput)
    email = forms.EmailField(label='Email', error_messages={'unique': 'This Email is already Exist.'})

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'password','user_img']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email


class EditForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.NumberInput)
    email = forms.EmailField(label='Email', error_messages={'unique': 'This Email is already Exist.'})

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'city','user_img']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email


class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'autocomplete':'off','autofill':"off",'placeholder':'abc12@gmail.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'autocomplete':'off','autofill':"off",'placeholder':'password'
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude=['postby','publish_date']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
