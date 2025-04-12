from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Student

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

def add_student(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        age = request.POST.get('age', '')
        course = request.POST.get('course', '').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append("Name is required")
        if not age:
            errors.append("Age is required")
        elif not age.isdigit() or int(age) <= 0:
            errors.append("Age must be a positive number")
        if not course:
            errors.append("Course is required")
            
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'students/add.html', {
                'name': name,
                'age': age,
                'course': course
            })
            
        try:
            Student.objects.create(name=name, age=int(age), course=course)
            messages.success(request, "Student added successfully!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error adding student: {str(e)}")
            return render(request, 'students/add.html', {
                'name': name,
                'age': age,
                'course': course
            })
            
    return render(request, 'students/add.html')

def update_student(request, id):
    student = get_object_or_404(Student, id=id)
    
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        age = request.POST.get('age', '')
        course = request.POST.get('course', '').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append("Name is required")
        if not age:
            errors.append("Age is required")
        elif not age.isdigit() or int(age) <= 0:
            errors.append("Age must be a positive number")
        if not course:
            errors.append("Course is required")
            
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'students/update.html', {
                'student': student,
                'name': name,
                'age': age,
                'course': course
            })
            
        try:
            student.name = name
            student.age = int(age)
            student.course = course
            student.save()
            messages.success(request, "Student updated successfully!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error updating student: {str(e)}")
            return render(request, 'students/update.html', {
                'student': student,
                'name': name,
                'age': age,
                'course': course
            })
            
    return render(request, 'students/update.html', {'student': student})

def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    try:
        student.delete()
        messages.success(request, "Student deleted successfully!")
    except Exception as e:
        messages.error(request, f"Error deleting student: {str(e)}")
    return redirect('home')
