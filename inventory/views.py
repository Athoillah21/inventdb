from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import DatabaseInventory
from .forms import DatabaseInventoryForm
import json
import csv
import re
from datetime import datetime


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('dashboard')



@login_required
def dashboard(request):
    """Main dashboard view with Plotly charts."""
    # Exclude dismantled databases from dashboard stats
    inventories = DatabaseInventory.objects.filter(is_dismantled=False)
    production_dbs = inventories.filter(category_database='Production')
    
    # Database Status Distribution
    status_data = list(inventories.exclude(database_status='').values('database_status')
                       .annotate(count=Count('id')).order_by('-count')[:10])
    
    # Category Distribution
    category_data = list(inventories.exclude(category_database='').values('category_database')
                         .annotate(count=Count('id')).order_by('-count'))
    
    # Site Distribution
    site_data = list(inventories.exclude(site='').values('site')
                     .annotate(count=Count('id')).order_by('-count'))
    
    # Business Category Distribution - Normalized to handle case/typo variations
    business_raw = inventories.exclude(business_category='')
    business_counts = {}
    
    # Normalization mapping
    normalize_map = {
        'mission critical': 'Mission Critical',
        'business critical': 'Business Critical',
        'business important': 'Business Important',
        'business support': 'Business Support',
        'bussiness support': 'Business Support',  # typo fix
        'bussiness critical': 'Business Critical',  # typo fix
        'bussiness important': 'Business Important',  # typo fix
    }
    
    for inv in business_raw:
        cat = inv.business_category.strip()
        # Normalize by lowercase lookup
        normalized = normalize_map.get(cat.lower(), cat.title())
        business_counts[normalized] = business_counts.get(normalized, 0) + 1
    
    business_data = [{'business_category': k, 'count': v} 
                     for k, v in sorted(business_counts.items(), key=lambda x: -x[1])[:8]]
    
    # Master/Slave Distribution for Production
    # Based on the 'notes' field which contains Master, Slave, Standby info
    master_count = production_dbs.filter(
        Q(notes__icontains='Master') | Q(notes__icontains='master')
    ).exclude(
        Q(notes__icontains='Slave') | Q(notes__icontains='Standby')
    ).count()
    
    slave_count = production_dbs.filter(
        Q(notes__icontains='Slave') | Q(notes__icontains='slave') |
        Q(notes__icontains='Standby') | Q(notes__icontains='standby')
    ).count()
    
    single_instance = production_dbs.filter(
        Q(notes__icontains='Single Instance') | Q(database_status__icontains='Single Instance')
    ).count()
    
    # Calculate other (not master, slave, or single instance)
    identified = master_count + slave_count + single_instance
    other_count = production_dbs.count() - identified if production_dbs.count() > identified else 0
    
    role_data = [
        {'role': 'Master', 'count': master_count},
        {'role': 'Slave/Standby', 'count': slave_count},
        {'role': 'Single Instance', 'count': single_instance},
    ]
    if other_count > 0:
        role_data.append({'role': 'Other', 'count': other_count})
    
    # Version Distribution (simplified)
    version_data = []
    for inv in inventories.exclude(version=''):
        ver = inv.version.strip()
        if 'PostgreSQL' in ver or 'EnterpriseDB' in ver:
            # Extract major version
            parts = ver.split()
            if len(parts) >= 2:
                version_data.append(parts[0] + ' ' + parts[1].split('.')[0])
    
    version_counts = {}
    for v in version_data:
        version_counts[v] = version_counts.get(v, 0) + 1
    
    version_chart = [{'version': k, 'count': v} for k, v in sorted(version_counts.items(), key=lambda x: -x[1])[:10]]
    
    # Database Growth (Cumulative)
    # Get all installation dates
    all_dates = inventories.values_list('installation_date', flat=True)
    total_inventory = inventories.count()
    
    monthly_counts = {}
    valid_date_count = 0
    
    # Month mapping for text formats
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    for d in all_dates:
        if not d:
            continue
            
        d_str = str(d).strip().lower()
        if not d_str:
            continue

        year = None
        month = None
        
        # Try YYYY-MM-DD or YYYY/MM/DD
        match_iso = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', d_str)
        # Try DD-MM-YYYY or DD/MM/YYYY
        match_dmy = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', d_str)
        # Try "Month YYYY"
        match_text = re.search(r'([a-z]+)[,\s-]+\d{0,2}[,\s-]*(\d{4})', d_str)
        
        if match_iso:
            year = int(match_iso.group(1))
            month = int(match_iso.group(2))
        elif match_dmy:
            year = int(match_dmy.group(3))
            month = int(match_dmy.group(2))
        elif match_text:
            m_str = match_text.group(1)
            y_str = match_text.group(2)
            if m_str in month_map:
                year = int(y_str)
                month = month_map[m_str]
        
        # Fallback: Just Year
        if not year:
             match_year = re.search(r'(\d{4})', d_str)
             if match_year:
                 year = int(match_year.group(1))
                 month = 1 
        
        if year and month:
            if 1990 <= year <= 2030 and 1 <= month <= 12:
                key = f"{year}-{month:02d}"
                monthly_counts[key] = monthly_counts.get(key, 0) + 1
                valid_date_count += 1

    # Calculate Baseline (Missing Dates or Unparseable)
    # These are treated as "existing from the start"
    baseline_count = total_inventory - valid_date_count

    # Sort and Aggregate Monthly
    sorted_months = sorted(monthly_counts.keys())
    
    cumulative_monthly = baseline_count
    growth_monthly = []
    
    # Track yearly counts
    yearly_counts = {} 
    
    for key in sorted_months:
        count = monthly_counts[key]
        cumulative_monthly += count
        
        # Format display date
        y, m = key.split('-')
        date_obj = datetime(int(y), int(m), 1)
        display_date = date_obj.strftime('%b %Y')
        
        growth_monthly.append({
            'label': display_date,
            'added': count,
            'total': cumulative_monthly,
            'raw_date': key
        })
        
        # Aggregate to yearly
        yearly_counts[y] = yearly_counts.get(y, 0) + count

    # Build Yearly Data
    sorted_years = sorted(yearly_counts.keys())
    cumulative_yearly = baseline_count
    growth_yearly = []
    
    for year in sorted_years:
        count = yearly_counts[year]
        cumulative_yearly += count
        growth_yearly.append({
            'label': year,
            'added': count,
            'total': cumulative_yearly
        })

    # Raw data for client-side filtering (simplified fields only)
    raw_data = []
    for inv in inventories:
        # Normalize business category
        bcat = inv.business_category.strip() if inv.business_category else ''
        bcat_lower = bcat.lower()
        bcat_normalized = {
            'mission critical': 'Mission Critical',
            'business critical': 'Business Critical',
            'business important': 'Business Important',
            'business support': 'Business Support',
        }.get(bcat_lower, bcat.title() if bcat else '')
        
        # Determine role
        notes = inv.notes or ''
        role = ''
        if 'master' in notes.lower() and 'slave' not in notes.lower() and 'standby' not in notes.lower():
            role = 'Master'
        elif 'slave' in notes.lower() or 'standby' in notes.lower():
            role = 'Slave/Standby'
        elif 'single instance' in notes.lower() or 'single instance' in (inv.database_status or '').lower():
            role = 'Single Instance'
        
        # Extract version
        ver = inv.version.strip() if inv.version else ''
        version_short = ''
        if 'PostgreSQL' in ver or 'EnterpriseDB' in ver:
            parts = ver.split()
            if len(parts) >= 2:
                version_short = parts[0] + ' ' + parts[1].split('.')[0]
        
        raw_data.append({
            'hostname': inv.hostname or '',
            'category': inv.category_database or '',
            'site': inv.site or '',
            'business': bcat_normalized,
            'status': inv.database_status or '',
            'version': version_short,
            'role': role,
            'installation_date': inv.installation_date or '',
        })
    
    # Get unique filter options
    filter_options = {
        'category': sorted(list(set(d['category'] for d in raw_data if d['category']))),
        'site': sorted(list(set(d['site'] for d in raw_data if d['site']))),
        'business': sorted(list(set(d['business'] for d in raw_data if d['business']))),
        'status': sorted(list(set(d['status'] for d in raw_data if d['status'])))[:10],
        'version': sorted(list(set(d['version'] for d in raw_data if d['version']))),
        'role': ['Master', 'Slave/Standby', 'Single Instance'],
    }

    context = {
        'total_databases': inventories.count(),
        'production_count': production_dbs.count(),
        'development_count': inventories.filter(category_database='Development').count(),
        'preprod_count': inventories.filter(category_database='Pre Production').count(),
        'master_count': master_count,
        'slave_count': slave_count,
        'status_data': json.dumps(status_data),
        'category_data': json.dumps(category_data),
        'site_data': json.dumps(site_data),
        'business_data': json.dumps(business_data),
        'version_data': json.dumps(version_chart),
        'role_data': json.dumps(role_data),
        'growth_monthly': json.dumps(growth_monthly),
        'growth_yearly': json.dumps(growth_yearly),
        'raw_data': json.dumps(raw_data),
        'filter_options': json.dumps(filter_options),
    }
    return render(request, 'dashboard.html', context)


