from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('skills/', views.manage_skills, name='manage_skills'),

    path(
        'skills/remove/<int:skill_id>/',
        views.remove_skill,
        name='remove_skill'
    ),

    path(
        'request/<int:student_id>/<int:skill_id>/',
        views.send_learning_request,
        name='send_learning_request'
    ),

    path('requests/', views.requests, name='requests'),

    path(
        'request/<int:request_id>/accept/',
        views.accept_request,
        name='accept_request'
    ),

    path(
        'request/<int:request_id>/reject/',
        views.reject_request,
        name='reject_request'
    ),

    path(
        'notification/<int:notification_id>/read/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

    path(
        'review/<int:student_id>/',
        views.submit_review,
        name='submit_review'
    ),

    path('logout/', views.logout_view, name='logout'),
]