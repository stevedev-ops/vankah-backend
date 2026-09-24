import uuid
from django.utils import timezone
from django.db.models import Sum, F
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import (
    UserProfile, Product, JobCard, LaborItem, JobPartItem,
    YardVehicle, ToolItem, ToolRental, DebtorCustomer,
    DebtRecord, Shift, StockAudit, StockAuditItem, Transaction
)
from .serializers import (
    UserProfileSerializer, ProductSerializer, JobCardSerializer,
    YardVehicleSerializer, ToolItemSerializer, ToolRentalSerializer,
    DebtorCustomerSerializer, DebtRecordSerializer, ShiftSerializer,
    StockAuditSerializer, TransactionSerializer
)

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        role = request.data.get('role')
        pin = request.data.get('pin')
        user = UserProfile.objects.filter(role=role, pin=pin).first()
        if user:
            return Response(UserProfileSerializer(user).data)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'], url_path='users')
    def list_users(self, request):
        users = UserProfile.objects.all()
        return Response(UserProfileSerializer(users, many=True).data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer


class JobCardViewSet(viewsets.ModelViewSet):
    queryset = JobCard.objects.all().order_by('-created_at')
    serializer_class = JobCardSerializer

    @action(detail=True, methods=['post'], url_path='settle')
    def settle(self, request, pk=None):
        job = self.get_object()
        payment_method = request.data.get('paymentMethod', 'Cash')
        mpesa_amount = float(request.data.get('mpesaAmount', 0))
        cash_amount = float(request.data.get('cashAmount', 0))
        mpesa_ref = request.data.get('mpesaRef', '')

        job.status = 'Delivered'
        job.payment_method = payment_method
        job.mpesa_amount = mpesa_amount
        job.cash_amount = cash_amount
        job.mpesa_ref = mpesa_ref
        job.completed_at = timezone.now()
        job.save()

        total_labor = sum(item.cost for item in job.labor_items.all())
        total_parts_selling = sum(part.unit_selling_price * part.quantity for part in job.parts.all())
        total_parts_cost = sum(part.unit_cost_price * part.quantity for part in job.parts.all())
        total_bill = float(total_labor + total_parts_selling)
        remaining_balance = total_bill - float(job.advance_deposit)

        if remaining_balance > 0:
            Transaction.objects.create(
                type='JOB_CARD',
                reference_id=job.id,
                reference_no=job.job_no,
                description=f'Final Settlement for {job.car_reg_no} ({job.car_make_model})',
                gross_amount=remaining_balance,
                cost_amount=float(total_parts_cost),
                profit_amount=remaining_balance - float(total_parts_cost),
                payment_method=payment_method,
                mpesa_amount=mpesa_amount,
                cash_amount=cash_amount,
                mpesa_ref=mpesa_ref,
                cashier_name=request.data.get('cashierName', 'Workshop Staff')
            )

        return Response(JobCardSerializer(job).data)


class YardVehicleViewSet(viewsets.ModelViewSet):
    queryset = YardVehicle.objects.all().order_by('-arrival_date')
    serializer_class = YardVehicleSerializer

    @action(detail=True, methods=['post'], url_path='settle')
    def settle(self, request, pk=None):
        vehicle = self.get_object()
        payment_method = request.data.get('paymentMethod', 'Cash')
        amount_paid = float(request.data.get('amountPaid', 0))
        mpesa_ref = request.data.get('mpesaRef', '')
        cashier_name = request.data.get('cashierName', 'Security Officer')

        now_str = timezone.now().strftime('%Y%m%d')
        clean_plate = vehicle.car_reg_no.replace(' ', '')
        gate_pass = f'GP-{now_str}-{clean_plate}'
        vehicle.paid_amount = float(vehicle.paid_amount) + amount_paid
        vehicle.is_cleared = True
        vehicle.gate_pass_no = gate_pass
        vehicle.cleared_at = timezone.now()
        vehicle.save()

        if amount_paid > 0:
            Transaction.objects.create(
                type='YARD_FEE',
                reference_id=vehicle.id,
                reference_no=gate_pass,
                description=f'Yard Storage Fee Clearance for {vehicle.car_reg_no}',
                gross_amount=amount_paid,
                cost_amount=0,
                profit_amount=amount_paid,
                payment_method=payment_method,
                mpesa_amount=amount_paid if payment_method == 'Mpesa' else 0,
                cash_amount=amount_paid if payment_method == 'Cash' else 0,
                mpesa_ref=mpesa_ref,
                cashier_name=cashier_name
            )

        return Response(YardVehicleSerializer(vehicle).data)


class ToolItemViewSet(viewsets.ModelViewSet):
    queryset = ToolItem.objects.all().order_by('name')
    serializer_class = ToolItemSerializer


class ToolRentalViewSet(viewsets.ModelViewSet):
    queryset = ToolRental.objects.all().order_by('-date_taken')
    serializer_class = ToolRentalSerializer

    @action(detail=False, methods=['post'], url_path='rent')
    def rent_tool(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = serializer.save(status='Active')

        ToolItem.objects.filter(id=rental.tool_id).update(status='Rented')

        total_payment = float(rental.total_hire_fee) + float(rental.deposit_paid)
        Transaction.objects.create(
            type='TOOL_RENTAL',
            reference_id=rental.id,
            reference_no=f'RENT-{rental.tool_code}',
            description=f'Tool Hire: {rental.tool_name} to {rental.hirer_name}',
            gross_amount=total_payment,
            cost_amount=0,
            profit_amount=float(rental.total_hire_fee),
            payment_method=rental.payment_method,
            mpesa_amount=total_payment if rental.payment_method == 'Mpesa' else 0,
            cash_amount=total_payment if rental.payment_method == 'Cash' else 0,
            mpesa_ref=rental.mpesa_ref,
            cashier_name=request.data.get('cashierName', 'Tool Desk')
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='return')
    def return_tool(self, request, pk=None):
        rental = self.get_object()
        damage_fee = float(request.data.get('damageFee', 0))
        deposit_refunded = float(request.data.get('depositRefunded', 0))

        rental.damage_fee = damage_fee
        rental.deposit_refunded = deposit_refunded
        rental.actual_return_date = timezone.now()
        rental.status = 'Returned'
        rental.save()

        ToolItem.objects.filter(id=rental.tool_id).update(status='Available')

        return Response(ToolRentalSerializer(rental).data)


class DebtorCustomerViewSet(viewsets.ModelViewSet):
    queryset = DebtorCustomer.objects.all().order_by('name')
    serializer_class = DebtorCustomerSerializer

    @action(detail=True, methods=['post'], url_path='repay')
    def record_repayment(self, request, pk=None):
        debtor = self.get_object()
        amount = float(request.data.get('amount', 0))
        payment_method = request.data.get('paymentMethod', 'Cash')
        mpesa_ref = request.data.get('mpesaRef', '')
        cashier_name = request.data.get('cashierName', 'Cashier')

        debtor.current_balance = max(0, float(debtor.current_balance) - amount)
        debtor.save()

        now_time = timezone.now().strftime('%H%M%S')
        ref_no = f'REC-REP-{now_time}'
        rec = DebtRecord.objects.create(
            customer_id=debtor.id,
            customer_name=debtor.name,
            type='DEBT_REPAYMENT',
            amount=amount,
            reference_no=ref_no,
            description=f'Debt Repayment from {debtor.name}',
            payment_method=payment_method,
            mpesa_ref=mpesa_ref,
            cashier_name=cashier_name
        )

        Transaction.objects.create(
            type='DEBT_REPAYMENT',
            reference_id=debtor.id,
            reference_no=ref_no,
            description=f'Debt Repayment received from {debtor.name}',
            gross_amount=amount,
            cost_amount=0,
            profit_amount=amount,
            payment_method=payment_method,
            mpesa_amount=amount if payment_method == 'Mpesa' else 0,
            cash_amount=amount if payment_method == 'Cash' else 0,
            mpesa_ref=mpesa_ref,
            cashier_name=cashier_name
        )

        return Response({
            'debtor': DebtorCustomerSerializer(debtor).data,
            'debtRecord': DebtRecordSerializer(rec).data
        })


class DebtRecordViewSet(viewsets.ModelViewSet):
    queryset = DebtRecord.objects.all().order_by('-date')
    serializer_class = DebtRecordSerializer


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all().order_by('-start_time')
    serializer_class = ShiftSerializer

    @action(detail=False, methods=['get'], url_path='active')
    def active_shift(self, request):
        shift = Shift.objects.filter(status='Open').order_by('-start_time').first()
        if shift:
            return Response(ShiftSerializer(shift).data)
        return Response(None, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='start')
    def start_shift(self, request):
        cashier_name = request.data.get('cashierName', 'Workshop Staff')
        opening_float = float(request.data.get('openingFloat', 0))

        shift = Shift.objects.create(
            cashier_name=cashier_name,
            opening_float=opening_float,
            total_cash_expected=opening_float,
            total_mpesa_expected=0,
            status='Open'
        )
        return Response(ShiftSerializer(shift).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='close')
    def close_shift(self, request, pk=None):
        shift = self.get_object()
        actual_cash = float(request.data.get('actualClosingCash', 0))
        notes = request.data.get('notes', '')

        shift.closing_cash_actual = actual_cash
        shift.discrepancy = actual_cash - float(shift.total_cash_expected)
        shift.status = 'Closed'
        shift.end_time = timezone.now()
        shift.notes = notes
        shift.save()

        return Response(ShiftSerializer(shift).data)


class StockAuditViewSet(viewsets.ModelViewSet):
    queryset = StockAudit.objects.all().order_by('-audit_date')
    serializer_class = StockAuditSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date')
    serializer_class = TransactionSerializer

    @action(detail=False, methods=['post'], url_path='pos-sale')
    def process_pos_sale(self, request):
        cart = request.data.get('cart', [])
        payment_method = request.data.get('paymentMethod', 'Cash')
        mpesa_amount = float(request.data.get('mpesaAmount', 0))
        cash_amount = float(request.data.get('cashAmount', 0))
        mpesa_ref = request.data.get('mpesaRef', '')
        debtor_id = request.data.get('debtorId')
        cashier_name = request.data.get('cashierName', 'Cashier')

        total_gross = 0.0
        total_cost = 0.0
        desc_parts = []

        for item in cart:
            prod_id = item['product']['id']
            qty = int(item['quantity'])
            unit_price = float(item['unitPrice'])
            unit_cost = float(item['unitCost'])

            total_gross += unit_price * qty
            total_cost += unit_cost * qty
            desc_parts.append(f"{item['product']['name']} (x{qty})")

            try:
                prod = Product.objects.get(id=prod_id)
                prod.stock_qty = max(0, prod.stock_qty - qty)
                prod.save()
            except Product.DoesNotExist:
                pass

        now_time = timezone.now().strftime('%y%m%d%H%M%S')
        ref_no = f'POS-REC-{now_time}'
        desc = ', '.join(desc_parts)

        if payment_method == 'Credit' and debtor_id:
            try:
                debtor = DebtorCustomer.objects.get(id=debtor_id)
                debtor.current_balance = float(debtor.current_balance) + total_gross
                debtor.save()
                DebtRecord.objects.create(
                    customer_id=debtor.id,
                    customer_name=debtor.name,
                    type='CREDIT_PURCHASE',
                    amount=total_gross,
                    reference_no=ref_no,
                    description=desc,
                    cashier_name=cashier_name
                )
            except DebtorCustomer.DoesNotExist:
                pass

        tx = Transaction.objects.create(
            type='POS_SALE',
            reference_id=ref_no,
            reference_no=ref_no,
            description=desc,
            gross_amount=total_gross,
            cost_amount=total_cost,
            profit_amount=total_gross - total_cost,
            payment_method=payment_method,
            mpesa_amount=mpesa_amount,
            cash_amount=cash_amount,
            mpesa_ref=mpesa_ref,
            cashier_name=cashier_name
        )

        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def vehicle_history(request, plate):
    norm_plate = plate.replace(' ', '').upper()
    job_cards = JobCard.objects.filter(car_reg_no__icontains=norm_plate).order_by('-created_at')
    yard_stays = YardVehicle.objects.filter(car_reg_no__icontains=norm_plate).order_by('-arrival_date')

    total_spent = sum(
        sum(item.cost for item in j.labor_items.all()) +
        sum(p.unit_selling_price * p.quantity for p in j.parts.all())
        for j in job_cards
    )
    total_labor = sum(
        sum(item.cost for item in j.labor_items.all())
        for j in job_cards
    )

    parts_fitted = []
    for j in job_cards:
        for p in j.parts.all():
            parts_fitted.append({
                'name': p.name,
                'quantity': p.quantity,
                'date': j.created_at.strftime('%Y-%m-%d')
            })

    return Response({
        'jobCards': JobCardSerializer(job_cards, many=True).data,
        'yardStays': YardVehicleSerializer(yard_stays, many=True).data,
        'totalSpent': float(total_spent),
        'totalLaborDone': float(total_labor),
        'partsFitted': parts_fitted
    })


@api_view(['GET'])
def dashboard_stats(request):
    total_sales = Transaction.objects.aggregate(total=Sum('gross_amount'))['total'] or 0
    total_profit = Transaction.objects.aggregate(profit=Sum('profit_amount'))['profit'] or 0
    active_jobs = JobCard.objects.exclude(status='Delivered').count()
    active_rentals = ToolRental.objects.filter(status='Active').count()
    parked_vehicles = YardVehicle.objects.filter(is_cleared=False).count()
    low_stock_count = Product.objects.filter(stock_qty__lte=F('min_alert_qty')).count()

    return Response({
        'totalSales': float(total_sales),
        'totalProfit': float(total_profit),
        'activeJobs': active_jobs,
        'activeRentals': active_rentals,
        'parkedVehicles': parked_vehicles,
        'lowStockCount': low_stock_count
    })
