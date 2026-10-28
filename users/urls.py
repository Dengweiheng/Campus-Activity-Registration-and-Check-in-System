from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('my-registrations/', views.my_registrations_view, name='my_registrations'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/users/', views.user_management, name='user_management'),
    path('dashboard/checkin-monitor/', views.checkin_monitor, name='checkin_monitor'),
    path('dashboard/export/csv/', views.export_dashboard_csv, name='export_dashboard_csv'),
    path('dashboard/export/excel/', views.export_dashboard_excel, name='export_dashboard_excel'),
]
