from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from .models import Student, Teacher, Schedule, Assignment, Marks, Attendance, Activity, AssignmentSubmission, FeeStructure, FeePayment
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import SetPasswordForm
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

# Remove recent activity by customizing admin site
class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Remove LogEntry from admin interface
        for app in app_list:
            if app['app_label'] == 'admin':
                app['models'] = [model for model in app['models'] if model['object_name'] != 'LogEntry']
        return app_list

# Replace the default admin site
admin.site = CustomAdminSite()

# Custom User Admin with password information
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_password_info')
    
    def get_password_info(self, obj):
        if obj.has_usable_password():
            return format_html('<span style="color: green;">Password Set</span>')
        else:
            return format_html('<span style="color: red;">No Password</span>')
    get_password_info.short_description = 'Password Status'

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'roll_number', 'department', 'semester', 'division', 'batch', 'get_email', 'get_password_info')
    search_fields = ('user__first_name', 'user__last_name', 'roll_number', 'department')
    list_filter = ('department', 'semester', 'division', 'batch')
    list_editable = ('department', 'semester', 'division', 'batch')
    change_form_template = 'admin/custom_student_change_form.html'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'roll_number', 'department', 'semester', 'division', 'batch')
        }),
        ('Password Management', {
            'fields': ('get_password_status',),
            'classes': ('collapse',),
            'description': 'Click the Reset Password button below to change the password.'
        }),
    )
    
    readonly_fields = ('get_password_status',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_password_info(self, obj):
        if obj.user.has_usable_password():
            return format_html('<span style="color: green;">Password Set</span>')
        else:
            return format_html('<span style="color: red;">No Password</span>')
    get_password_info.short_description = 'Password Status'
    
    def get_password_status(self, obj):
        if obj.user.has_usable_password():
            return format_html(
                '<div style="padding: 10px; background-color: #e8f5e9; border-radius: 4px;">'
                '<strong>Password Status:</strong> Password is set<br>'
                '<a href="{}" class="button" style="display: inline-block; padding: 5px 10px; '
                'background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; '
                'margin-top: 10px;">Reset Password</a></div>',
                f'reset-password/'
            )
        else:
            return format_html(
                '<div style="padding: 10px; background-color: #ffebee; border-radius: 4px;">'
                '<strong>Password Status:</strong> No password set<br>'
                '<a href="{}" class="button" style="display: inline-block; padding: 5px 10px; '
                'background-color: #f44336; color: white; text-decoration: none; border-radius: 4px; '
                'margin-top: 10px;">Set Password</a></div>',
                f'reset-password/'
            )
    get_password_status.short_description = 'Password Management'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/reset-password/',
                self.admin_site.admin_view(self.reset_password_view),
                name='student-reset-password',
            ),
        ]
        return custom_urls + urls
    
    def reset_password_view(self, request, object_id):
        student = self.get_object(request, object_id)
        user = student.user
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Password for {user.username} has been reset successfully.")
                return HttpResponseRedirect("..")
        else:
            form = SetPasswordForm(user)
        
        context = {
            'title': f'Reset password for {user.username}',
            'form': form,
            'user': user,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request, student),
        }
        return TemplateResponse(request, 'admin/reset_password.html', context)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'department', 'phone', 'get_email', 'get_password_info')
    search_fields = ('user__first_name', 'user__last_name', 'department')
    list_filter = ('department',)
    list_editable = ('department', 'phone')
    change_form_template = 'admin/custom_teacher_change_form.html'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'department', 'phone')
        }),
        ('Password Management', {
            'fields': ('get_password_status',),
            'classes': ('collapse',),
            'description': 'Click the Reset Password button below to change the password.'
        }),
    )
    
    readonly_fields = ('get_password_status',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_password_info(self, obj):
        if obj.user.has_usable_password():
            return format_html('<span style="color: green;">Password Set</span>')
        else:
            return format_html('<span style="color: red;">No Password</span>')
    get_password_info.short_description = 'Password Status'
    
    def get_password_status(self, obj):
        if obj.user.has_usable_password():
            return format_html(
                '<div style="padding: 10px; background-color: #e8f5e9; border-radius: 4px;">'
                '<strong>Password Status:</strong> Password is set<br>'
                '<a href="{}" class="button" style="display: inline-block; padding: 5px 10px; '
                'background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; '
                'margin-top: 10px;">Reset Password</a></div>',
                f'reset-password/'
            )
        else:
            return format_html(
                '<div style="padding: 10px; background-color: #ffebee; border-radius: 4px;">'
                '<strong>Password Status:</strong> No password set<br>'
                '<a href="{}" class="button" style="display: inline-block; padding: 5px 10px; '
                'background-color: #f44336; color: white; text-decoration: none; border-radius: 4px; '
                'margin-top: 10px;">Set Password</a></div>',
                f'reset-password/'
            )
    get_password_status.short_description = 'Password Management'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/reset-password/',
                self.admin_site.admin_view(self.reset_password_view),
                name='teacher-reset-password',
            ),
        ]
        return custom_urls + urls
    
    def reset_password_view(self, request, object_id):
        teacher = self.get_object(request, object_id)
        user = teacher.user
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Password for {user.username} has been reset successfully.")
                return HttpResponseRedirect("..")
        else:
            form = SetPasswordForm(user)
        
        context = {
            'title': f'Reset password for {user.username}',
            'form': form,
            'user': user,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request, teacher),
        }
        return TemplateResponse(request, 'admin/reset_password.html', context)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_name', 'subject', 'class_type', 'division', 'day', 'get_time_slot')
    list_filter = ('teacher', 'class_type', 'day', 'division')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'subject')
    list_editable = ('subject', 'class_type', 'division', 'day')
    
    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name()
    get_teacher_name.short_description = 'Teacher'
    
    def get_time_slot(self, obj):
        return f"{obj.start_time.strftime('%I:%M %p')} - {obj.end_time.strftime('%I:%M %p')}"
    get_time_slot.short_description = 'Time Slot'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_teacher_name', 'due_date', 'get_status')
    list_filter = ('teacher', 'due_date')
    search_fields = ('title', 'teacher__user__first_name', 'teacher__user__last_name')
    list_editable = ('due_date',)
    
    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name()
    get_teacher_name.short_description = 'Teacher'
    
    def get_status(self, obj):
        total = AssignmentSubmission.objects.filter(assignment=obj).count()
        submitted = AssignmentSubmission.objects.filter(assignment=obj, grade__isnull=False).count()
        return f"{submitted}/{total}"
    get_status.short_description = 'Graded'

