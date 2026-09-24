import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import (
    UserProfile, Product, JobCard, LaborItem, JobPartItem,
    YardVehicle, ToolItem, ToolRental, DebtorCustomer,
    DebtRecord, Shift, StockAudit, StockAuditItem, Transaction
)

class Command(BaseCommand):
    help = 'Seeds initial ERP mock data into PostgreSQL'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data into PostgreSQL...')

        # 1. Users
        UserProfile.objects.all().delete()
        admin_user = UserProfile.objects.create(
            id='user-admin-1',
            name='Director / General Manager',
            role='ADMIN',
            title='Owner & Managing Director',
            pin='1234'
        )
        staff_user = UserProfile.objects.create(
            id='user-staff-1',
            name='Workshop Staff / Cashier',
            role='STAFF',
            title='Lead Cashier & Front Desk',
            pin='0000'
        )
        self.stdout.write('  [+] Created User Profiles')

        # 2. Products
        Product.objects.all().delete()
        products_data = [
            {
                'id': 'prod-1',
                'name': 'Auto OBD2 Diagnostic Scanner Pro',
                'sku': 'DIAG-SCAN-01',
                'imei_or_serial': 'SN-9824-77102-K',
                'category': 'Electrical',
                'buying_price': 12000,
                'selling_price': 18500,
                'stock_qty': 4,
                'min_alert_qty': 2,
                'location': 'Shelf E1'
            },
            {
                'id': 'prod-2',
                'name': 'Heavy Duty 12V 75Ah Battery',
                'sku': 'BAT-75AH-HD',
                'imei_or_serial': 'BAT-88392019-B',
                'category': 'Electrical',
                'buying_price': 8500,
                'selling_price': 12000,
                'stock_qty': 8,
                'min_alert_qty': 3,
                'location': 'Battery Rack'
            },
            {
                'id': 'prod-3',
                'name': 'Universal Panel Beating Hammer & Dolly Kit',
                'sku': 'PB-TOOL-KIT',
                'imei_or_serial': 'KIT-44109',
                'category': 'Tools & Accessories',
                'buying_price': 4500,
                'selling_price': 7000,
                'stock_qty': 3,
                'min_alert_qty': 1,
                'location': 'Workshop Tool Room'
            },
            {
                'id': 'prod-4',
                'name': '2K Auto Body Filler & Hardener (3kg)',
                'sku': 'BODY-FIL-3KG',
                'category': 'Consumables & Oils',
                'buying_price': 1800,
                'selling_price': 2800,
                'stock_qty': 14,
                'min_alert_qty': 5,
                'location': 'Paint Store'
            },
            {
                'id': 'prod-5',
                'name': 'High Performance Spark Plugs (Pack of 4)',
                'sku': 'NGK-SP-4',
                'category': 'Engine & Transmission',
                'buying_price': 1500,
                'selling_price': 2500,
                'stock_qty': 22,
                'min_alert_qty': 6,
                'location': 'Shelf A3'
            },
            {
                'id': 'prod-6',
                'name': '2.5mm Mild Steel Welding Electrodes (5kg Box)',
                'sku': 'WELD-ELEC-25',
                'category': 'Custom Fabrication',
                'buying_price': 2200,
                'selling_price': 3500,
                'stock_qty': 12,
                'min_alert_qty': 4,
                'location': 'Welding Bay'
            }
        ]
        for p in products_data:
            Product.objects.create(**p)
        self.stdout.write('  [+] Created Products')

        # 3. Job Cards
        JobCard.objects.all().delete()
        now = timezone.now()

        job1 = JobCard.objects.create(
            id='job-101',
            job_no='JOB-2026-001',
            car_reg_no='KDG 482B',
            car_make_model='Toyota Hilux Single Cab',
            customer_name='Kiprono Ngetich',
            customer_phone='0712 345 678',
            status='In Progress',
            advance_deposit=15000,
            payment_method='Mpesa',
            mpesa_ref='RBL784920K',
            mpesa_amount=15000,
            cash_amount=0,
            notes='Fabrication and heavy restoration build for farm use.',
            created_at=now - datetime.timedelta(days=3)
        )
        LaborItem.objects.create(id='lab-1', job_card=job1, type='Panel Beating', description='Chassis alignment and right front fender reshape', mechanic_name='John Kamau', cost=14000)
        LaborItem.objects.create(id='lab-2', job_card=job1, type='Welding', description='Reinforce heavy bumper brackets & undercarriage mount', mechanic_name='Otieno Welder', cost=8500)
        LaborItem.objects.create(id='lab-3', job_card=job1, type='Spray Painting', description='2K basecoat & clearcoat right front quarter', mechanic_name='Paul Spray', cost=9000)
        JobPartItem.objects.create(id='part-1', job_card=job1, part_id='prod-4', name='2K Auto Body Filler & Hardener (3kg)', quantity=2, unit_cost_price=1800, unit_selling_price=2800, is_outside_purchase=False)
        JobPartItem.objects.create(id='part-2', job_card=job1, name='OEM Front Bumper Assembly (Bought from City Auto)', quantity=1, unit_cost_price=22000, unit_selling_price=26000, is_outside_purchase=True, vendor_name='City Spares Ltd', receipt_no='REC-99410')

        job2 = JobCard.objects.create(
            id='job-102',
            job_no='JOB-2026-002',
            car_reg_no='KCY 912M',
            car_make_model='Isuzu D-Max',
            customer_name='Sammy Mwangi',
            customer_phone='0722 889 900',
            status='Ready',
            advance_deposit=2000,
            notes='Exhaust silencer replaced and welded.',
            created_at=now - datetime.timedelta(days=1)
        )
        LaborItem.objects.create(id='lab-4', job_card=job2, type='Welding', description='Exhaust fabrication & silencer bracket welding', mechanic_name='Otieno Welder', cost=4500)
        JobPartItem.objects.create(id='part-3', job_card=job2, part_id='prod-6', name='2.5mm Mild Steel Welding Electrodes (5kg Box)', quantity=1, unit_cost_price=2200, unit_selling_price=3500, is_outside_purchase=False)

        job0 = JobCard.objects.create(
            id='job-100',
            job_no='JOB-2026-000',
            car_reg_no='KDG 482B',
            car_make_model='Toyota Hilux Single Cab',
            customer_name='Kiprono Ngetich',
            customer_phone='0712 345 678',
            status='Delivered',
            advance_deposit=9000,
            payment_method='Mpesa',
            notes='Initial maintenance visit 2 months ago.',
            created_at=now - datetime.timedelta(days=60),
            completed_at=now - datetime.timedelta(days=59)
        )
        LaborItem.objects.create(id='lab-0', job_card=job0, type='Mechanical', description='Complete brake pad change & suspension greasing', mechanic_name='Kamau', cost=6500)
        JobPartItem.objects.create(id='part-0', job_card=job0, part_id='prod-5', name='High Performance Spark Plugs (Pack of 4)', quantity=1, unit_cost_price=1500, unit_selling_price=2500, is_outside_purchase=False)
        self.stdout.write('  [+] Created Job Cards')

        # 4. Yard Vehicles
        YardVehicle.objects.all().delete()
        YardVehicle.objects.create(
            id='yard-1',
            car_reg_no='KBA 301P',
            customer_name='Maina Mutua',
            customer_phone='0733 112 233',
            bay_number='Bay 04 (Holding Area)',
            arrival_date=now - datetime.timedelta(days=14),
            weekly_rate=5000,
            storage_penalty_per_day=500,
            paid_amount=5000,
            is_cleared=False,
            notes='Vehicle awaiting clearance from insurer.'
        )
        YardVehicle.objects.create(
            id='yard-2',
            car_reg_no='KBX 770T',
            customer_name='Grace Wambui',
            customer_phone='0799 445 566',
            bay_number='Bay 12 (Storage)',
            arrival_date=now - datetime.timedelta(days=21),
            weekly_rate=5000,
            storage_penalty_per_day=500,
            paid_amount=10000,
            is_cleared=False,
            notes='Project body parked while sourcing engine block.'
        )
        self.stdout.write('  [+] Created Yard Vehicles')

        # 5. Tools
        ToolItem.objects.all().delete()
        ToolItem.objects.create(id='tool-1', tool_code='BJ-01', name='Hydraulic Heavy Duty Body Jack 10-Ton', category='Lifting & Jacks', daily_rate=1000, security_deposit=3000, status='Rented', condition_notes='All extension rods and pump tested.')
        ToolItem.objects.create(id='tool-2', tool_code='BJ-02', name='Hydraulic Heavy Duty Body Jack 10-Ton', category='Lifting & Jacks', daily_rate=1000, security_deposit=3000, status='Available', condition_notes='Good condition.')
        ToolItem.objects.create(id='tool-3', tool_code='CH-10', name='Auto Body Check Handle & Lever Bar', category='Hand Tools', daily_rate=500, security_deposit=1500, status='Rented', condition_notes='Checked and oiled.')
        ToolItem.objects.create(id='tool-4', tool_code='WM-04', name='Inverter ARC/TIG Welding Machine 250A', category='Welding', daily_rate=2000, security_deposit=5000, status='Available', condition_notes='Includes earth clamp and electrode lead.')
        ToolItem.objects.create(id='tool-5', tool_code='HP-03', name='Hydraulic Bearing & Hub Puller Kit', category='Hydraulics', daily_rate=1500, security_deposit=4000, status='Available', condition_notes='All 3 pulling arms intact.')
        self.stdout.write('  [+] Created Tools')

        # 6. Tool Rentals
        ToolRental.objects.all().delete()
        ToolRental.objects.create(
            id='rent-1',
            tool_id='tool-1',
            tool_code='BJ-01',
            tool_name='Hydraulic Heavy Duty Body Jack 10-Ton',
            hirer_name='David Ochieng (Mechanic)',
            hirer_phone='0700 334 455',
            hirer_id_number='29884120',
            date_taken=now - datetime.timedelta(days=2),
            expected_return_date=now + datetime.timedelta(days=1),
            daily_rate=1000,
            deposit_paid=3000,
            total_hire_fee=3000,
            damage_fee=0,
            status='Active',
            payment_method='Mpesa',
            mpesa_ref='RKL330198'
        )
        ToolRental.objects.create(
            id='rent-2',
            tool_id='tool-3',
            tool_code='CH-10',
            tool_name='Auto Body Check Handle & Lever Bar',
            hirer_name='Francis Kilonzo',
            hirer_phone='0711 998 877',
            hirer_id_number='31204899',
            date_taken=now - datetime.timedelta(days=1),
            expected_return_date=now,
            daily_rate=500,
            deposit_paid=1500,
            total_hire_fee=500,
            damage_fee=0,
            status='Active',
            payment_method='Cash'
        )
        self.stdout.write('  [+] Created Tool Rentals')

        # 7. Debtors
        DebtorCustomer.objects.all().delete()
        DebtRecord.objects.all().delete()
        DebtorCustomer.objects.create(
            id='debtor-1',
            name='Maina Matatu Fleet',
            phone='0722 102 938',
            business_or_car_reg='Fleet #14 (KCR 411T, KDA 990B)',
            credit_limit=50000,
            current_balance=16500,
            notes='Weekly credit terms; pays every Monday.',
            created_at=now - datetime.timedelta(days=30)
        )
        DebtorCustomer.objects.create(
            id='debtor-2',
            name='Muriithi Contractors & Builders',
            phone='0733 445 566',
            business_or_car_reg='Isuzu Tipper KCH 884Q',
            credit_limit=80000,
            current_balance=24000,
            notes='Takes fabrication parts and welding rods on credit.',
            created_at=now - datetime.timedelta(days=20)
        )
        DebtorCustomer.objects.create(
            id='debtor-3',
            name='Sammy Mwangi (Taxi Operator)',
            phone='0722 889 900',
            business_or_car_reg='Toyota Probox KCY 912M',
            credit_limit=20000,
            current_balance=4500,
            notes='Trusted regular client.',
            created_at=now - datetime.timedelta(days=15)
        )

        DebtRecord.objects.create(
            id='rec-1',
            customer_id='debtor-1',
            customer_name='Maina Matatu Fleet',
            date=now - datetime.timedelta(days=4),
            type='CREDIT_PURCHASE',
            amount=16500,
            reference_no='POS-CR-8812',
            description='2x 12V 75Ah Batteries on Credit',
            cashier_name='Workshop Staff'
        )
        DebtRecord.objects.create(
            id='rec-2',
            customer_id='debtor-2',
            customer_name='Muriithi Contractors & Builders',
            date=now - datetime.timedelta(days=2),
            type='CREDIT_PURCHASE',
            amount=24000,
            reference_no='POS-CR-8819',
            description='Fabrication parts and Welding Electrodes',
            cashier_name='Workshop Staff'
        )
        self.stdout.write('  [+] Created Debtors & Debt Records')

        # 8. Shift
        Shift.objects.all().delete()
        Shift.objects.create(
            id='shift-today',
            cashier_name='Workshop Staff / Cashier',
            start_time=now,
            opening_float=5000,
            total_cash_expected=7500,
            total_mpesa_expected=36500,
            status='Open'
        )
        self.stdout.write('  [+] Created Active Shift')

        # 9. Transactions
        Transaction.objects.all().delete()
        Transaction.objects.create(
            id='tx-1',
            date=now,
            type='POS_SALE',
            reference_id='pos-1001',
            reference_no='POS-REC-001',
            description='Auto OBD2 Diagnostic Scanner Pro (SN-9824-77102-K)',
            gross_amount=18500,
            cost_amount=12000,
            profit_amount=6500,
            payment_method='Mpesa',
            mpesa_amount=18500,
            cash_amount=0,
            mpesa_ref='RQM998201',
            cashier_name='Workshop Staff / Cashier'
        )
        Transaction.objects.create(
            id='tx-2',
            date=now - datetime.timedelta(days=3),
            type='JOB_CARD',
            reference_id='job-101',
            reference_no='JOB-2026-001',
            description='Advance Deposit for KDG 482B Hilux Panel & Welding',
            gross_amount=15000,
            cost_amount=0,
            profit_amount=15000,
            payment_method='Mpesa',
            mpesa_amount=15000,
            cash_amount=0,
            mpesa_ref='RBL784920K',
            cashier_name='Workshop Staff / Cashier'
        )
        Transaction.objects.create(
            id='tx-3',
            date=now - datetime.timedelta(days=2),
            type='TOOL_RENTAL',
            reference_id='rent-1',
            reference_no='RENT-BJ-01',
            description='Body Jack 10-Ton Hire (3 Days) + Deposit',
            gross_amount=3000,
            cost_amount=0,
            profit_amount=3000,
            payment_method='Mpesa',
            mpesa_amount=3000,
            cash_amount=0,
            mpesa_ref='RKL330198',
            cashier_name='Workshop Staff / Cashier'
        )
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with realistic ERP data!'))
