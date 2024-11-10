"""Urls.py"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
name='password_reset_complete'),

    path('add_expense/', views.add_expense, name='add_expense'),
    path('manage_categories/', views.manage_categories, name='manage_categories'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('edit_expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('expense-history/', views.expense_history, name='expense_history'),

    path('reports/', views.reports, name='reports'),
    path('reports/download/', views.download_report, name='download_report'),
]
