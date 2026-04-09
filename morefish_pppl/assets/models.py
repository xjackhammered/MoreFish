from django.db import models

# Create your models here.
class AssetsType(models.Model):
    ast_title = models.CharField(max_length=255, null=True, blank=True)
    ast_created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "%s" % self.ast_title
    
class District(models.Model):
    district = models.CharField(max_length=50)
    lattitude = models.DecimalField(max_digits=9, decimal_places=6,blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,blank=True, null=True)

    def __str__(self) -> str:
        return "%s" % self.district
    
class AssetsProperties(models.Model):
    ast_name = models.CharField(max_length=300, null=True, blank=True)
    ast_type = models.ForeignKey(
        AssetsType,
        related_name="assets_type",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    ast_user = models.ManyToManyField(
        'users.User',
        related_name="assets_user", blank=True, null=True
    )
    ast_address = models.TextField(null=True, blank=True)
    ast_lat = models.CharField(max_length=100, null=True, blank=True)
    ast_long = models.CharField(max_length=100, null=True, blank=True)
    ast_length = models.CharField(max_length=100, null=True, blank=True)
    ast_width = models.CharField(max_length=100, null=True, blank=True)
    ast_depth = models.CharField(max_length=100, null=True, blank=True)
    ast_min_ph = models.CharField(max_length=100, default='6.5')
    ast_max_ph = models.CharField(max_length=100, default='9')
    ast_min_temp = models.CharField(max_length=100, default='10')
    ast_max_temp = models.CharField(max_length=100, default='33')
    ast_min_tds = models.CharField(max_length=100, default='120')
    ast_max_tds = models.CharField(max_length=100, default='400')
    ast_max_do = models.CharField(max_length=100, default='10')
    ast_min_do = models.CharField(max_length=100, default='5')
    ast_min_ammonia = models.CharField(max_length=100,default='0')
    ast_max_ammonia = models.CharField(max_length=100,default='0.05')
    ast_min_alkalinity = models.CharField(max_length=100, null=True, blank=True)
    ast_max_alkalinity = models.CharField(max_length=100, null=True, blank=True)
    ast_min_hardness = models.CharField(max_length=100, default='120')
    ast_max_hardness = models.CharField(max_length=100, default='400')
    ast_min_p = models.CharField(max_length=100, null=True, blank=True)
    ast_max_p = models.CharField(max_length=100, null=True, blank=True)
    ast_min_k = models.CharField(max_length=100, null=True, blank=True)
    ast_max_k = models.CharField(max_length=100, null=True, blank=True)
    ast_min_moisture = models.CharField(max_length=100, null=True, blank=True)
    ast_max_moisture = models.CharField(max_length=100, null=True, blank=True)
    ast_comments = models.TextField(null=True, blank=True)
    ast_description = models.TextField(null=True, blank=True)
    ast_image = models.ImageField(upload_to='uploads/assets/images/', blank=True, null=True)
    ast_created_at = models.DateTimeField(auto_now_add=True)
    ast_updated_at = models.DateTimeField(auto_now=True)
    ast_created_by = models.ForeignKey(
        'users.User',
        related_name="ast_created_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    ast_updated_by = models.ForeignKey(
        'users.User',
        related_name="ast_updated_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    company = models.ForeignKey("users.Company", null=True,blank=True, on_delete=models.SET_NULL)
    district = models.ForeignKey("assets.District",null=True,blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return "%s" % self.ast_name
class AssetsFiles(models.Model):
    asset = models.ForeignKey(
        AssetsProperties,
        related_name="assets_files",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    files = models.ImageField(upload_to='uploads/assets/images/', blank=True, null=True)

    class Meta:
        verbose_name = 'Assets File'
        verbose_name_plural = 'Assets Files'

    def __str__(self):
        return "%s" % self.files