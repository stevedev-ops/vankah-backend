from django.contrib import admin
from .models import (
    UserProfile, Product, JobCard, LaborItem, JobPartItem,
    YardVehicle, ToolItem, ToolRental, DebtorCustomer,
    DebtRecord, Shift, StockAudit, StockAuditItem, Transaction
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'title', 'pin')
    search_fields = ('name', 'title')
    list_filter = ('role',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'stock_qty', 'buying_price', 'selling_price', 'location')
    search_fields = ('name', 'sku', 'imei_or_serial', 'location')
    list_filter = ('category',)

class LaborItemInline(admin.TabularInline):
    model = LaborItem
    extra = 1

class JobPartItemInline(admin.TabularInline):
    model = JobPartItem
    extra = 1

@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = ('job_no', 'car_reg_no', 'car_make_model', 'customer_name', 'status', 'advance_deposit', 'created_at')
    search_fields = ('job_no', 'car_reg_no', 'customer_name', 'customer_phone')
    list_filter = ('status',)
    inlines = [LaborItemInline, JobPartItemInline]

@admin.register(YardVehicle)
class YardVehicleAdmin(admin.ModelAdmin):
    list_display = ('car_reg_no', 'customer_name', 'bay_number', 'arrival_date', 'paid_amount', 'is_cleared', 'gate_pass_no')
    search_fields = ('car_reg_no', 'customer_name', 'customer_phone', 'gate_pass_no')
    list_filter = ('is_cleared',)

@admin.register(ToolItem)
class ToolItemAdmin(admin.ModelAdmin):
    list_display = ('tool_code', 'name', 'category', 'status', 'daily_rate', 'security_deposit')
    search_fields = ('tool_code', 'name')
    list_filter = ('category', 'status')

@admin.register(ToolRental)
class ToolRentalAdmin(admin.ModelAdmin):
    list_display = ('tool_code', 'tool_name', 'hirer_name', 'hirer_phone', 'status', 'daily_rate', 'total_hire_fee', 'date_taken')
    search_fields = ('tool_code', 'tool_name', 'hirer_name', 'hirer_phone', 'hirer_id_number')
    list_filter = ('status', 'payment_method')

@admin.register(DebtorCustomer)
class DebtorCustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'business_or_car_reg', 'credit_limit', 'current_balance', 'created_at')
    search_fields = ('name', 'phone', 'business_or_car_reg')

@admin.register(DebtRecord)
class DebtRecordAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'type', 'amount', 'reference_no', 'date', 'cashier_name')
    search_fields = ('customer_name', 'reference_no')
    list_filter = ('type', 'payment_method')

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('cashier_name', 'status', 'start_time', 'end_time', 'opening_float', 'total_cash_expected', 'total_mpesa_expected', 'discrepancy')
    list_filter = ('status',)

class StockAuditItemInline(admin.TabularInline):
    model = StockAuditItem
    extra = 1

@admin.register(StockAudit)
class StockAuditAdmin(admin.ModelAdmin):
    list_display = ('audit_date', 'conducted_by', 'total_variance_value_kes', 'status')
    list_filter = ('status',)
    inlines = [StockAuditItemInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_no', 'type', 'gross_amount', 'profit_amount', 'payment_method', 'date', 'cashier_name')
    search_fields = ('reference_no', 'description', 'cashier_name', 'mpesa_ref')
    list_filter = ('type', 'payment_method')
