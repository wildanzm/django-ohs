from django.shortcuts import render, redirect
from django.conf import settings
from .models import Employee, Attendance, PPE, PPEDetection
import os
from datetime import timedelta, date, datetime
from django.db.models import Count
from calendar import monthrange
import calendar
from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import EmployeeForm
from django.contrib.messages.views import SuccessMessageMixin

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'core/employee.html'
    context_object_name = 'employees'
    paginate_by = 10 

class EmployeeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'core/employee_form.html'
    success_url = reverse_lazy('employee_list') 
    success_message = "Data karyawan berhasil ditambahkan."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Tambah Karyawan Baru'
        return context

class EmployeeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'core/employee_form.html'
    success_url = reverse_lazy('employee_list')
    success_message = "Data karyawan berhasil diperbarui." 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Data Karyawan'
        return context

class EmployeeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Employee
    template_name = 'core/employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')
    success_message = "Data karyawan berhasil dihapus."


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Login Berhasil! Selamat datang, {user.username}.")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'admin/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    today = timezone.now().date()
    
    active_filter = request.GET.get('filter', 'weekly')

    total_employees = Employee.objects.count()
    present_today = Attendance.objects.filter(check_in_time__date=today, status=Attendance.AttendanceStatus.HADIR).count()
    absent_today = Attendance.objects.filter(check_in_time__date=today).exclude(status=Attendance.AttendanceStatus.HADIR).count()

    chart_labels = []
    hadir_data = []
    sakit_data = []
    izin_data = []
    tanpa_keterangan_data = []

    if active_filter == 'monthly':
        num_days = monthrange(today.year, today.month)[1]
        days_in_month = [date(today.year, today.month, i) for i in range(1, num_days + 1)]
        
        chart_labels = [day.strftime("%d") for day in days_in_month]
        
        for day in days_in_month:
            attendances = Attendance.objects.filter(check_in_time__date=day).values('status').annotate(count=Count('status'))
            counts = {item['status']: item['count'] for item in attendances}
            
            hadir_data.append(counts.get(Attendance.AttendanceStatus.HADIR, 0))
            sakit_data.append(counts.get(Attendance.AttendanceStatus.SAKIT, 0))
            izin_data.append(counts.get(Attendance.AttendanceStatus.IZIN, 0))
            tanpa_keterangan_data.append(counts.get(Attendance.AttendanceStatus.TANPA_KETERANGAN, 0))

    elif active_filter == 'yearly':
        chart_labels = [calendar.month_abbr[i] for i in range(1, 13)]
        
        for month_num in range(1, 13):
            attendances = Attendance.objects.filter(check_in_time__year=today.year, check_in_time__month=month_num).values('status').annotate(count=Count('status'))
            counts = {item['status']: item['count'] for item in attendances}

            hadir_data.append(counts.get(Attendance.AttendanceStatus.HADIR, 0))
            sakit_data.append(counts.get(Attendance.AttendanceStatus.SAKIT, 0))
            izin_data.append(counts.get(Attendance.AttendanceStatus.IZIN, 0))
            tanpa_keterangan_data.append(counts.get(Attendance.AttendanceStatus.TANPA_KETERANGAN, 0))
            
    else: 
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            chart_labels.append(day.strftime("%b %d"))
            
            attendances = Attendance.objects.filter(check_in_time__date=day).values('status').annotate(count=Count('status'))
            counts = {item['status']: item['count'] for item in attendances}

            hadir_data.append(counts.get(Attendance.AttendanceStatus.HADIR, 0))
            sakit_data.append(counts.get(Attendance.AttendanceStatus.SAKIT, 0))
            izin_data.append(counts.get(Attendance.AttendanceStatus.IZIN, 0))
            tanpa_keterangan_data.append(counts.get(Attendance.AttendanceStatus.TANPA_KETERANGAN, 0))

    context = {
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'chart_labels': chart_labels,
        'hadir_data': hadir_data,
        'sakit_data': sakit_data,
        'izin_data': izin_data,
        'tanpa_keterangan_data': tanpa_keterangan_data,
        'active_filter': active_filter,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def attendance_view(request):
    return render(request, 'core/attendance.html')