def dashboard_api(request):
    """API endpoint returning dashboard data as JSON for Svelte frontend."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # DEBUG: Check DB connection
    from django.db import connections
    db_name = connections['default'].settings_dict['NAME']
    count = DatabaseInventory.objects.count()
    print(f"DEBUG dashboard_api: Connected to DB: {db_name}")
    print(f"DEBUG dashboard_api: Record count: {count}")
    
    inventories = DatabaseInventory.objects.filter(is_dismantled=False)
    production_dbs = inventories.filter(category_database='Production')
    
    # Raw data for client-side filtering
    raw_data = []
    for inv in inventories:
        # Normalize business category
        bcat = inv.business_category.strip() if inv.business_category else ''
        bcat_lower = bcat.lower()
        bcat_normalized = {
            'mission critical': 'Mission Critical',
            'business critical': 'Business Critical',
            'business important': 'Business Important',
            'business support': 'Business Support',
        }.get(bcat_lower, bcat.title() if bcat else '')
        
        # Determine role
        notes = inv.notes or ''
        role = ''
        if 'master' in notes.lower() and 'slave' not in notes.lower() and 'standby' not in notes.lower():
            role = 'Master'
        elif 'slave' in notes.lower() or 'standby' in notes.lower():
            role = 'Slave/Standby'
        elif 'single instance' in notes.lower() or 'single instance' in (inv.database_status or '').lower():
            role = 'Single Instance'
        
        # Extract version
        ver = inv.version.strip() if inv.version else ''
        version_short = ''
        if 'PostgreSQL' in ver or 'EnterpriseDB' in ver:
            parts = ver.split()
            if len(parts) >= 2:
                version_short = parts[0] + ' ' + parts[1].split('.')[0]
        
        raw_data.append({
            'hostname': inv.hostname or '',
            'category': inv.category_database or '',
            'site': inv.site or '',
            'business': bcat_normalized,
            'status': inv.database_status or '',
            'version': version_short,
            'role': role,
            'installation_date': str(inv.installation_date) if inv.installation_date else '',
        })
    
    # Get unique filter options
    filter_options = {
        'category': sorted(list(set(d['category'] for d in raw_data if d['category']))),
        'site': sorted(list(set(d['site'] for d in raw_data if d['site']))),
        'business': sorted(list(set(d['business'] for d in raw_data if d['business']))),
        'role': ['Master', 'Slave/Standby', 'Single Instance'],
    }
    
    return JsonResponse({
        'raw_data': raw_data,
        'filter_options': filter_options,
        'user': request.user.username,
    })


from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
import json as json_module


@csrf_exempt
def api_login(request):
    """API login endpoint for Svelte frontend."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json_module.loads(request.body)
        username = data.get('username', '')
        password = data.get('password', '')
    except:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return JsonResponse({
            'success': True,
            'user': user.username,
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Invalid username or password',
        }, status=401)


