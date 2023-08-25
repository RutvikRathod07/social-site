from django.contrib import admin
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
              path('admin/', admin.site.urls),
              path('', UserCreateView.as_view(), name='signup'),
              path('login/', LoginView.as_view(), name='login'),
              path('logout/', LogOut.as_view(), name='logout'),
              path('edit_user/<int:pk>', UserUpdateView.as_view(), name='edit_user'),
              path('delete_user/<int:pk>', DeleteUser.as_view(), name='delete_user'),
              path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
              path('password-reset/', PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
              path('password-reset-confirm/<uidb64>/<token>/',PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
              path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
              path('password-reset/complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),
              path('showpost/', ShowPostView.as_view(), name='display_post'),
              path('homepage/', HomePageView.as_view(), name='home_page'),
              path('showallpost/', ShowAllPostView.as_view(), name='display_all_post'),
              path('addpost/', AddPostView.as_view(), name='add_post'),
              path('updatepost/<int:id>', PostUpdateView.as_view()),
              path('deletepost/<int:id>', DeletePostView.as_view()),
              path('likepost/<int:post_id>/', LikePostView.as_view(), name='like_post'),
              path('add-comment', AddCommentView.as_view(), name='add_comment'),
              path('deletecomment/<int:id>', CommentDeleteView.as_view()),
              # extra
              path('search/', SearchPostView.as_view()),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
