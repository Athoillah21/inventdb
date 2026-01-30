import csv
import os
from django.core.management.base import BaseCommand
from inventory.models import DatabaseInventory


class Command(BaseCommand):
    help = 'Import database inventory from CSV file'

    def handle(self, *args, **options):
        # Path to CSV file
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
            'Invent PostgreSQL_1(Januari 2026).csv'
        )
        
        self.stdout.write(f'Reading CSV from: {csv_path}')
        
        # Clear existing data
        DatabaseInventory.objects.all().delete()
        self.stdout.write('Cleared existing data')
        
        imported = 0
        skipped = 0
        
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            for row in reader:
                try:
                    # Skip empty rows
                    no_val = row.get('No', '').strip()
                    if not no_val or not no_val.isdigit():
                        skipped += 1
                        continue
                    
                    DatabaseInventory.objects.create(
                        no=int(no_val),
                        hostname=row.get('Hostname', '').strip(),
                        db=row.get('DB', '').strip(),
                        database_status=row.get('Database Status', '').strip(),
                        ip_oam=row.get('IP OAM', '').strip(),
                        ip_service=row.get('IP SERVICE', '').strip(),
                        category_database=row.get('CATEGORY DATABASE', '').strip(),
                        notes=row.get('NOTES', '').strip(),
                        port=row.get('PORT', '').strip(),
                        version=row.get('Version', '').strip(),
                        installation_date=row.get('Tanggal Instalasi', '').strip(),
                        operating_system=row.get('OPERATION SYSTEM', '').strip(),
                        apps=row.get('APPS', '').strip(),
                        apps_on_product_catalog=row.get('Apps on Product Catalog', '').strip(),
                        business_category=row.get('BUSINESS CATEGORY', '').strip(),
                        departemen=row.get('Departemen', '').strip(),
                        owner=row.get('OWNER', '').strip(),
                        pic_operational=row.get('PIC Operational', '').strip(),
                        monitoring=row.get('Monitoring', '').strip(),
                        site=row.get('Site', '').strip(),
                        installed_by=row.get('Installed by', '').strip(),
                        size_mountpoint=row.get('Size Mountpoint datadir in (GiB)', '').strip(),
                        size_database=row.get('Size Database (GiB)', '').strip(),
                    )
                    imported += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error on row: {e}'))
                    skipped += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported} records'))
        self.stdout.write(f'Skipped {skipped} rows')
