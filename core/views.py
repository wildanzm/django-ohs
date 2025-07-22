from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Employee, Attendance, PPE, PPEDetection
from .forms import EmployeeForm, AttendanceRecordForm
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from django.db.models import Count, OuterRef, Subquery, Prefetch
from calendar import monthrange
import calendar
import cv2
import numpy as np
from ultralytics import YOLO
from django.conf import settings
import os

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Login Berhasil! Selamat datang kembali, {user.username}.")
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

    start_of_today = timezone.make_aware(datetime.combine(today, time.min))
    end_of_today = timezone.make_aware(datetime.combine(today, time.max))

    total_employees = Employee.objects.count()
    
    today_attendances = Attendance.objects.filter(check_in_time__range=(start_of_today, end_of_today))
    
    present_today = today_attendances.filter(status=Attendance.AttendanceStatus.HADIR).count()
    absent_today = today_attendances.exclude(status=Attendance.AttendanceStatus.HADIR).count()

    active_filter = request.GET.get('filter', 'weekly')
    chart_labels, hadir_data, sakit_data, izin_data, tanpa_keterangan_data = [], [], [], [], []

    if active_filter == 'monthly':
        num_days = monthrange(today.year, today.month)[1]
        days_in_month = [date(today.year, today.month, i) for i in range(1, num_days + 1)]
        chart_labels = [day.strftime("%d") for day in days_in_month]
        
        for day in days_in_month:
            start_of_day = timezone.make_aware(datetime.combine(day, time.min))
            end_of_day = timezone.make_aware(datetime.combine(day, time.max))
            attendances = Attendance.objects.filter(check_in_time__range=(start_of_day, end_of_day)).values('status').annotate(count=Count('status'))
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
            
            start_of_day = timezone.make_aware(datetime.combine(day, time.min))
            end_of_day = timezone.make_aware(datetime.combine(day, time.max))
            attendances = Attendance.objects.filter(check_in_time__range=(start_of_day, end_of_day)).values('status').annotate(count=Count('status'))
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
    success_message = "Data karyawan baru berhasil ditambahkan."
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

class AttendanceListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'core/attendance_list.html'
    context_object_name = 'attendance_data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_date_str = self.request.GET.get('filter_date', date.today().strftime('%Y-%m-%d'))
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        start_of_day = timezone.make_aware(datetime.combine(selected_date, time.min))
        end_of_day = timezone.make_aware(datetime.combine(selected_date, time.max))

        all_employees = Employee.objects.all().order_by('full_name')

        attendances_for_day = Attendance.objects.filter(
            check_in_time__range=(start_of_day, end_of_day)
        ).prefetch_related('detected_ppes')

        attendance_map = {att.employee_id: att for att in attendances_for_day}

        final_data = []
        for employee in all_employees:
            attendance_record = attendance_map.get(employee.id, None)
            final_data.append({
                'employee': employee,
                'attendance': attendance_record
            })
        
        context['attendance_data'] = final_data
        context['selected_date'] = selected_date
        context['max_date'] = date.today().strftime('%Y-%m-%d')
        return context

class AttendanceRecordView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Attendance
    form_class = AttendanceRecordForm
    template_name = 'core/attendance_form.html'
    success_message = "Kehadiran berhasil dicatat."

    def get_success_url(self):
        selected_date = self.request.session.get('selected_date', date.today().strftime('%Y-%m-%d'))
        return f"{reverse_lazy('attendance_list')}?filter_date={selected_date}"

    def form_valid(self, form):
        employee = Employee.objects.get(pk=self.kwargs['employee_pk'])
        selected_date_str = self.request.session.get('selected_date', date.today().strftime('%Y-%m-%d'))
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        if Attendance.objects.filter(employee=employee, check_in_time__date=selected_date).exists():
            messages.error(self.request, f"Karyawan {employee.full_name} sudah tercatat absensinya untuk tanggal ini.")
            return redirect(self.get_success_url())

        attendance = form.save(commit=False)
        attendance.employee = employee
        
        if attendance.status == Attendance.AttendanceStatus.HADIR and self.request.FILES.get('image_attendance'):
            try:
                face_proto = os.path.join(settings.BASE_DIR, 'deploy.prototxt.txt')
                face_model = os.path.join(settings.BASE_DIR, 'res10_300x300_ssd_iter_140000.caffemodel')
                face_net = cv2.dnn.readNetFromCaffe(face_proto, face_model)
                yolo_model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'best.pt')
                model_apd = YOLO(yolo_model_path)
                
                ALLOWED_CLASSES = {'Hardhat', 'Mask', 'Safety Vest'}
                TRANSLATION_MAP = {'Hardhat': 'Helm', 'Mask': 'Masker', 'Safety Vest': 'Rompi'}

                image_file = self.request.FILES.get('image_attendance')
                image_bytes = image_file.read()
                np_arr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                h, w = image.shape[:2]
                blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
                face_net.setInput(blob)
                face_detections = face_net.forward()
                for i in range(face_detections.shape[2]):
                    if face_detections[0, 0, i, 2] > 0.7:
                        attendance.body_temperature = round(36.2 + np.random.uniform(-0.5, 1.3), 1)
                        break
                
                results = model_apd(image)[0]
                detected_ppes_english = {model_apd.names[int(box.cls[0])] for box in results.boxes if model_apd.names[int(box.cls[0])] in ALLOWED_CLASSES}
                
                super().form_valid(form)
                for ppe_name_en in detected_ppes_english:
                    ppe_name_id = TRANSLATION_MAP.get(ppe_name_en)
                    if ppe_name_id:
                        ppe_obj, _ = PPE.objects.get_or_create(name=ppe_name_id)
                        PPEDetection.objects.create(attendance=self.object, ppe=ppe_obj)

            except Exception as e:
                messages.error(self.request, f"Gagal memproses gambar: {e}")
                return redirect(self.get_success_url())
        
        else:
            attendance.body_temperature = None
            if not self.request.FILES.get('image_attendance'):
                 attendance.image_attendance = None
            
            super().form_valid(form)
        
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = Employee.objects.get(pk=self.kwargs['employee_pk'])
        context['page_title'] = f"Catat Kehadiran: {employee.full_name}"
        self.request.session['selected_date'] = self.request.GET.get('date', date.today().strftime('%Y-%m-%d'))
        return context

class AttendanceUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Attendance
    form_class = AttendanceRecordForm 
    template_name = 'core/attendance_form.html'
    success_message = "Data absensi berhasil diperbarui."

    def get_success_url(self):
        selected_date = self.object.check_in_time.strftime('%Y-%m-%d')
        return f"{reverse_lazy('attendance_list')}?filter_date={selected_date}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Edit Absensi: {self.object.employee.full_name}"
        return context

class AttendanceDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Attendance
    template_name = 'core/attendance_confirm_delete.html'
    success_message = "Data absensi berhasil dihapus."
    
    def get_success_url(self):
        selected_date = self.object.check_in_time.strftime('%Y-%m-%d')
        return f"{reverse_lazy('attendance_list')}?filter_date={selected_date}"