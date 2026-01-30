from django import forms
from .models import DatabaseInventory


class DatabaseInventoryForm(forms.ModelForm):
    """Form for creating and editing database inventory entries."""
    
    class Meta:
        model = DatabaseInventory
        fields = [
            'no', 'hostname', 'db', 'database_status', 'ip_oam', 'ip_service',
            'category_database', 'notes', 'port', 'version', 'installation_date',
            'operating_system', 'apps', 'business_category', 'departemen',
            'owner', 'pic_operational', 'monitoring', 'site', 'installed_by',
            'size_mountpoint', 'size_database'
        ]
        widgets = {
            'no': forms.NumberInput(attrs={'class': 'form-control'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'db': forms.TextInput(attrs={'class': 'form-control'}),
            'database_status': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Status'),
                ('Single Instance (VM)', 'Single Instance (VM)'),
                ('Single Instance (Bare Metal)', 'Single Instance (Bare Metal)'),
                ('Replication (VM)', 'Replication (VM)'),
                ('Replication (Bare Metal)', 'Replication (Bare Metal)'),
                ('Witness', 'Witness'),
                ('Server backup', 'Server backup'),
            ]),
            'ip_oam': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_service': forms.TextInput(attrs={'class': 'form-control'}),
            'category_database': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Category'),
                ('Production', 'Production'),
                ('Development', 'Development'),
                ('Pre Production', 'Pre Production'),
            ]),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'port': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'installation_date': forms.TextInput(attrs={'class': 'form-control'}),
            'operating_system': forms.TextInput(attrs={'class': 'form-control'}),
            'apps': forms.TextInput(attrs={'class': 'form-control'}),
            'business_category': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Business Category'),
                ('Mission Critical', 'Mission Critical'),
                ('Business Critical', 'Business Critical'),
                ('Business Important', 'Business Important'),
                ('Business Support', 'Business Support'),
                ('Bussiness Support', 'Bussiness Support'),
            ]),
            'departemen': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.TextInput(attrs={'class': 'form-control'}),
            'pic_operational': forms.TextInput(attrs={'class': 'form-control'}),
            'monitoring': forms.TextInput(attrs={'class': 'form-control'}),
            'site': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Site'),
                ('BSD', 'BSD'),
                ('TBS', 'TBS'),
                ('BRN', 'BRN'),
            ]),
            'installed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'size_mountpoint': forms.TextInput(attrs={'class': 'form-control'}),
            'size_database': forms.TextInput(attrs={'class': 'form-control'}),
        }
