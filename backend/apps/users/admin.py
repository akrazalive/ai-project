from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'preferred_role', 'preferred_location']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('skills', 'preferred_role', 'preferred_location', 'resume_text')}),
    )
