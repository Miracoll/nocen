from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginForm.as_view(), name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('user/add/', views.addUser, name='add-user'),
    path('user/manage/', views.manageUser, name='manage-user'),
    path('user/disable/<str:user>/', views.disableUser, name='disable-user'),
    path('user/enable/<str:user>/', views.enableUser, name='enable-user'),
    path('user/password/change/', views.changePassword, name='change-password'),
    path('start/session/', views.startNewSession, name='start-new-session'),
]