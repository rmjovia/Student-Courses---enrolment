from django.urls import path
from. import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    # Login page
    path('login/', auth_views.LoginView.as_view(template_name='reports/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    #path('', views.student_list, name='student_list'),#
    path ('<int:student_id>/', views.student_detail, name='student_detail'),
    path('<int:student_id>/courses/', views.course_list, name='course_list'),
    path('<int:course_id>/', views.toggle_enrollment, name='toggle_enrollment'),
    path('<int:course_id>/', views.add_review, name='add_review'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/lecturer/course/<int:course_id>/reviews/', views.course_reviews, name='course_reviews'),
    path('dashboard/lecturer/course/<int:course_id>/students/', views.course_students, name='course_students'),
    path('dashboard/lecturer/course/<int:course_id>/grade/<int:student_id>/', views.update_grade, name='update_grade'),
    path('dashboard/lecturer/course/create/', views.create_course, name='create_course'),
    path('dashboard/lecturer/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('reports/courses/<int:course_id>/review/', views.submit_review, name='submit_review'),
    path('<int:student_id>/courses/', views.my_courses, name='my_courses'),
    path('reports/courses/<int:course_id>/add_review', views.add_review, name='add_review'),

    path('logout/', views.logout_view, name='logout'),

    # Generic redirect after login
    path('dashboard/', views.login_redirect, name='login_redirect'),
]