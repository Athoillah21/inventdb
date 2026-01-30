import os
from django.core.management.base import BaseCommand
from inventory.models import DatabaseInventory

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Command(BaseCommand):
    help = 'Import database inventory from PostgreSQL (via SSH tunnel)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Query and display only, do not save to database'
        )
        parser.add_argument(
            '--host',
            type=str,
            default=os.environ.get('PG_HOST', 'localhost'),
            help='PostgreSQL host (default: localhost for tunnel)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=int(os.environ.get('PG_PORT', '6122')),
            help='PostgreSQL port'
        )
        parser.add_argument(
            '--database',
            type=str,
            default=os.environ.get('PG_DATABASE', 'postgres'),
            help='Database name'
        )
        parser.add_argument(
            '--user',
            type=str,
            default=os.environ.get('PG_USER', 'apps'),
            help='Database user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default=os.environ.get('PG_PASSWORD', 'apps2025'),
            help='Database password'
        )
        parser.add_argument(
            '--table',
            type=str,
            default=os.environ.get('PG_TABLE', 'database_inventory'),
            help='Source table name'
        )
        parser.add_argument(
            '--list-tables',
            action='store_true',
            help='List all tables and exit'
        )

    def handle(self, *args, **options):
        import psycopg2
        
        host = options['host']
        port = options['port']
        database = options['database']
        user = options['user']
        password = options['password']
        table = options['table']
        dry_run = options['dry_run']
        list_tables = options['list_tables']
        
        self.stdout.write(f'Connecting to PostgreSQL: {host}:{port}/{database}')
        
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            cursor = conn.cursor()
            self.stdout.write(self.style.SUCCESS('Connected!'))
            
            # List tables mode
            if list_tables:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                self.stdout.write('\nAvailable tables:')
                for t in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'  - {t[0]} ({count} rows)')
                cursor.close()
                conn.close()
                return
            
            # Column mapping (source -> model field)
            # Adjust these based on your actual table columns
            column_map = {
                'no': 'no',
                'hostname': 'hostname',
                'db': 'db',
                'database_status': 'database_status',
                'ip_oam': 'ip_oam',
                'ip_service': 'ip_service',
                'category_database': 'category_database',
                'notes': 'notes',
                'port': 'port',
                'version': 'version',
                'installation_date': 'installation_date',
                'operating_system': 'operating_system',
                'apps': 'apps',
                'apps_on_product_catalog': 'apps_on_product_catalog',
                'business_category': 'business_category',
                'departemen': 'departemen',
                'owner': 'owner',
                'pic_operational': 'pic_operational',
                'monitoring': 'monitoring',
                'site': 'site',
                'installed_by': 'installed_by',
                'size_mountpoint': 'size_mountpoint',
                'size_database': 'size_database',
            }
            
            # Get columns from source table
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            source_columns = [row[0] for row in cursor.fetchall()]
            
            if not source_columns:
                self.stdout.write(self.style.ERROR(f'Table "{table}" not found or has no columns.'))
                self.stdout.write('Use --list-tables to see available tables.')
                return
            
            self.stdout.write(f'Source columns: {source_columns}')
            
            # Build query for matching columns
            select_cols = []
            model_fields = []
            for src_col in source_columns:
                src_lower = src_col.lower()
                if src_lower in column_map:
                    select_cols.append(src_col)
                    model_fields.append(column_map[src_lower])
            
            self.stdout.write(f'Mapping {len(select_cols)} columns: {select_cols}')
            
            # Query data
            query = f"SELECT {', '.join(select_cols)} FROM {table}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            self.stdout.write(f'Found {len(rows)} records')
            
            if not dry_run:
                DatabaseInventory.objects.all().delete()
                self.stdout.write('Cleared existing data')
            
            imported = 0
            skipped = 0
            
            for row in rows:
                try:
                    data = {}
                    for i, field in enumerate(model_fields):
                        val = row[i]
                        if val is not None:
                            if field == 'installation_date' and hasattr(val, 'strftime'):
                                val = val.strftime('%Y-%m-%d')
                            else:
                                val = str(val).strip()
                        else:
                            val = ''
                        data[field] = val
                    
                    # Convert 'no' to int
                    if 'no' in data and data['no']:
                        try:
                            data['no'] = int(float(data['no']))
                        except (ValueError, TypeError):
                            skipped += 1
                            continue
                    else:
                        skipped += 1
                        continue
                    
                    if dry_run:
                        if imported < 5:
                            self.stdout.write(f'  Sample: {data}')
                    else:
                        DatabaseInventory.objects.create(**data)
                    
                    imported += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Row error: {e}'))
                    skipped += 1
            
            cursor.close()
            conn.close()
            
            action = 'Parsed' if dry_run else 'Imported'
            self.stdout.write(self.style.SUCCESS(f'{action} {imported} records'))
            self.stdout.write(f'Skipped {skipped} rows')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            self.stdout.write('\nMake sure SSH tunnel is running!')
            self.stdout.write('ssh -L 6122:10.250.200.37:6122 muhammad_athoillah_x@telkomsel.co.id@10.59.146.43 -p 22 -t launch 232105')
