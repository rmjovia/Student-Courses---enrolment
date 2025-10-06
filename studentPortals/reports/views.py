from django.shortcuts import render,  get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import student_required, lecturer_required, admin_required
from .models import Student, Grade, Course, CourseReview
from django.contrib.auth import authenticate, login, logout
from .forms import CourseForm


# Create your views here.

def student_list(request):
    students = Student.objects.all()
    return render(request, "reports/student_list.html", {"students": students})



@login_required
@user_passes_test(student_required)
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Courses enrolled via ManyToManyField
    enrolled_courses_m2m = list(student.courses.all())

    # Courses that the student has grades for
    courses_with_grades = list(Course.objects.filter(grade__student=student).distinct())

    # Merge the two lists, remove duplicates
    enrolled_courses = list({c.id: c for c in enrolled_courses_m2m + courses_with_grades}.values())

    # Available courses for enrollment (exclude already enrolled)
    available_courses = Course.objects.exclude(id__in=[c.id for c in enrolled_courses])

    # Handle enroll/unenroll
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        if student in course.students.all():
            course.students.remove(student)
        else:
            course.students.add(student)
        return redirect('student_detail', student_id=student.id)

    # Grades and reviews
    grades = Grade.objects.filter(student=student)

    # Prepare a list for template
    courses_with_reviews = []
    for course in enrolled_courses:
        review = course.reviews.filter(student=student).first()
        courses_with_reviews.append({
            'course': course,
            'review': review
        })

    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses,
        'grades': grades,
        
    }
    return render(request, 'reports/student_detail.html', context)

@login_required
@user_passes_test(student_required)
def course_list(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Courses the student already has grades for
    graded_course_ids = Grade.objects.filter(student=student).values_list('course_id', flat=True)

    # Courses available to enroll (not graded yet)
    available_courses = Course.objects.exclude(id__in=graded_course_ids)

    # Optional search/filter
    query = request.GET.get('q')
    if query:
        available_courses = available_courses.filter(name__icontains=query)

    # Handle enroll/unenroll
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        if student in course.students.all():
            course.students.remove(student)
        else:
            course.students.add(student)
        return redirect('course_list', student_id=student.id)  # back to the same page

    context = {
        'student': student,
        'available_courses': available_courses,
        'query': query or "",
    }
    return render(request, 'reports/course_list.html', context)


def toggle_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = Student.objects.get(user=request.user)
    if student in course.students.all():
        course.students.remove(student)
    else:
        course.students.add(student)
    return redirect('course_list')


@login_required
def add_review(request, course_id):
    student = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    enrolled_courses = student.courses.all()  # all courses student is enrolled in
    reviews = CourseReview.objects.filter(student=student)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Update existing review or create new
        review, created = CourseReview.objects.update_or_create(
            student=student,
            course=course,
            defaults={'rating': rating, 'comment': comment}
        )
        return redirect('student_detail', student_id=student.id)

    return render(request, 'reports/add_review.html', {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'reviews': reviews,
        'selected_course': course  # new
    })

@login_required
@user_passes_test(student_required)
def student_dashboard(request):
    # student-specific actions
    return render(request, 'students/student_detail.html')

@login_required
@user_passes_test(lecturer_required)
def lecturer_dashboard(request):
    lecturer_name = request.user.username  # assuming lecturer name = username
    courses = Course.objects.filter(lecturer=request.user)
    return render(request, 'reports/lecturer_dashboard.html', {'courses': courses})

@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    # Example: admin can manage everything
    students = Student.objects.all()
    courses = Course.objects.all()
    return render(request, 'reports/admin_dashboard.html', {'students': students, 'courses': courses})



@login_required
def login_redirect(request):
    profile = request.user.profile

    if profile.role == 'student':
        # Find the corresponding Student instance
        try:
            student = Student.objects.get(email=request.user.email)
            return redirect('student_detail', student_id=student.id)
        except Student.DoesNotExist:
            # fallback if Student record missing
            return redirect('lecturer_dashboard')
    elif profile.role == 'lecturer':
        return redirect('lecturer_dashboard')
    elif profile.role == 'admin':
        return redirect('admin_dashboard')
    

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lecturer_required)
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Students explicitly enrolled via M2M
    students_from_m2m = list(course.students.all())
    students_from_grades = [grade.student for grade in Grade.objects.filter(course=course)]
    students = list({student.id: student for student in students_from_m2m + students_from_grades}.values())

    # Handle grade submission
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        score = request.POST.get('score')
        student = get_object_or_404(Student, id=student_id)
        grade, created = Grade.objects.get_or_create(student=student, course=course, defaults={'score': score})
        if not created:
            grade.score = score
            grade.save()
        return redirect('course_students', course_id=course.id)

    # Prepare data for template
    students_with_grades = []
    for student in students:
        grade = Grade.objects.filter(student=student, course=course).first()
        students_with_grades.append({'student': student, 'grade': grade})

    return render(request, 'reports/course_students.html', {
        'course': course,
        'students_with_grades': students_with_grades
    })

@login_required
@user_passes_test(lecturer_required)  # Make sure this decorator exists
def update_grade(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, id=student_id)

    # Get or create the grade object
    grade, created = Grade.objects.get_or_create(student=student, course=course)

    if request.method == 'POST':
        score = request.POST.get('score')
        if score:
            grade.score = int(score)
            grade.save()
        # Redirect back to the students list to show updated grade
        return redirect('course_students', course_id=course.id)

    return render(request, 'reports/update_grade.html', {
        'grade': grade,
        'student': student,
        'course': course
    })


@login_required
@user_passes_test(lecturer_required)  # ensures only lecturers can access
def course_reviews(request, course_id):
    # Make sure the course belongs to this lecturer
    course = get_object_or_404(Course, id=course_id, lecturer=request.user)
    
    # Fetch reviews efficiently with related student info
    reviews = CourseReview.objects.filter(course=course).select_related('student')
    
    return render(request, 'reports/course_reviews.html', {'course': course, 'reviews': reviews})


@login_required
@user_passes_test(lecturer_required)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.lecturer = request.user
            course.save()
            return redirect('lecturer_dashboard')
    else:
        form = CourseForm()
    return render(request, 'reports/create_course.html', {'form': form})

@login_required
@user_passes_test(lecturer_required)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, lecturer=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('lecturer_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'reports/edit_course.html', {'form': form, 'course': course})

@login_required
@user_passes_test(student_required)
def submit_review(request, course_id):
    #student = request.user.profile.student  # get the logged-in student
    
    student = Student.objects.get(email=request.user.email)
    course = get_object_or_404(Course, id=course_id)

    # Rating options
    rating_choices = [1, 2, 3, 4, 5]

    # Get existing review if any
    review = CourseReview.objects.filter(student=student, course=course).first()

    if request.method == 'POST':
        rating = int(request.POST['rating'])
        comment = request.POST['comment'].strip()
        if review:
            review.rating = rating
            review.comment = comment
            review.save()
        else:
            CourseReview.objects.create(student=student, course=course, rating=rating, comment=comment)
        return redirect('student_detail', student_id=student.id)

    context = {
        'course': course,
        'review': review,
        'rating_choices': rating_choices,
        'student': student,
    }
    return render(request, 'reports/submit_review.html', context)


@login_required
@user_passes_test(student_required)
def my_courses(request):
    student = request.user.profile
    courses = student.courses.all()  # ManyToManyField
    return render(request, 'reports/my_courses.html', {'courses': courses})