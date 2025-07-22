from django import forms
from .models import Employee, Attendance

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'employee_id_number', 'role']
        labels = {
            'full_name': 'Nama Lengkap',
            'employee_id_number': 'Nomor Induk Pekerja',
            'role': 'Jabatan',
        }
        
class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'image_attendance']
        labels = {
            'status': 'Status Kehadiran',
            'image_attendance': 'Upload Foto Bukti (jika Hadir)',
        }
        widgets = {
            'status': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-orange-500 focus:border-orange-500 block w-full p-2.5'
            }),
            'image_attendance': forms.FileInput(attrs={'class': 'hidden'}),
        }