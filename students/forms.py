from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student, Teacher, Schedule, Assignment, Marks, Attendance, AssignmentSubmission

class StudentRegistrationForm(UserCreationForm):
    roll_number = forms.CharField(max_length=20)
    department = forms.CharField(max_length=100)
    semester = forms.IntegerField()
    phone = forms.CharField(max_length=15)
    division = forms.CharField(max_length=10)
    batch = forms.CharField(max_length=10, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UpdateStudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    roll_number = forms.CharField(max_length=20)
    department = forms.CharField(max_length=100)
    semester = forms.IntegerField()
    phone = forms.CharField(max_length=15)
    division = forms.CharField(max_length=10)
    batch = forms.CharField(max_length=10, required=False)

    class Meta:
        model = Student
        fields = ['roll_number', 'department', 'semester', 'phone', 'division', 'batch']

class TeacherRegistrationForm(UserCreationForm):
    department = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UpdateTeacherForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    department = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = Teacher
        fields = ['department', 'phone']

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['teacher', 'subject', 'class_type', 'division', 'batch', 'day', 'start_time', 'end_time', 'classroom']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Make batch field not required by default
        self.fields['batch'].required = False
        
        # Add onchange event for class_type
        self.fields['class_type'].widget.attrs.update({
            'onchange': 'handleClassTypeChange()'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        class_type = cleaned_data.get('class_type')
        batch = cleaned_data.get('batch')

        if class_type == 'LAB' and not batch:
            self.add_error('batch', 'Batch is required for LAB classes')
        elif class_type != 'LAB' and batch:
            cleaned_data['batch'] = None  # Clear batch if not LAB

        return cleaned_data

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['student', 'subject', 'marks', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class AttendanceForm(forms.ModelForm):
    subject = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, teacher=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            # Get unique subjects taught by this teacher from their schedule
            subjects = Schedule.objects.filter(teacher=teacher).values_list('subject', flat=True).distinct()
            self.fields['subject'].choices = [(subject, subject) for subject in subjects]
            
            # Get students from the teacher's classes
            student_divisions = Schedule.objects.filter(teacher=teacher).values_list('division', flat=True).distinct()
            students = Student.objects.filter(division__in=student_divisions).order_by('division', 'roll_number')
            self.fields['student'].queryset = students

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file']
        widgets = {
            'submission_file': forms.FileInput(attrs={'class': 'form-control'})
        } 