from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'real_name', 'student_id', 'role', 'phone', 'email', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'real_name', 'student_id', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('real_name', 'student_id', 'phone', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('real_name', 'student_id', 'phone', 'role')}),
    )
