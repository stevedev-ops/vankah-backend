from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import (
    UserProfile, Product, JobCard, LaborItem, JobPartItem,
    YardVehicle, ToolItem, ToolRental, DebtorCustomer,
    DebtRecord, Shift, StockAudit, StockAuditItem, Transaction
)

class Command(BaseCommand):
    help = 'Clears all mock data from the database leaving a clean empty production slate'

    def handle(self, *args, **options):
        self.stdout.write('Clearing all operational data...')
        
        # Delete all mock records
        Transaction.objects.all().delete()
        StockAuditItem.objects.all().delete()
        StockAudit.objects.all().delete()
        Shift.objects.all().delete()
        DebtRecord.objects.all().delete()
        DebtorCustomer.objects.all().delete()
        ToolRental.objects.all().delete()
        ToolItem.objects.all().delete()
        YardVehicle.objects.all().delete()
        JobPartItem.objects.all().delete()
        LaborItem.objects.all().delete()
        JobCard.objects.all().delete()
        Product.objects.all().delete()
        
        # Ensure standard workstation access roles exist for login
        UserProfile.objects.all().delete()
        UserProfile.objects.create(
            id='user-admin-1',
            name='Director / General Manager',
            role='ADMIN',
            title='Managing Director & Owner',
            pin='1234'
        )
        UserProfile.objects.create(
            id='user-staff-1',
            name='Workshop Staff / Cashier',
            role='STAFF',
            title='Front Desk Cashier',
            pin='0000'
        )

        # Ensure Django admin superuser exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@vankah.local', 'admin123')
            self.stdout.write('  [+] Created superuser: admin / admin123')

        self.stdout.write(self.style.SUCCESS('Successfully cleared all mock data! Database is completely fresh.'))
