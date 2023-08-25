from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .forms import SignUpForm, LoginForm, EditForm, PostForm
from django.views.generic import CreateView, ListView, View,  UpdateView, DeleteView
from .models import CustomUser, Post, Comment, Like
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import CustomPasswordChangeForm
from django.core.paginator import Paginator
from django.core import serializers
from django.db.models import Count
from django.shortcuts import redirect


class UserCreateView(CreateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'user_create.html'
    success_url = reverse_lazy('login')

    def post(self, *args, **kwargs):
        form = SignUpForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(self.request, 'You Have successfully Sign Up...')
            return redirect(reverse_lazy('login'))
        else:
            return render(self.request, 'user_create.html', {'form': form})


class UserUpdateView(UpdateView):

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.success(self.request, 'You have to first log-in to Update User')
            return redirect(reverse_lazy('login'))
        user = CustomUser.objects.get(id=kwargs['pk'])
        form = EditForm(instance=user)
        return render(self.request, 'user_edit.html', {'form': form})

    def post(self, *args, **kwargs):
        user = CustomUser.objects.get(id=kwargs['pk'])
        form = EditForm(self.request.POST, self.request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('display_post'))


class DeleteUser(DeleteView):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.success(self.request, 'You have to first log-in to Delete User')
            return redirect(reverse_lazy('login'))
        user = CustomUser.objects.get(id=kwargs['pk'])
        user.delete()
        return redirect(reverse_lazy('logout'))


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email.lower(), password=password)
        if user is not None:
            login(request, user)
            return redirect('display_post')
        else:
            messages.success(request, 'Please enter valid details ...')
            return redirect('login')


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('login')
    template_name = 'password_change.html'

    def form_valid(self, form):
        logout(self.request)
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)


class LogOut(View):
    def get(self, request):
        if not self.request.user.is_authenticated:
            messages.success(self.request, 'You have to first log-in')
            return redirect(reverse_lazy('login'))
        logout(request)
        return redirect('login')


class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'add_post.html'
    success_url = reverse_lazy('display_post')

    def post(self, *args, **kwargs):
        post = PostForm(self.request.POST, self.request.FILES)
        if post.is_valid():
            post = post.save(commit=False)
            post.postby = self.request.user
            post.save()
            return redirect(reverse_lazy('display_post'))
        else:
            print(post)
            return render(self.request, 'add_post.html', {'form': post})


class ShowAllPostView(ListView):
    model = Post, CustomUser
    template_name = 'home_page.html'
    context_object_name = 'posts'

    def get(self, *args, **kwargs):
        posts = Post.objects.all().order_by('-id').values().annotate(comment_count=Count('comments'))
        for post in posts:
            post['comments'] = Comment.objects.filter(post_id=post['id']).order_by('-id')
            post['postby'] = CustomUser.objects.get(id=post['postby_id'])
            post['like_count'] = Like.objects.filter(post_id=post['id']).count()

        paginator = Paginator(posts, 5, orphans=2)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(self.request, 'show_all_post.html', {'page_obj': page_obj, 'total_posts': posts.count()})


class HomePageView(ListView):
    model = Post, CustomUser
    template_name = 'home_page.html'
    context_object_name = 'posts'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.success(self.request, 'You have to first log-in to view Posts')
            return redirect(reverse_lazy('login'))
        posts = Post.objects.all().order_by('-id').values().annotate(comment_count=Count('comments'))
        for post in posts:
            post['comments'] = Comment.objects.filter(post_id=post['id']).order_by('-id')
            post['postby'] = CustomUser.objects.get(id=post['postby_id'])
            post['is_like'] = Like.objects.filter(user=self.request.user, post_id=post['id']).count()
            post['like_count'] = Like.objects.filter(post_id=post['id']).count()

        user = CustomUser.objects.get(pk=self.request.user.pk)
        paginator = Paginator(posts, 5, orphans=2)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(self.request, 'home_page.html',
                      {'page_obj': page_obj, 'user': user, 'total_posts': posts.count()})


class ShowPostView(ListView):
    model = Post
    template_name = 'show_post.html'
    context_object_name = 'posts'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.success(self.request, 'You have to first log-in to view Posts')
            return redirect(reverse_lazy('login'))
        posts = Post.objects.filter(postby=self.request.user).order_by('-id').values().annotate(comment_count= Count('comments'))
        for post in posts:
            post['comments'] = Comment.objects.filter(post_id=post['id']).order_by('-id')
            post['postby'] = CustomUser.objects.get(id=post['postby_id'])
            post['is_like'] = Like.objects.filter(user=self.request.user, post_id=post['id']).count()
            post['like_count'] = Like.objects.filter(post_id=post['id']).count()
        paginator = Paginator(posts, 5, orphans=2)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(self.request, 'show_post.html', {'page_obj': page_obj, 'total_posts': posts.count()})


class LikePostView(View):
    def post(self, request, post_id):
        data = {'status': 'liked'}
        if request.user.is_authenticated:
            post = get_object_or_404(Post, id=post_id)
            like, created = Like.objects.get_or_create(post=post, user=request.user)
            if not created:
                like.delete()
                data['status'] = 'unliked'
        return JsonResponse(data)


class PostUpdateView(UpdateView):
    def get(self, *args, **kwargs):
        post = Post.objects.get(id=kwargs['id'])
        form = PostForm(instance=post)
        return render(self.request, 'edit_post.html', {'form': form})

    def post(self, *args, **kwargs):
        post = Post.objects.get(id=kwargs['id'])
        form = PostForm(self.request.POST, self.request.FILES, instance=post)
        if form.is_valid():
            print(form)
            form.save()
            return redirect(reverse_lazy('display_post'))


class DeletePostView(DeleteView):
    def get(self, *args, **kwargs):
        previous_url = self.request.META.get('HTTP_REFERER')
        print(previous_url)
        post = Post.objects.get(id=kwargs['id'])
        post.delete()
        return redirect(previous_url)


class SearchPostView(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'page_obj'

    def get(self, *args, **kwargs):

        if not self.request.user.is_authenticated:
            messages.success(self.request, 'You have to first log-in to view Posts')
            return redirect(reverse_lazy('login'))
        query = self.request.GET['query']
        allpost = Post.objects.filter(title__icontains=query).order_by('-id').values().annotate( comment_count= Count('comments'))
        for post in allpost:
            post['comments'] = Comment.objects.filter(post_id=post['id']).order_by('-id')
            post['postby'] = CustomUser.objects.get(id=post['postby_id'])
            post['is_like'] = Like.objects.filter(user=self.request.user, post_id=post['id']).count()
            post['like_count'] = Like.objects.filter(post_id=post['id']).count()
        paginator = Paginator(allpost, 5, orphans=2)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(self.request, 'search.html', {'page_obj': page_obj})


class AddCommentView(CreateView):
    def get(self, request, *args, **kwargs):
        post_id = request.GET.get('postId')
        comment_text = request.GET.get('comment')
        comment = Comment(post_id=post_id, user=request.user, content=comment_text)
        comment.save()
        serialized_comment = serializers.serialize('json', [comment])
        return JsonResponse({'data': serialized_comment}, safe=False)


class CommentDeleteView(DeleteView):
    def get(self, *args, **kwargs):
        previous_url = self.request.META.get('HTTP_REFERER')
        comment = Comment.objects.get(id=kwargs['id'])
        post = Post.objects.get(pk=comment.post.pk)
        comment.delete()
        return redirect(previous_url)
