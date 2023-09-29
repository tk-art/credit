from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.top, name='top'),
    path('signup/', views.signup, name='signup'),
    path('login_view/', views.login_view, name='login_view'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('post/', views.post, name='post'),
    path('get_like_status/', views.get_like_status, name='get_like_status'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('follow/<int:user_id>/', views.follow, name='follow'),
    path('get_follow_status/<int:user_id>/', views.get_follow_status, name='get_follow_status'),
    path('evidence/', views.evidence, name='evidence'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete_evidence/<int:post_id>/', views.delete_evidence, name='delete_evidence'),
    path('evidence_detail/<int:evidence_id>/', views.evidence_detail, name='evidence_detail'),
    path('submit_rating/<int:evidence_id>/', views.submit_rating, name='submit_rating'),
    path('get_star_status/', views.get_star_status, name='get_star_status'),
    path('notification/', views.notification, name='notification'),
    path('api/notifications/check/', views.check_new_notifications, name='check_new_notifications'),
    path('search/', views.search, name='search'),
    path('search_results/', views.search_results, name='search_results'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)