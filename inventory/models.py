from django.db import models


class DatabaseInventory(models.Model):
    """Model representing a PostgreSQL database inventory entry."""
    
    no = models.IntegerField(default=0, verbose_name='No')
    hostname = models.CharField(max_length=100, blank=True, verbose_name='Hostname')
    db = models.CharField(max_length=200, blank=True, verbose_name='DB Name')
    database_status = models.CharField(max_length=100, blank=True, verbose_name='Database Status')
    ip_oam = models.CharField(max_length=50, blank=True, verbose_name='IP OAM')
    ip_service = models.CharField(max_length=50, blank=True, verbose_name='IP Service')
    category_database = models.CharField(max_length=50, blank=True, verbose_name='Category')
    notes = models.TextField(blank=True, verbose_name='Notes')
    port = models.CharField(max_length=20, blank=True, verbose_name='Port')
    version = models.CharField(max_length=100, blank=True, verbose_name='Version')
    installation_date = models.CharField(max_length=50, blank=True, verbose_name='Installation Date')
    operating_system = models.TextField(blank=True, verbose_name='Operating System')
    apps = models.CharField(max_length=300, blank=True, verbose_name='Apps')
    apps_on_product_catalog = models.CharField(max_length=200, blank=True, verbose_name='Apps on Product Catalog')
    business_category = models.CharField(max_length=150, blank=True, verbose_name='Business Category')
    departemen = models.CharField(max_length=200, blank=True, verbose_name='Department')
    owner = models.TextField(blank=True, verbose_name='Owner')
    pic_operational = models.CharField(max_length=200, blank=True, verbose_name='PIC Operational')
    monitoring = models.CharField(max_length=50, blank=True, verbose_name='Monitoring')
    site = models.CharField(max_length=20, blank=True, verbose_name='Site')
    installed_by = models.CharField(max_length=100, blank=True, verbose_name='Installed By')
    size_mountpoint = models.CharField(max_length=50, blank=True, verbose_name='Size Mountpoint')
    size_database = models.TextField(blank=True, verbose_name='Size Database')
    is_dismantled = models.BooleanField(default=False, verbose_name='Dismantled')
    
    class Meta:
        verbose_name = 'Database Inventory'
        verbose_name_plural = 'Database Inventories'
        ordering = ['no']
    
    def __str__(self):
        return f"{self.hostname} - {self.db}"
