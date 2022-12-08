from django.urls import path
from .views import IndexView, DashboardView, MakePaymentView, TCCView, AssetsView, PaymentView, AdminDashboardView, DeleteTccView, ApproveTccView, logout_view

app_name = 'etax'

urlpatterns = [
    path('', IndexView.as_view(), name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('tcc/', TCCView.as_view(), name='tcc'),
    path('assets/', AssetsView.as_view(), name='assets'),
    path('payments/', PaymentView.as_view(), name='payments'),
    path('make-payment/<int:asset_id>/', MakePaymentView.as_view(), name='make-payment'),
    # path('payments/', AssetsView.as_view(), name='payments'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('delete-tcc/<int:tcc_id>/', DeleteTccView.as_view(), name='delete_tcc'),
    path('approve-tcc/<int:tcc_id>/', ApproveTccView.as_view(), name='approve_tcc'),
]