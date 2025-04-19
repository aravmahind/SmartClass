from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from .models import Student, Teacher, Schedule, Assignment, AssignmentSubmission, Marks, Attendance, Activity, FeeStructure, FeePayment
from .forms import StudentRegistrationForm, TeacherRegistrationForm, AssignmentForm, MarksForm, AttendanceForm, ScheduleForm, AssignmentSubmissionForm, UpdateStudentForm, UpdateTeacherForm
from django.db import models
from django.db.models import Q
import random
import time
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def is_student(user):
    return hasattr(user, 'student')

def is_teacher(user):
    return hasattr(user, 'teacher')

def is_admin(user):
    return user.is_staff

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            elif hasattr(user, 'teacher'):
                return redirect('teacher_dashboard')
            elif hasattr(user, 'student'):
                return redirect('student_dashboard')
            else:
                messages.error(request, 'User profile not found.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'students/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'teacher'):
        return redirect('teacher_dashboard')
    elif hasattr(request.user, 'student'):
        return redirect('student_dashboard')
    else:
        messages.error(request, 'User profile not found.')
        return redirect('login')

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
        today = timezone.now().date()
        today_schedule = Schedule.objects.filter(
            division=student.division,
            day=today.strftime('%A')
        ).filter(
            models.Q(batch=student.batch) | models.Q(batch='ALL') | models.Q(batch=None)
        ).order_by('start_time')

        # Get marks for the student
        marks = Marks.objects.filter(student=student).order_by('-date')

        # Get assignments for the student's subjects
        student_subjects = Schedule.objects.filter(
            division=student.division
        ).filter(
            models.Q(batch=student.batch) | models.Q(batch='ALL') | models.Q(batch=None)
        ).values_list('subject', flat=True).distinct()

        assignments = Assignment.objects.filter(
            teacher__schedule__subject__in=student_subjects
        ).distinct().order_by('-due_date')

        # Get attendance for the student
        attendance = Attendance.objects.filter(student=student).order_by('-date')

        # Get submission details for each assignment
        for assignment in assignments:
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=student
            ).first()
            assignment.submission = submission
            assignment.is_submitted = submission is not None

        context = {
            'student': student,
            'today_schedule': today_schedule,
            'marks': marks,
            'assignments': assignments,
            'attendance': attendance
        }
        return render(request, 'students/student_dashboard.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('login')

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    teacher = request.user.teacher
    today = timezone.now().date()
    
    # Get today's schedule
    today_schedule = Schedule.objects.filter(
        teacher=teacher,
        day=today.strftime('%A')
    ).order_by('start_time')
    
    # Get weekly schedule
    weekly_schedule = Schedule.objects.filter(
        teacher=teacher
    ).order_by('day', 'start_time')
    
    # Get assignments grouped by title
    assignments_by_title = {}
    assignments = Assignment.objects.filter(teacher=teacher).order_by('-due_date')
    
    for assignment in assignments:
        if assignment.title not in assignments_by_title:
            assignments_by_title[assignment.title] = []
        assignments_by_title[assignment.title].append(assignment)
    
    context = {
        'teacher': teacher,
        'today_schedule': today_schedule,
        'weekly_schedule': weekly_schedule,
        'assignments_by_title': assignments_by_title
    }
    return render(request, 'students/teacher_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_assignments = Assignment.objects.count()
    
    # Get all schedules ordered by day and time
    schedules = Schedule.objects.all().order_by('day', 'start_time')
    
    # Get recent activity (last 5 activities)
    recent_activity = Activity.objects.all().order_by('-timestamp')[:5]
    
    # Add success message if schedule was created
    if 'schedule_created' in request.session:
        messages.success(request, 'Schedule created successfully!')
        del request.session['schedule_created']
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_assignments': total_assignments,
        'schedules': schedules,
        'recent_activity': recent_activity
    }
    return render(request, 'students/admin_dashboard.html', context)

@login_required
@user_passes_test(is_teacher)
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user.teacher
            assignment.save()
            messages.success(request, 'Assignment created successfully')
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm()
    
    return render(request, 'students/create_assignment.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def upload_marks(request):
    teacher = request.user.teacher
    
    if request.method == 'POST':
        form = MarksForm(teacher=teacher, data=request.POST)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.teacher = teacher
            marks.save()
            messages.success(request, 'Marks uploaded successfully')
            return redirect('teacher_dashboard')
    else:
        form = MarksForm(teacher=teacher)
    
    return render(request, 'students/upload_marks.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
@csrf_protect
def mark_attendance(request):
    teacher = request.user.teacher
    
    if request.method == 'POST':
        form = AttendanceForm(teacher=teacher, data=request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.teacher = teacher
            attendance.save()
            messages.success(request, 'Attendance marked successfully')
            return redirect('teacher_dashboard')
    else:
        form = AttendanceForm(teacher=teacher)
    
    return render(request, 'students/mark_attendance.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Student.objects.create(
                user=user,
                roll_number=form.cleaned_data['roll_number'],
                department=form.cleaned_data['department'],
                semester=form.cleaned_data['semester'],
                phone=form.cleaned_data['phone'],
                division=form.cleaned_data['division'],
                batch=form.cleaned_data['batch']
            )
            messages.success(request, 'Student registered successfully')
            return redirect('admin_dashboard')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students/register_student.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Teacher.objects.create(
                user=user,
                department=form.cleaned_data['department'],
                phone=form.cleaned_data['phone']
            )
            messages.success(request, 'Teacher registered successfully')
            return redirect('admin_dashboard')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'students/register_teacher.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def create_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            # Add activity log
            Activity.objects.create(
                title='Schedule Created',
                description=f'New schedule created for {schedule.subject} on {schedule.get_day_display()}',
                timestamp=timezone.now()
            )
            # Set session variable for success message
            request.session['schedule_created'] = True
            return redirect('admin_dashboard')
    else:
        form = ScheduleForm()
    
    return render(request, 'students/create_schedule.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def update_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            updated_schedule = form.save()
            # Add activity log
            Activity.objects.create(
                title='Schedule Updated',
                description=f'Schedule updated for {updated_schedule.subject} on {updated_schedule.get_day_display()}',
                timestamp=timezone.now()
            )
            messages.success(request, 'Schedule updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ScheduleForm(instance=schedule)
    
    return render(request, 'students/update_schedule.html', {'form': form, 'schedule': schedule})

@login_required
@user_passes_test(is_admin)
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        # Add activity log before deletion
        Activity.objects.create(
            title='Schedule Deleted',
            description=f'Schedule deleted for {schedule.subject} on {schedule.get_day_display()}',
            timestamp=timezone.now()
        )
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'students/delete_schedule.html', {'schedule': schedule})

def home(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get sort parameter
    sort_by = request.GET.get('sort', 'name')
    
    # Get all students
    students = Student.objects.all()
    
    # Apply search filter if query exists
    if search_query:
        students = students.filter(
            name__icontains=search_query
        ) | students.filter(
            course__icontains=search_query
        )
    
    # Apply sorting
    if sort_by in ['name', 'age', 'course']:
        students = students.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(students, 5)  # Show 5 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'students/home.html', {
        'students': page_obj,
        'search_query': search_query,
        'sort_by': sort_by
    })

@login_required
@user_passes_test(is_student)
def student_schedule(request):
    try:
        student = Student.objects.get(user=request.user)
        # Get schedules for the student's division and batch
        schedules = Schedule.objects.filter(
            division=student.division
        ).filter(
            models.Q(batch=student.batch) | models.Q(batch='ALL') | models.Q(batch=None)
        ).order_by('day', 'start_time')
        
        # Group schedules by day
        schedule_by_day = {}
        for schedule in schedules:
            if schedule.day not in schedule_by_day:
                schedule_by_day[schedule.day] = []
            schedule_by_day[schedule.day].append(schedule)
        
        context = {
            'schedule_by_day': schedule_by_day,
            'student': student
        }
        return render(request, 'students/student_schedule.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('student_dashboard')

@login_required
@user_passes_test(is_student)
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user.student
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = student
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('student_dashboard')
    else:
        form = AssignmentSubmissionForm()
    
    context = {
        'assignment': assignment,
        'form': form
    }
    return render(request, 'students/submit_assignment.html', context)

@login_required
@user_passes_test(is_teacher)
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=request.user.teacher)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    context = {
        'assignment': assignment,
        'submissions': submissions
    }
    return render(request, 'students/view_submissions.html', context)

@login_required
@user_passes_test(is_teacher)
def grade_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        
        if grade:
            submission.grade = grade
            submission.feedback = feedback
            submission.save()
            messages.success(request, 'Submission graded successfully!')
            return redirect('view_submissions', assignment_id=submission.assignment.id)
    
    context = {
        'submission': submission
    }
    return render(request, 'students/grade_submission.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def view_students(request):
    students = Student.objects.all().order_by('department', 'semester', 'division', 'user__first_name')
    return render(request, 'students/view_students.html', {'students': students})

@login_required
@user_passes_test(lambda u: u.is_staff)
def view_teachers(request):
    teachers = Teacher.objects.all().order_by('department', 'user__first_name')
    return render(request, 'students/view_teachers.html', {'teachers': teachers})

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = UpdateStudentForm(request.POST, instance=student)
        if form.is_valid():
            # Update user fields
            student.user.first_name = form.cleaned_data['first_name']
            student.user.last_name = form.cleaned_data['last_name']
            student.user.email = form.cleaned_data['email']
            student.user.save()
            
            # Update student fields
            form.save()
            messages.success(request, 'Student details updated successfully!')
            return redirect('view_students')
    else:
        initial_data = {
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'email': student.user.email,
            'roll_number': student.roll_number,
            'department': student.department,
            'semester': student.semester,
            'phone': student.phone,
            'division': student.division,
            'batch': student.batch
        }
        form = UpdateStudentForm(initial=initial_data, instance=student)
    return render(request, 'students/update_student.html', {'form': form, 'student': student})

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        form = UpdateTeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            # Update user fields
            if form.cleaned_data.get('first_name'):
                teacher.user.first_name = form.cleaned_data['first_name']
            if form.cleaned_data.get('last_name'):
                teacher.user.last_name = form.cleaned_data['last_name']
            if form.cleaned_data.get('email'):
                teacher.user.email = form.cleaned_data['email']
            teacher.user.save()
            
            # Update teacher fields
            form.save()
            messages.success(request, 'Teacher details updated successfully!')
            return redirect('view_teachers')
    else:
        initial_data = {
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'email': teacher.user.email,
            'department': teacher.department,
            'phone': teacher.phone
        }
        form = UpdateTeacherForm(initial=initial_data, instance=teacher)
    return render(request, 'students/update_teacher.html', {'form': form, 'teacher': teacher})

@login_required
@user_passes_test(lambda u: u.is_staff)
def view_student_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendance = Attendance.objects.filter(student=student).order_by('-date')
    marks = Marks.objects.filter(student=student).order_by('-date')
    
    # Get student's subjects from their schedule
    student_subjects = Schedule.objects.filter(
        division=student.division
    ).filter(
        models.Q(batch=student.batch) | models.Q(batch='ALL') | models.Q(batch=None)
    ).values_list('subject', flat=True).distinct()
    
    # Get assignments for the student's subjects
    assignments = Assignment.objects.filter(
        teacher__schedule__subject__in=student_subjects
    ).distinct().order_by('-due_date')
    
    # Get submission details for each assignment
    for assignment in assignments:
        submission = AssignmentSubmission.objects.filter(
            assignment=assignment,
            student=student
        ).first()
        assignment.submission = submission
        assignment.is_submitted = submission is not None
    
    return render(request, 'students/student_details.html', {
        'student': student,
        'attendance': attendance,
        'marks': marks,
        'assignments': assignments
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def view_teacher_details(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    schedules = Schedule.objects.filter(teacher=teacher).order_by('day', 'start_time')
    assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
    return render(request, 'students/teacher_details.html', {
        'teacher': teacher,
        'schedules': schedules,
        'assignments': assignments
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def view_schedules(request):
    schedules = Schedule.objects.all().order_by('day', 'start_time')
    return render(request, 'students/view_schedules.html', {'schedules': schedules})

@login_required
@user_passes_test(is_student)
def student_fee_details(request):
    student = request.user.student
    try:
        fee_structure = FeeStructure.objects.get(
            department=student.department,
            semester=student.semester
        )
        payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
        total_paid = payments.aggregate(total=models.Sum('amount'))['total'] or 0
        remaining_fee = fee_structure.total_fee - total_paid
        
        context = {
            'student': student,
            'fee_structure': fee_structure,
            'payments': payments,
            'total_paid': total_paid,
            'remaining_fee': remaining_fee
        }
        return render(request, 'students/student_fee_details.html', context)
    except FeeStructure.DoesNotExist:
        messages.error(request, 'Fee structure not defined for your department and semester.')
        return redirect('student_dashboard')

@login_required
@user_passes_test(is_teacher)
def view_student_attendance(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    
    context = {
        'student': student,
        'attendance_records': attendance_records
    }
    return render(request, 'students/view_student_attendance.html', context)

@login_required
@user_passes_test(is_teacher)
def view_student_marks(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    marks_records = Marks.objects.filter(student=student).order_by('-date')
    
    context = {
        'student': student,
        'marks_records': marks_records
    }
    return render(request, 'students/view_student_marks.html', context)

@login_required
@user_passes_test(is_teacher)
def view_student_list(request):
    students = Student.objects.all().order_by('department', 'semester', 'division', 'roll_number')
    
    context = {
        'students': students
    }
    return render(request, 'students/view_student_list.html', context)

@login_required
@user_passes_test(is_admin)
def manage_fee_structure(request):
    if request.method == 'POST':
        department = request.POST.get('department')
        semester = request.POST.get('semester')
        total_fee = request.POST.get('total_fee')
        academic_year = request.POST.get('academic_year')
        
        try:
            fee_structure = FeeStructure.objects.get(
                department=department,
                semester=semester,
                academic_year=academic_year
            )
            fee_structure.total_fee = total_fee
            fee_structure.save()
        except FeeStructure.DoesNotExist:
            FeeStructure.objects.create(
                department=department,
                semester=semester,
                total_fee=total_fee,
                academic_year=academic_year
            )
        
        messages.success(request, 'Fee structure updated successfully')
        return redirect('admin_dashboard')
    
    fee_structures = FeeStructure.objects.all().order_by('department', 'semester', 'academic_year')
    return render(request, 'students/manage_fee_structure.html', {'fee_structures': fee_structures})

def generate_unique_receipt_number():
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    receipt_number = f"RCPT-{timestamp}-{random_num}"
    
    # Keep generating until we find a unique one
    while FeePayment.objects.filter(receipt_number=receipt_number).exists():
        random_num = random.randint(1000, 9999)
        receipt_number = f"RCPT-{timestamp}-{random_num}"
    
    return receipt_number

@login_required
@user_passes_test(is_admin)
def record_fee_payment(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')
        remarks = request.POST.get('remarks')
        
        student = get_object_or_404(Student, id=student_id)
        
        # Generate a unique receipt number
        receipt_number = generate_unique_receipt_number()
        
        FeePayment.objects.create(
            student=student,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            receipt_number=receipt_number,
            remarks=remarks
        )
        
        messages.success(request, 'Fee payment recorded successfully')
        return redirect('admin_dashboard')
    
    students = Student.objects.all().order_by('department', 'semester', 'roll_number')
    recent_payments = FeePayment.objects.all().order_by('-payment_date')[:10]  # Get last 10 payments
    
    return render(request, 'students/record_fee_payment.html', {
        'students': students,
        'recent_payments': recent_payments
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'students/change_password.html', {
        'form': form,
        'title': 'Change Password'
    })

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "students/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'SmartClass',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except Exception as e:
                        messages.error(request, "Error sending email. Please try again later.")
                        return redirect('password_reset_request')
                    
                    messages.success(request, 'Password reset instructions have been sent to your email.')
                    return redirect('login')
            else:
                messages.error(request, 'No user found with this email address.')
    else:
        form = PasswordResetForm()
    return render(request, 'students/password_reset_request.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'students/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link was invalid, possibly because it has already been used.')
        return redirect('login')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reset_student_password(request):
    """View for admin to reset a student's password."""
    if request.method == 'POST':
        student_id = request.POST.get('student')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not student_id:
            messages.error(request, 'Please select a student.')
        elif not new_password:
            messages.error(request, 'Please enter a new password.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                student = Student.objects.get(id=student_id)
                user = student.user
                user.set_password(new_password)
                user.save()
                messages.success(request, f'Password for {user.get_full_name()} has been reset successfully.')
                return redirect('admin_dashboard')
            except Student.DoesNotExist:
                messages.error(request, 'Student not found.')
    
    students = Student.objects.all().order_by('user__first_name', 'user__last_name')
    return render(request, 'students/admin_reset_password.html', {
        'students': students,
        'user_type': 'student'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reset_teacher_password(request):
    """View for admin to reset a teacher's password."""
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not teacher_id:
            messages.error(request, 'Please select a teacher.')
        elif not new_password:
            messages.error(request, 'Please enter a new password.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                teacher = Teacher.objects.get(id=teacher_id)
                user = teacher.user
                user.set_password(new_password)
                user.save()
                messages.success(request, f'Password for {user.get_full_name()} has been reset successfully.')
                return redirect('admin_dashboard')
            except Teacher.DoesNotExist:
                messages.error(request, 'Teacher not found.')
    
    teachers = Teacher.objects.all().order_by('user__first_name', 'user__last_name')
    return render(request, 'students/admin_reset_password.html', {
        'teachers': teachers,
        'user_type': 'teacher'
    })
