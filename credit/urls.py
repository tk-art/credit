from django.urls import path
from . import views

urlpatterns = [
    path('', views.top, name='top'),
    path('signup/', views.signup, name='signup'),
    path('login_view/', views.login_view, name='login_view'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
]