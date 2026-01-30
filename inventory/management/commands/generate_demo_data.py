"""Generate random demo data for DatabaseInventory."""
import random
from django.core.management.base import BaseCommand
from inventory.models import DatabaseInventory


class Command(BaseCommand):
    help = 'Generate random demo data for the database inventory'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of records to generate (default: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        if options['clear']:
            deleted, _ = DatabaseInventory.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {deleted} existing records'))
        
        # Realistic data pools
        hostname_prefixes = [
            'pgsqlbsdpdb', 'pgsqltbspdb', 'rafmpdb', 'consdb', 'trans4merspdb',
            'hpebrnpdb', 'hpetbspdb', 'ngpammedbsdpdb', 'dmpdb', 'gitlabeepdb'
        ]
        
        db_names = [
            'PPCIAMNEW', 'SIFA', 'PGATE', 'PPPES', 'PPRAFM', 'CITRA', 'KLOP',
            'APIDS', 'GRAPARI', 'DOMARP', 'AGNOSD', 'CPQ', 'PPBIMAX', 'PPMEQP',
            'PPWMA', 'PPMEVO', 'PPUTOIP', 'PPDOLCE', 'PPNOIS', 'PPRMS', 'PPHPE',
            'PPOTPGATE5', 'PPCDP', 'PPMYTSELCASH', 'PPIPCA', 'PPFMCORDER'
        ]
        
        statuses = [
            'Replication (Bare Metal)', 'Replication (VM)', 'Single Instance (VM)',
            'Single Instance (Bare Metal)', 'Replication'
        ]
        
        categories = ['Production', 'Development', 'Pre Production']
        category_weights = [0.70, 0.20, 0.10]  # 70% production
        
        sites = ['BSD', 'TBS', 'BRN']
        site_weights = [0.45, 0.45, 0.10]
        
        business_categories = [
            'Mission Critical', 'Business Critical', 'Business Important', 
            'Business Support', 'Bussiness Support'
        ]
        
        versions = [
            'PostgreSQL 14.2', 'PostgreSQL 14.4', 'PostgreSQL 15.2', 'PostgreSQL 15.3',
            'PostgreSQL 15.6', 'PostgreSQL 16.2', 'EnterpriseDB 14.2', 'EnterpriseDB 15.2',
            'EnterpriseDB 16.2', 'EnterpriseDB 13.4.8', 'EnterpriseDB 14.1'
        ]
        
        notes_options = [
            'Master', 'Slave', 'Standby', 'Single Instance', 'Master', 'Standby',
            'Slave DR', 'Master', 'Standby', 'Single Instance'
        ]
        
        monitoring_options = ['PEM 8.5', 'PEM 8.2', 'PEM 7.10', '-']
        
        os_options = [
            'Red Hat Enterprise Linux Server release 7.6 (Maipo)',
            'Red Hat Enterprise Linux Server release 8.4 (Ootpa)',
            'Red Hat Enterprise Linux 9.0 (Plow)',
            'Rocky Linux 9.5 (Blue Onyx)'
        ]
        
        installers = [
            'Risyda', 'Hilmi', 'Fajri', 'Azmul', 'Athok', 'Kahfi', 'Aqil',
            'Anisa', 'Rangga', 'Dzaki', 'Dilah', 'Yusran', 'Farhan'
        ]
        
        departments = [
            'IT Data Integration Management', 'IT Payment and Collection Management',
            'Database Administration Management Department', 'IT Digital Business Channel',
            'IT UX and Discovery Department', 'IT Analytics and Machine Learning',
            'IT ERP Core Finance Department', 'IT Billing Support'
        ]
        
        apps = [
            'Payment Gateway', 'MyTelkomsel', 'CIAM', 'Digipos Reporting',
            'SIFA', 'CPQ', 'GRAPARI', 'DOLCE', 'RAFM', 'BIMA', 'KLOP'
        ]
        
        # Generate records
        start_no = DatabaseInventory.objects.count() + 1
        records_created = 0
        
        for i in range(count):
            # Generate realistic IP
            ip_oam = f"10.{random.randint(38,59)}.{random.randint(1,200)}.{random.randint(1,254)}"
            ip_service = f"10.{random.randint(38,59)}.{random.randint(1,200)}.{random.randint(1,254)}"
            
            # Generate random date between 2020 and 2025
            year = random.randint(2020, 2025)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            install_date = f"{day:02d}/{month:02d}/{year}"
            
            # Generate random port
            port = str(random.choice([5432, 5433, 9901, 9903, 9910, 9911, 9920, 9923, 9933, 9955, 9965, 9976]))
            
            # Generate hostname
            prefix = random.choice(hostname_prefixes)
            suffix = random.randint(1, 4)
            hostname = f"{prefix}{suffix}"
            
            # Generate size
            size_mp = f"{random.randint(50, 1000)}GB"
            size_db = f"{random.randint(10, 500)} GB"
            
            category = random.choices(categories, weights=category_weights)[0]
            site = random.choices(sites, weights=site_weights)[0]
            
            record = DatabaseInventory(
                no=start_no + i,
                hostname=hostname,
                db=random.choice(db_names),
                database_status=random.choice(statuses),
                ip_oam=ip_oam,
                ip_service=ip_service,
                category_database=category,
                notes=random.choice(notes_options),
                port=port,
                version=random.choice(versions),
                installation_date=install_date,
                operating_system=random.choice(os_options),
                apps=random.choice(apps),
                apps_on_product_catalog='',
                business_category=random.choice(business_categories),
                departemen=random.choice(departments),
                owner=f"user_{random.randint(1,50)}@telkomsel.co.id",
                pic_operational='',
                monitoring=random.choice(monitoring_options),
                site=site,
                installed_by=random.choice(installers),
                size_mountpoint=size_mp,
                size_database=size_db,
            )
            record.save()
            records_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {records_created} demo records'))
