import uuid
from django.db import models
from django.utils import timezone

def generate_uuid():
    return str(uuid.uuid4())

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Owner / Manager'),
        ('STAFF', 'Workshop Staff / Cashier'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STAFF')
    title = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.name} ({self.role})'


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Body Parts', 'Body Parts'),
        ('Electrical', 'Electrical'),
        ('Engine & Transmission', 'Engine & Transmission'),
        ('Consumables & Oils', 'Consumables & Oils'),
        ('Tools & Accessories', 'Tools & Accessories'),
        ('Custom Fabrication', 'Custom Fabrication'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    imei_or_serial = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    buying_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_qty = models.IntegerField(default=0)
    min_alert_qty = models.IntegerField(default=1)
    location = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.sku}) - Qty: {self.stock_qty}'


class JobCard(models.Model):
    STATUS_CHOICES = (
        ('Intake', 'Intake'),
        ('In Progress', 'In Progress'),
        ('Waiting Parts', 'Waiting Parts'),
        ('Ready', 'Ready'),
        ('Delivered', 'Delivered'),
    )
    PAYMENT_CHOICES = (
        ('Mpesa', 'Mpesa'),
        ('Cash', 'Cash'),
        ('Split', 'Split'),
        ('Credit', 'Credit'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    job_no = models.CharField(max_length=50, unique=True, db_index=True)
    car_reg_no = models.CharField(max_length=50, db_index=True)
    car_make_model = models.CharField(max_length=150)
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Intake')
    advance_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    mpesa_ref = models.CharField(max_length=100, blank=True, null=True)
    mpesa_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.job_no} - {self.car_reg_no} ({self.customer_name})'


class LaborItem(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    job_card = models.ForeignKey(JobCard, related_name='labor_items', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    description = models.TextField()
    mechanic_name = models.CharField(max_length=150)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.type}: {self.description} ({self.mechanic_name})'


class JobPartItem(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    job_card = models.ForeignKey(JobCard, related_name='parts', on_delete=models.CASCADE)
    part_id = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_outside_purchase = models.BooleanField(default=False)
    vendor_name = models.CharField(max_length=200, blank=True, null=True)
    receipt_no = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.name} x {self.quantity}'


class YardVehicle(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    car_reg_no = models.CharField(max_length=50, db_index=True)
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=50)
    bay_number = models.CharField(max_length=100)
    arrival_date = models.DateTimeField(default=timezone.now)
    weekly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=5000)
    storage_penalty_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=500)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    is_cleared = models.BooleanField(default=False)
    gate_pass_no = models.CharField(max_length=100, blank=True, null=True)
    cleared_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.car_reg_no} - Bay: {self.bay_number} ({self.customer_name})'


class ToolItem(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Maintenance', 'Maintenance'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    tool_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Available')
    condition_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'[{self.tool_code}] {self.name} - {self.status}'


class ToolRental(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    tool_id = models.CharField(max_length=64)
    tool_name = models.CharField(max_length=255)
    tool_code = models.CharField(max_length=50)
    hirer_name = models.CharField(max_length=150)
    hirer_phone = models.CharField(max_length=50)
    hirer_id_number = models.CharField(max_length=50)
    date_taken = models.DateTimeField(default=timezone.now)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_hire_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    damage_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_refunded = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')
    payment_method = models.CharField(max_length=20, default='Mpesa')
    mpesa_ref = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.tool_name} -> {self.hirer_name} ({self.status})'


class DebtorCustomer(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    business_or_car_reg = models.CharField(max_length=200)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.name} - Balance: KES {self.current_balance}'


class DebtRecord(models.Model):
    TYPE_CHOICES = (
        ('CREDIT_PURCHASE', 'Credit Purchase'),
        ('DEBT_REPAYMENT', 'Debt Repayment'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    customer_id = models.CharField(max_length=64, db_index=True)
    customer_name = models.CharField(max_length=200)
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference_no = models.CharField(max_length=100)
    description = models.TextField()
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    mpesa_ref = models.CharField(max_length=100, blank=True, null=True)
    cashier_name = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.type} - {self.customer_name}: KES {self.amount}'


class Shift(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    cashier_name = models.CharField(max_length=150)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    opening_float = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_cash_actual = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_cash_expected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_mpesa_expected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discrepancy = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Shift ({self.cashier_name}) - {self.status}'


class StockAudit(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Approved', 'Approved'),
    )
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    audit_date = models.DateTimeField(default=timezone.now)
    conducted_by = models.CharField(max_length=150)
    total_variance_value_kes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    def __str__(self):
        return f'Audit on {self.audit_date} by {self.conducted_by}'


class StockAuditItem(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    audit = models.ForeignKey(StockAudit, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=64)
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    imei_or_serial = models.CharField(max_length=100, blank=True, null=True)
    system_qty = models.IntegerField(default=0)
    counted_qty = models.IntegerField(default=0)
    variance_qty = models.IntegerField(default=0)
    buying_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    variance_value_kes = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.product_name} - Variance: {self.variance_qty}'


class Transaction(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=generate_uuid)
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=60)
    reference_id = models.CharField(max_length=100)
    reference_no = models.CharField(max_length=100)
    description = models.TextField()
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=30)
    mpesa_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mpesa_ref = models.CharField(max_length=100, blank=True, null=True)
    cashier_name = models.CharField(max_length=150)

    def __str__(self):
        return f'[{self.type}] {self.reference_no} - KES {self.gross_amount}'
