from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('karyawan/', views.employee_view, name='employee'),
    path('absensi/', views.attendance_view, name='attendance')
]