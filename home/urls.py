from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listing/<int:pk>/save/', views.save_listing, name='save_listing'),
    path('listing/<int:pk>/interest/', views.show_interest, name='show_interest'),
    path('listing/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('listing/<int:pk>/update-status/', views.update_listing_status, name='update_listing_status'),
    path('listing/<int:pk>/report/', views.report_listing, name='report_listing'),
    path('listing/<int:pk>/chat/', views.chat_view, name='chat_view'),
    path('listing/<int:pk>/send-message/', views.send_message, name='send_message'),
    path('admin/report/<int:pk>/resolve/', views.admin_resolve_report, name='resolve_report'),
    path('admin/toggle-user/<int:pk>/', views.toggle_user_status, name='toggle_user_status'),
]