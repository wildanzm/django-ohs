from django.db import models

# Create your models here.
class Employee(models.Model):
    full_name = models.CharField(max_length=255)
    employee_id_number = models.CharField(max_length=50, unique=True, help_text="Unique identifier for the employee")
    role = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id_number})"

class PPE(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Hardhat, Mask, Safety Vest")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    class AttendanceStatus(models.TextChoices):
        HADIR = 'Hadir', 'Hadir'
        IZIN = 'Izin', 'Izin'
        SAKIT = 'Sakit', 'Sakit'
        TANPA_KETERANGAN = 'Alfa', 'Alfa'
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    check_in_time = models.DateTimeField(auto_now_add=True)
    body_temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, help_text="Temperature in Celsius")
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices, default=AttendanceStatus.TANPA_KETERANGAN, help_text="Status of attendance")
    image_attendance = models.ImageField(upload_to='attendance_image/', null=True, blank=True, help_text="Path to the photo taken during check-in")
    detected_ppes = models.ManyToManyField(PPE, through='PPEDetection')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance for {self.employee.full_name} at {self.check_in_time.strftime('%Y-%m-%d %H:%M')}"

class PPEDetection(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    ppe = models.ForeignKey(PPE, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attendance', 'ppe')

    def __str__(self):
        return f"{self.ppe.name} detected for {self.attendance.id}"