@csrf_exempt
def api_signup(request):
    """API signup endpoint for Svelte frontend."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json_module.loads(request.body)
        username = data.get('username', '')
        password = data.get('password', '')
    except:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
    
    if not username or not password:
        return JsonResponse({'error': 'Username and password required'}, status=400)
    
    # Check if user exists
    from django.contrib.auth.models import User
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)
    
    # Create user
    user = User.objects.create_user(username=username, password=password)
    user.is_active = False # Pending approval
    user.save()
    
    # Send Telegram Notification
    try:
        from dashboard.telegram_utils import send_approval_request
        send_approval_request(user)
    except Exception as e:
        print(f"Error sending telegram: {e}")

    # Return pending status (Do not login)
    return JsonResponse({
        'success': True,
        'message': 'Account created successfully! Your account is pending admin approval. You will be notified when active.',
        'pending': True
    })


def api_logout(request):
    """API logout endpoint for Svelte frontend."""
    auth_logout(request)
    return JsonResponse({'success': True})


@never_cache
def api_check_auth(request):
    """Check if user is authenticated."""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': request.user.username,
        })
    else:
        return JsonResponse({
            'authenticated': False,
        })


class InventoryListView(LoginRequiredMixin, ListView):
    """List view with filtering and pagination."""
    model = DatabaseInventory
    template_name = 'inventory_list.html'
    context_object_name = 'inventories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = DatabaseInventory.objects.all()
        
        # Apply filters
        hostname = self.request.GET.get('hostname')
        db = self.request.GET.get('db')
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        site = self.request.GET.get('site')
        business = self.request.GET.get('business')
        role = self.request.GET.get('role')
        
        if hostname:
            queryset = queryset.filter(hostname__icontains=hostname)
        if db:
            queryset = queryset.filter(db__icontains=db)
        if status:
            queryset = queryset.filter(database_status__icontains=status)
        if category:
            queryset = queryset.filter(category_database=category)
        if site:
            queryset = queryset.filter(site=site)
        if business:
            queryset = queryset.filter(business_category__icontains=business)
        if role:
            if role == 'Master':
                queryset = queryset.filter(
                    Q(notes__icontains='Master')
                ).exclude(
                    Q(notes__icontains='Slave') | Q(notes__icontains='Standby')
                )
            elif role == 'Slave':
                queryset = queryset.filter(
                    Q(notes__icontains='Slave') | Q(notes__icontains='Standby')
                )
            elif role == 'Single':
                queryset = queryset.filter(
                    Q(notes__icontains='Single Instance') | Q(database_status__icontains='Single Instance')
                )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ['Production', 'Development', 'Pre Production']
        context['sites'] = ['BSD', 'TBS', 'BRN']
        context['roles'] = ['Master', 'Slave', 'Single']
        context['current_filters'] = {
            'hostname': self.request.GET.get('hostname', ''),
            'db': self.request.GET.get('db', ''),
            'status': self.request.GET.get('status', ''),
            'category': self.request.GET.get('category', ''),
            'site': self.request.GET.get('site', ''),
            'business': self.request.GET.get('business', ''),
            'role': self.request.GET.get('role', ''),
        }
        return context


class InventoryCreateView(LoginRequiredMixin, CreateView):
    """Create new inventory entry."""
    model = DatabaseInventory
    form_class = DatabaseInventoryForm
    template_name = 'inventory_form.html'
    success_url = reverse_lazy('inventory_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Database'
        context['button_text'] = 'Create'
        return context


class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing inventory entry."""
    model = DatabaseInventory
    form_class = DatabaseInventoryForm
    template_name = 'inventory_form.html'
    success_url = reverse_lazy('inventory_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit: {self.object.hostname}'
        context['button_text'] = 'Save Changes'
        return context


class InventoryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete inventory entry with confirmation."""
    model = DatabaseInventory
    template_name = 'inventory_confirm_delete.html'
    success_url = reverse_lazy('inventory_list')


@login_required
def export_inventory_csv(request):
    """Export filtered inventory data to CSV."""
    queryset = DatabaseInventory.objects.all()
    
    # Apply same filters as InventoryListView
    hostname = request.GET.get('hostname')
    db = request.GET.get('db')
    status = request.GET.get('status')
    category = request.GET.get('category')
    site = request.GET.get('site')
    business = request.GET.get('business')
    role = request.GET.get('role')
    
    if hostname:
        queryset = queryset.filter(hostname__icontains=hostname)
    if db:
        queryset = queryset.filter(db__icontains=db)
    if status:
        queryset = queryset.filter(database_status__icontains=status)
    if category:
        queryset = queryset.filter(category_database=category)
    if site:
        queryset = queryset.filter(site=site)
    if business:
        queryset = queryset.filter(business_category__icontains=business)
    if role:
        if role == 'Master':
            queryset = queryset.filter(
                Q(notes__icontains='Master')
            ).exclude(
                Q(notes__icontains='Slave') | Q(notes__icontains='Standby')
            )
        elif role == 'Slave':
            queryset = queryset.filter(
                Q(notes__icontains='Slave') | Q(notes__icontains='Standby')
            )
        elif role == 'Single':
            queryset = queryset.filter(
                Q(notes__icontains='Single Instance') | Q(database_status__icontains='Single Instance')
            )
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_export.csv"'
    
    writer = csv.writer(response)
    # Write header
    writer.writerow([
        'No', 'Hostname', 'Database', 'Port', 'Version', 'Category', 
        'Site', 'Business Category', 'Database Status', 'Notes'
    ])
    
    # Write data
    for inv in queryset:
        writer.writerow([
            inv.no, inv.hostname, inv.db, inv.port, inv.version,
            inv.category_database, inv.site, inv.business_category,
            inv.database_status, inv.notes
        ])
    
    return response


@csrf_exempt
@login_required
def api_inventory_list(request):
    """API endpoint for full inventory list."""
    inventories = DatabaseInventory.objects.all().order_by('id')
    
    # Return all fields needed for the table
    data = []
    for inv in inventories:
        # Normalize business category
        bcat = inv.business_category.strip() if inv.business_category else ''
        bcat_lower = bcat.lower()
        bcat_normalized = {
            'mission critical': 'Mission Critical',
            'business critical': 'Business Critical',
            'business important': 'Business Important',
            'business support': 'Business Support',
        }.get(bcat_lower, bcat.title() if bcat else '')
        
        # Determine role
        notes = inv.notes or ''
        role = ''
        if 'master' in notes.lower() and 'slave' not in notes.lower() and 'standby' not in notes.lower():
            role = 'Master'
        elif 'slave' in notes.lower() or 'standby' in notes.lower():
            role = 'Slave/Standby'
        elif 'single instance' in notes.lower() or 'single instance' in (inv.database_status or '').lower():
            role = 'Single Instance'

        # Extract version
        ver = inv.version.strip() if inv.version else ''
        version_short = ''
        if 'PostgreSQL' in ver or 'EnterpriseDB' in ver:
            parts = ver.split()
            if len(parts) >= 2:
                version_short = parts[0] + ' ' + parts[1].split('.')[0]

        data.append({
            'id': inv.id,
            'hostname': inv.hostname or '',
            'db_name': inv.db or '',  # 'db' field in model
            'status': inv.database_status or '',
            'category': inv.category_database or '',
            'site': inv.site or '',
            'version': version_short or ver, # Fallback to full string if parse fails
            'port': inv.port or '',
            'role': role,
            'business': bcat_normalized,
            'notes': inv.notes or '',
            'is_dismantled': inv.is_dismantled,
        })

    return JsonResponse({'inventory': data})


@csrf_exempt
@login_required
def api_inventory_delete(request, pk):
    """API endpoint to delete an inventory item."""
    if request.method != 'DELETE' and request.method != 'POST':
         return JsonResponse({'error': 'DELETE or POST required'}, status=405)
         
    try:
        inv = DatabaseInventory.objects.get(pk=pk)
        inv.delete()
        return JsonResponse({'success': True})
    except DatabaseInventory.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@csrf_exempt
@login_required
def api_inventory_create(request):
    """API endpoint to create a new inventory item."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Determine Role logic for Notes
        role = data.get('role', '')
        notes = data.get('notes', '')
        if role and role not in notes:
            if notes:
                notes += f" ({role})"
            else:
                notes = role
        
        inv = DatabaseInventory.objects.create(
            hostname=data.get('hostname'),
            db=data.get('db_name'),
            database_status=data.get('status'),
            category_database=data.get('category'),
            site=data.get('site'),
            version=data.get('version'),
            port=data.get('port'),
            business_category=data.get('business'),
            notes=notes
        )
        return JsonResponse({'success': True, 'id': inv.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_inventory_update(request, pk):
    """API endpoint to update an inventory item."""
    if request.method != 'PUT' and request.method != 'POST':
        return JsonResponse({'error': 'PUT or POST required'}, status=405)
        
    try:
        inv = DatabaseInventory.objects.get(pk=pk)
        data = json.loads(request.body)
        
        inv.hostname = data.get('hostname', inv.hostname)
        inv.db = data.get('db_name', inv.db)
        inv.database_status = data.get('status', inv.database_status)
        inv.category_database = data.get('category', inv.category_database)
        inv.site = data.get('site', inv.site)
        inv.version = data.get('version', inv.version)
        inv.port = data.get('port', inv.port)
        inv.business_category = data.get('business', inv.business_category)
        
        # Handle Role update fairly simply - append if not present in notes, 
        # or just update notes if provided directly. 
        # For this POC, we'll assume the client sends specific 'notes' or 'role'
        if 'notes' in data:
            inv.notes = data['notes']
        elif 'role' in data:
            # If role is sent but notes isn't, attempt to inject role into notes
            # This is a simplification; ideally notes and role would be separate
            role = data['role']
            current_notes = inv.notes or ''
            # Simple replacement of known roles
            for r in ['Master', 'Slave', 'Standby', 'Single Instance']:
                if r in current_notes:
                    current_notes = current_notes.replace(r, role)
                    break
            else:
                if role not in current_notes:
                     current_notes += f" {role}"
            inv.notes = current_notes
        
        # Handle is_dismantled field
        if 'is_dismantled' in data:
            inv.is_dismantled = data['is_dismantled']
            
        inv.save()
        return JsonResponse({'success': True})
    except DatabaseInventory.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
