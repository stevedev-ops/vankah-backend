from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, ProductViewSet, JobCardViewSet,
    YardVehicleViewSet, ToolItemViewSet, ToolRentalViewSet,
    DebtorCustomerViewSet, DebtRecordViewSet, ShiftViewSet,
    StockAuditViewSet, TransactionViewSet, vehicle_history,
    dashboard_stats
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'job-cards', JobCardViewSet, basename='jobcard')
router.register(r'yard-vehicles', YardVehicleViewSet, basename='yardvehicle')
router.register(r'tools', ToolItemViewSet, basename='tool')
router.register(r'tool-rentals', ToolRentalViewSet, basename='toolrental')
router.register(r'debtors', DebtorCustomerViewSet, basename='debtor')
router.register(r'debt-records', DebtRecordViewSet, basename='debtrecord')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'stock-audits', StockAuditViewSet, basename='stockaudit')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('vehicle-history/<str:plate>/', vehicle_history, name='vehicle-history'),
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
]
