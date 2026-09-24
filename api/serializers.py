from rest_framework import serializers
from .models import (
    UserProfile, Product, JobCard, LaborItem, JobPartItem,
    YardVehicle, ToolItem, ToolRental, DebtorCustomer,
    DebtRecord, Shift, StockAudit, StockAuditItem, Transaction
)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'role', 'title', 'pin']


class ProductSerializer(serializers.ModelSerializer):
    imeiOrSerial = serializers.CharField(source='imei_or_serial', required=False, allow_null=True, allow_blank=True)
    buyingPrice = serializers.FloatField(source='buying_price')
    sellingPrice = serializers.FloatField(source='selling_price')
    stockQty = serializers.IntegerField(source='stock_qty')
    minAlertQty = serializers.IntegerField(source='min_alert_qty')
    location = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'imeiOrSerial', 'category',
            'buyingPrice', 'sellingPrice', 'stockQty', 'minAlertQty',
            'location', 'notes'
        ]


class LaborItemSerializer(serializers.ModelSerializer):
    mechanicName = serializers.CharField(source='mechanic_name')

    class Meta:
        model = LaborItem
        fields = ['id', 'type', 'description', 'mechanicName', 'cost']


class JobPartItemSerializer(serializers.ModelSerializer):
    partId = serializers.CharField(source='part_id', required=False, allow_null=True, allow_blank=True)
    unitCostPrice = serializers.FloatField(source='unit_cost_price')
    unitSellingPrice = serializers.FloatField(source='unit_selling_price')
    isOutsidePurchase = serializers.BooleanField(source='is_outside_purchase')
    vendorName = serializers.CharField(source='vendor_name', required=False, allow_null=True, allow_blank=True)
    receiptNo = serializers.CharField(source='receipt_no', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = JobPartItem
        fields = [
            'id', 'partId', 'name', 'quantity', 'unitCostPrice',
            'unitSellingPrice', 'isOutsidePurchase', 'vendorName', 'receiptNo'
        ]


class JobCardSerializer(serializers.ModelSerializer):
    jobNo = serializers.CharField(source='job_no')
    carRegNo = serializers.CharField(source='car_reg_no')
    carMakeModel = serializers.CharField(source='car_make_model')
    customerName = serializers.CharField(source='customer_name')
    customerPhone = serializers.CharField(source='customer_phone')
    advanceDeposit = serializers.FloatField(source='advance_deposit', default=0)
    paymentMethod = serializers.CharField(source='payment_method', required=False, allow_null=True, allow_blank=True)
    mpesaRef = serializers.CharField(source='mpesa_ref', required=False, allow_null=True, allow_blank=True)
    mpesaAmount = serializers.FloatField(source='mpesa_amount', default=0)
    cashAmount = serializers.FloatField(source='cash_amount', default=0)
    createdAt = serializers.DateTimeField(source='created_at', required=False)
    completedAt = serializers.DateTimeField(source='completed_at', required=False, allow_null=True)
    laborItems = LaborItemSerializer(source='labor_items', many=True, required=False)
    parts = JobPartItemSerializer(many=True, required=False)

    class Meta:
        model = JobCard
        fields = [
            'id', 'jobNo', 'carRegNo', 'carMakeModel', 'customerName',
            'customerPhone', 'status', 'laborItems', 'parts', 'advanceDeposit',
            'paymentMethod', 'mpesaRef', 'mpesaAmount', 'cashAmount', 'notes',
            'createdAt', 'completedAt'
        ]

    def create(self, validated_data):
        labor_data = validated_data.pop('labor_items', [])
        parts_data = validated_data.pop('parts', [])
        job = JobCard.objects.create(**validated_data)
        for item in labor_data:
            LaborItem.objects.create(job_card=job, **item)
        for part in parts_data:
            JobPartItem.objects.create(job_card=job, **part)
        return job

    def update(self, instance, validated_data):
        labor_data = validated_data.pop('labor_items', None)
        parts_data = validated_data.pop('parts', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if labor_data is not None:
            instance.labor_items.all().delete()
            for item in labor_data:
                LaborItem.objects.create(job_card=instance, **item)

        if parts_data is not None:
            instance.parts.all().delete()
            for part in parts_data:
                JobPartItem.objects.create(job_card=instance, **part)

        return instance


class YardVehicleSerializer(serializers.ModelSerializer):
    carRegNo = serializers.CharField(source='car_reg_no')
    customerName = serializers.CharField(source='customer_name')
    customerPhone = serializers.CharField(source='customer_phone')
    bayNumber = serializers.CharField(source='bay_number')
    arrivalDate = serializers.DateTimeField(source='arrival_date', required=False)
    weeklyRate = serializers.FloatField(source='weekly_rate', default=5000)
    storagePenaltyPerDay = serializers.FloatField(source='storage_penalty_per_day', default=500)
    paidAmount = serializers.FloatField(source='paid_amount', default=0)
    isCleared = serializers.BooleanField(source='is_cleared', default=False)
    gatePassNo = serializers.CharField(source='gate_pass_no', required=False, allow_null=True, allow_blank=True)
    clearedAt = serializers.DateTimeField(source='cleared_at', required=False, allow_null=True)

    class Meta:
        model = YardVehicle
        fields = [
            'id', 'carRegNo', 'customerName', 'customerPhone', 'bayNumber',
            'arrivalDate', 'weeklyRate', 'storagePenaltyPerDay', 'paidAmount',
            'notes', 'isCleared', 'gatePassNo', 'clearedAt'
        ]


class ToolItemSerializer(serializers.ModelSerializer):
    toolCode = serializers.CharField(source='tool_code')
    dailyRate = serializers.FloatField(source='daily_rate')
    securityDeposit = serializers.FloatField(source='security_deposit')
    conditionNotes = serializers.CharField(source='condition_notes', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ToolItem
        fields = [
            'id', 'toolCode', 'name', 'category', 'dailyRate',
            'securityDeposit', 'status', 'conditionNotes'
        ]


class ToolRentalSerializer(serializers.ModelSerializer):
    toolId = serializers.CharField(source='tool_id')
    toolName = serializers.CharField(source='tool_name')
    toolCode = serializers.CharField(source='tool_code')
    hirerName = serializers.CharField(source='hirer_name')
    hirerPhone = serializers.CharField(source='hirer_phone')
    hirerIdNumber = serializers.CharField(source='hirer_id_number')
    dateTaken = serializers.DateTimeField(source='date_taken', required=False)
    expectedReturnDate = serializers.DateTimeField(source='expected_return_date')
    actualReturnDate = serializers.DateTimeField(source='actual_return_date', required=False, allow_null=True)
    dailyRate = serializers.FloatField(source='daily_rate')
    depositPaid = serializers.FloatField(source='deposit_paid')
    totalHireFee = serializers.FloatField(source='total_hire_fee')
    damageFee = serializers.FloatField(source='damage_fee', default=0)
    depositRefunded = serializers.FloatField(source='deposit_refunded', default=0)
    paymentMethod = serializers.CharField(source='payment_method', default='Mpesa')
    mpesaRef = serializers.CharField(source='mpesa_ref', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ToolRental
        fields = [
            'id', 'toolId', 'toolName', 'toolCode', 'hirerName',
            'hirerPhone', 'hirerIdNumber', 'dateTaken', 'expectedReturnDate',
            'actualReturnDate', 'dailyRate', 'depositPaid', 'totalHireFee',
            'damageFee', 'depositRefunded', 'status', 'paymentMethod', 'mpesaRef'
        ]


class DebtorCustomerSerializer(serializers.ModelSerializer):
    businessOrCarReg = serializers.CharField(source='business_or_car_reg')
    creditLimit = serializers.FloatField(source='credit_limit')
    currentBalance = serializers.FloatField(source='current_balance', default=0)
    createdAt = serializers.DateTimeField(source='created_at', required=False)

    class Meta:
        model = DebtorCustomer
        fields = [
            'id', 'name', 'phone', 'businessOrCarReg', 'creditLimit',
            'currentBalance', 'notes', 'createdAt'
        ]


class DebtRecordSerializer(serializers.ModelSerializer):
    customerId = serializers.CharField(source='customer_id')
    customerName = serializers.CharField(source='customer_name')
    referenceNo = serializers.CharField(source='reference_no')
    paymentMethod = serializers.CharField(source='payment_method', required=False, allow_null=True, allow_blank=True)
    mpesaRef = serializers.CharField(source='mpesa_ref', required=False, allow_null=True, allow_blank=True)
    cashierName = serializers.CharField(source='cashier_name')
    amount = serializers.FloatField()
    date = serializers.DateTimeField(required=False)

    class Meta:
        model = DebtRecord
        fields = [
            'id', 'customerId', 'customerName', 'date', 'type', 'amount',
            'referenceNo', 'description', 'paymentMethod', 'mpesaRef', 'cashierName'
        ]


class ShiftSerializer(serializers.ModelSerializer):
    cashierName = serializers.CharField(source='cashier_name')
    startTime = serializers.DateTimeField(source='start_time', required=False)
    endTime = serializers.DateTimeField(source='end_time', required=False, allow_null=True)
    openingFloat = serializers.FloatField(source='opening_float')
    closingCashActual = serializers.FloatField(source='closing_cash_actual', required=False, allow_null=True)
    totalCashExpected = serializers.FloatField(source='total_cash_expected', default=0)
    totalMpesaExpected = serializers.FloatField(source='total_mpesa_expected', default=0)
    discrepancy = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Shift
        fields = [
            'id', 'cashierName', 'startTime', 'endTime', 'openingFloat',
            'closingCashActual', 'totalCashExpected', 'totalMpesaExpected',
            'discrepancy', 'status', 'notes'
        ]


class StockAuditItemSerializer(serializers.ModelSerializer):
    productId = serializers.CharField(source='product_id')
    productName = serializers.CharField(source='product_name')
    imeiOrSerial = serializers.CharField(source='imei_or_serial', required=False, allow_null=True, allow_blank=True)
    systemQty = serializers.IntegerField(source='system_qty')
    countedQty = serializers.IntegerField(source='counted_qty')
    varianceQty = serializers.IntegerField(source='variance_qty')
    buyingPrice = serializers.FloatField(source='buying_price')
    varianceValueKes = serializers.FloatField(source='variance_value_kes')

    class Meta:
        model = StockAuditItem
        fields = [
            'id', 'productId', 'productName', 'sku', 'imeiOrSerial',
            'systemQty', 'countedQty', 'varianceQty', 'buyingPrice',
            'varianceValueKes'
        ]


class StockAuditSerializer(serializers.ModelSerializer):
    auditDate = serializers.DateTimeField(source='audit_date', required=False)
    conductedBy = serializers.CharField(source='conducted_by')
    totalVarianceValueKes = serializers.FloatField(source='total_variance_value_kes', default=0)
    items = StockAuditItemSerializer(many=True, required=False)

    class Meta:
        model = StockAudit
        fields = [
            'id', 'auditDate', 'conductedBy', 'items', 'totalVarianceValueKes',
            'status'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        audit = StockAudit.objects.create(**validated_data)
        for item in items_data:
            StockAuditItem.objects.create(audit=audit, **item)
        return audit


class TransactionSerializer(serializers.ModelSerializer):
    referenceId = serializers.CharField(source='reference_id')
    referenceNo = serializers.CharField(source='reference_no')
    grossAmount = serializers.FloatField(source='gross_amount')
    costAmount = serializers.FloatField(source='cost_amount', default=0)
    profitAmount = serializers.FloatField(source='profit_amount', default=0)
    paymentMethod = serializers.CharField(source='payment_method')
    mpesaAmount = serializers.FloatField(source='mpesa_amount', default=0)
    cashAmount = serializers.FloatField(source='cash_amount', default=0)
    mpesaRef = serializers.CharField(source='mpesa_ref', required=False, allow_null=True, allow_blank=True)
    cashierName = serializers.CharField(source='cashier_name')
    date = serializers.DateTimeField(required=False)

    class Meta:
        model = Transaction
        fields = [
            'id', 'date', 'type', 'referenceId', 'referenceNo',
            'description', 'grossAmount', 'costAmount', 'profitAmount',
            'paymentMethod', 'mpesaAmount', 'cashAmount', 'mpesaRef',
            'cashierName'
        ]
