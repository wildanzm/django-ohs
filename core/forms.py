from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'employee_id_number', 'role']
        labels = {
            'full_name': 'Nama Lengkap',
            'employee_id_number': 'Nomor Induk Pekerja',
            'role': 'Jabatan',
        }