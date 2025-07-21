from django.urls import path
from . import views
from .views import EmployeeListView, EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView

urlpatterns = [
    path('dashboard', views.dashboard_view, name='dashboard'),
    
    path('karyawan/', EmployeeListView.as_view(), name='employee_list'),
    path('karyawan/add/', EmployeeCreateView.as_view(), name='employee_add'),
    path('karyawan/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_edit'),
    path('karyawan/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),
    
    path('absensi/', views.attendance_view, name='attendance')
]