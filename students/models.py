from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Student(models.Model):
    DIVISION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    
    BATCH_CHOICES = [
        ('1', 'Batch 1'),
        ('2', 'Batch 2'),
        ('3', 'Batch 3'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    semester = models.IntegerField()
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES)
    batch = models.CharField(max_length=1, choices=BATCH_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"

class Schedule(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    
    DIVISION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('ALL', 'All Divisions'),
    ]
    
    BATCH_CHOICES = [
        ('1', 'Batch 1'),
        ('2', 'Batch 2'),
        ('3', 'Batch 3'),
        ('ALL', 'All Batches'),
    ]
    
    CLASS_TYPE_CHOICES = [
        ('LECTURE', 'Lecture'),
        ('LAB', 'Laboratory'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.CharField(max_length=50)
    division = models.CharField(max_length=3, choices=DIVISION_CHOICES, default='ALL')
    batch = models.CharField(max_length=3, choices=BATCH_CHOICES, default='ALL')
    class_type = models.CharField(max_length=10, choices=CLASS_TYPE_CHOICES, default='LECTURE')
    
    def __str__(self):
        division_info = f" - Div {self.division}" if self.division != 'ALL' else ""
        batch_info = f" - Batch {self.batch}" if self.batch != 'ALL' else ""
        return f"{self.subject} - {self.day} {self.start_time}-{self.end_time}{division_info}{batch_info}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def has_student_submitted(self, student):
        return AssignmentSubmission.objects.filter(assignment=self, student=student).exists()

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='assignments/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student} - {self.assignment}"

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.marks}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.BooleanField(default=False)  # True for present, False for absent
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, null=True, blank=True)  # Make subject field nullable
    
    def __str__(self):
        return f"{self.student} - {self.subject or 'No Subject'} - {self.date} - {'Present' if self.status else 'Absent'}"

class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-timestamp']

class FeeStructure(models.Model):
    department = models.CharField(max_length=100)
    semester = models.IntegerField()
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.department} - Semester {self.semester} - {self.academic_year}"
    
    class Meta:
        unique_together = ('department', 'semester', 'academic_year')

class FeePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
        ('UPI', 'UPI'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student} - {self.amount} - {self.payment_date}"
    
    class Meta:
        ordering = ['-payment_date']