@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'subject', 'marks', 'date')
    list_filter = ('subject', 'date')
    search_fields = ('student__user__first_name', 'student__last_name', 'subject')
    list_editable = ('marks',)
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'date', 'status')
    list_filter = ('date', 'status')
    search_fields = ('student__user__first_name', 'student__user__last_name')
    list_editable = ('status',)
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student'
    
    def get_status(self, obj):
        color = 'green' if obj.status else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            'Present' if obj.status else 'Absent'
        )
    get_status.short_description = 'Status'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('title', 'description')
    list_editable = ('title', 'description')
    list_display_links = None

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_assignment_title', 'submitted_at', 'grade', 'feedback', 'get_grade_display')
    list_filter = ('assignment', 'submitted_at')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'assignment__title')
    list_editable = ('grade', 'feedback')
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student'
    
    def get_assignment_title(self, obj):
        return obj.assignment.title
    get_assignment_title.short_description = 'Assignment'
    
    def get_grade_display(self, obj):
        if obj.grade is not None:
            return f"{obj.grade}/100"
        return "Not Graded"
    get_grade_display.short_description = 'Grade Display'

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('department', 'semester', 'total_fee', 'academic_year')
    list_filter = ('department', 'semester', 'academic_year')
    search_fields = ('department', 'academic_year')
    list_editable = ('total_fee',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'semester', 'academic_year'),
            'classes': ('wide',)
        }),
        ('Fee Details', {
            'fields': ('total_fee',),
            'classes': ('wide',)
        }),
    )

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'amount', 'payment_date', 'payment_method', 'receipt_number', 'get_remaining_fee')
    list_filter = ('payment_date', 'payment_method')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'receipt_number', 'transaction_id')
    list_editable = ('amount', 'payment_method')
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',),
            'classes': ('wide',)
        }),
        ('Payment Details', {
            'fields': ('amount', 'payment_date', 'payment_method', 'transaction_id', 'receipt_number'),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': ('remarks',),
            'classes': ('wide',)
        }),
    )
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student'
    
    def get_remaining_fee(self, obj):
        try:
            fee_structure = FeeStructure.objects.get(
                department=obj.student.department,
                semester=obj.student.semester
            )
            total_paid = FeePayment.objects.filter(student=obj.student).aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            remaining = fee_structure.total_fee - total_paid
            color = 'green' if remaining <= 0 else 'red'
            return format_html(
                '<span style="color: {};">₹{:.2f}</span>',
                color,
                remaining
            )
        except FeeStructure.DoesNotExist:
            return "Fee structure not defined"
    get_remaining_fee.short_description = 'Remaining Fee'
