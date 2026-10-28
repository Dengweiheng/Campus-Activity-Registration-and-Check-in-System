from django.contrib import admin
from .models import Activity, Registration, CheckIn


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_time', 'reg_deadline', 'current_participants', 'max_participants', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at', 'current_participants', 'qr_token')
    date_hierarchy = 'start_time'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('activity', 'user', 'registration_time', 'status')
    list_filter = ('status', 'registration_time')
    search_fields = ('activity__title', 'user__username', 'user__real_name')


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_activity', 'check_in_time', 'status', 'ip_address')
    list_filter = ('status', 'check_in_time')
    search_fields = ('registration__user__username', 'registration__activity__title')

    def get_user(self, obj):
        return obj.registration.user.username
    get_user.short_description = '用户'

    def get_activity(self, obj):
        return obj.registration.activity.title
    get_activity.short_description = '活动'
