from django.contrib.auth.decorators import user_passes_test

def student_required(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'student'

def lecturer_required(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'lecturer'

def admin_required(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'
