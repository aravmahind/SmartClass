from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),
    path('student/fee-details/', views.student_fee_details, name='student_fee_details'),
    path('student/change-password/', views.change_password, name='change_password'),
    
    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/create-assignment/', views.create_assignment, name='create_assignment'),
    path('teacher/upload-marks/', views.upload_marks, name='upload_marks'),
    path('teacher/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('teacher/view-submissions/<int:assignment_id>/', views.view_submissions, name='view_submissions'),
    path('teacher/grade-submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('teacher/students/', views.view_student_list, name='view_student_list'),
    path('teacher/student/<int:student_id>/attendance/', views.view_student_attendance, name='view_student_attendance'),
    path('teacher/student/<int:student_id>/marks/', views.view_student_marks, name='view_student_marks'),
    path('teacher/change-password/', views.change_password, name='teacher_change_password'),
    
    # Admin URLs (changed from admin/ to system-admin/)
    path('system-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('system-admin/register-student/', views.register_student, name='register_student'),
    path('system-admin/register-teacher/', views.register_teacher, name='register_teacher'),
    path('system-admin/create-schedule/', views.create_schedule, name='create_schedule'),
    path('system-admin/update-schedule/<int:schedule_id>/', views.update_schedule, name='update_schedule'),
    path('system-admin/delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('system-admin/view-schedules/', views.view_schedules, name='view_schedules'),
    
    path('system-admin/students/', views.view_students, name='view_students'),
    path('system-admin/teachers/', views.view_teachers, name='view_teachers'),
    path('system-admin/update-student/<int:student_id>/', views.update_student, name='update_student'),
    path('system-admin/update-teacher/<int:teacher_id>/', views.update_teacher, name='update_teacher'),
    path('system-admin/student/<int:student_id>/', views.view_student_details, name='view_student_details'),
    path('system-admin/teacher/<int:teacher_id>/', views.view_teacher_details, name='view_teacher_details'),
    
    path('system-admin/fee-structure/', views.manage_fee_structure, name='manage_fee_structure'),
    path('system-admin/record-payment/', views.record_fee_payment, name='record_fee_payment'),
    
    path('forgot-password/', views.password_reset_request, name='password_reset_request'),
    path('reset-password-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    path('system-admin/reset-student-password/', views.admin_reset_student_password, name='admin_reset_student_password'),
    path('system-admin/reset-teacher-password/', views.admin_reset_teacher_password, name='admin_reset_teacher_password'),
    
    path('submit-assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
]
