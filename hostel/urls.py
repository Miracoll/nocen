from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get/rrr/', views.getRRR, name='get-rrr'),
    path('remove/rrr/', views.removeRRRInit, name='remove-rrr'),
    path('delet/rrr/<str:reg>/', views.removeRRR, name='delete-rrr'),
    path('clear/rrr/', views.clearStudentTuitionFee, name='clear-rrr'),
    path('student/status/', views.studentHostelStatus, name='student-status'),
    path('student/unallocate/init/', views.unallocateStudentInit, name='student-unallocate-init'),
    path('student/unallocate/<str:reg>/<str:room>/<str:bed>/', views.unallocateStudent, name='student-unallocate'),
    path('student/register/', views.registerStudentInit, name='register-student'),
    path('available/hostel/', views.availableHostel, name='available-hostel'),
    path('allocated/students/', views.allocatedStudents, name='allocated-students'),
    path('add/room/', views.addRoom, name='add-room'),
    path('backup/', views.backUpDb, name='backup'),
]