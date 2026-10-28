from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('', views.ActivityListView.as_view(), name='list'),
    path('<int:pk>/', views.ActivityDetailView.as_view(), name='detail'),
    path('manage/', views.OrganizedActivityListView.as_view(), name='organized_list'),
    path('create/', views.ActivityCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ActivityUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ActivityDeleteView.as_view(), name='delete'),
    path('<int:pk>/register/', views.register_activity, name='register'),
    path('<int:pk>/cancel/', views.cancel_registration, name='cancel'),
    path('<int:pk>/qr/', views.generate_qr, name='generate_qr'),
    path('<int:pk>/upload-checkin/', views.upload_checkin, name='upload_checkin'),
    path('<int:pk>/checkin/<uuid:token>/', views.checkin_view, name='checkin'),
    path('<int:pk>/stats/', views.activity_stats, name='stats'),
    path('<int:pk>/export/csv/', views.export_registrations_csv, name='export_csv'),
    path('<int:pk>/export/excel/', views.export_registrations_excel, name='export_excel'),
]
