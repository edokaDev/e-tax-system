from django.urls import path
from .views import IndexView, DashboardView, logout_view

app_name = 'etax'

urlpatterns = [
    path('', IndexView.as_view(), name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]