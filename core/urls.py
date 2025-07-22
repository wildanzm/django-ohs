from django.urls import path
from . import views
from .views import EmployeeListView, EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView
from .views import AttendanceListView, AttendanceRecordView, AttendanceUpdateView, AttendanceDeleteView


urlpatterns = [
    path('dashboard', views.dashboard_view, name='dashboard'),
    
    path('karyawan/', EmployeeListView.as_view(), name='employee_list'),
    path('karyawan/add/', EmployeeCreateView.as_view(), name='employee_add'),
    path('karyawan/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_edit'),
    path('karyawan/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),
    
    path('absensi/', AttendanceListView.as_view(), name='attendance_list'),
    path('absensi/record/<int:employee_pk>/', AttendanceRecordView.as_view(), name='attendance_record'),
    path('absensi/<int:pk>/edit/', AttendanceUpdateView.as_view(), name='attendance_edit'),
]