from django.urls import path, include
from .views import SignUpView, LoginView, profile_update, profile_two
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', profile_update, name='profile'),
    path('profile2/', profile_two, name='profile2'),
]