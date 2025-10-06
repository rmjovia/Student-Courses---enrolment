from django.contrib import admin

# Register your models here.
from .models import Student, Grade, Course, CourseReview, Profile

admin.site.register(Student)
admin.site.register(Grade)
admin.site.register(Course)
admin.site.register(CourseReview)
admin.site.register(Profile)