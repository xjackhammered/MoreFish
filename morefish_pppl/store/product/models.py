# from django.db import models
# from core.models import CoreModel
#
#
# # Create your models here.
#
# class ProductCategory(CoreModel):
#     category_name = models.CharField(max_length=150, blank=True, null=True)
#     category_image = models.ImageField('upload/category_image/', blank=True, null=True)
#
#     class Meta:
#         indexes = [
#             models.Index(fields=['category_name']),
#         ]
#
#     def __str__(self) -> str:
#         return self.category_name
#
#
# # added by papel on 15 march, 2025
# class ProductCompany(CoreModel):  # Renamed from Company to ProductCompany
#     name = models.CharField(max_length=150, blank=False, null=False)
#     category = models.ForeignKey('product.ProductCategory', on_delete=models.CASCADE, related_name='product_companies')
#     company_image = models.ImageField(upload_to='company_images/', blank=True, null=True)  # New field added
#
#     def __str__(self):
#         return self.name
#
#
# class Product(CoreModel):
#     name = models.CharField(max_length=150, blank=True, null=True)
#     description = models.CharField(max_length=150, blank=True, null=True)
#     price = models.IntegerField(default=0)
#     category = models.ForeignKey('product.ProductCategory', blank=True, null=True, on_delete=models.DO_NOTHING)
#     product_company = models.ForeignKey('product.ProductCompany', blank=True, null=True, on_delete=models.DO_NOTHING)  # Renamed field
#     is_published = models.BooleanField(default=False)  # New field added
#
#
#     class Meta:
#         indexes = [
#             models.Index(fields=['name', 'price'])
#         ]
#
#     def __str__(self):
#         return self.name
#
#
# class ProductImage(CoreModel):
#     product = models.ForeignKey('product.Product', blank=True, null=True, on_delete=models.DO_NOTHING)
#     image = models.ImageField(upload_to='uploads/', blank=True, null=True)
#     is_default = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.product.name
#
#
# class ProductSpecifications(CoreModel):
#     product = models.ForeignKey('product.Product', blank=True, null=True, on_delete=models.DO_NOTHING)
#     specification = models.CharField(max_length=150, blank=True, null=True)
#
#     def __str__(self):
#         return self.product.name


from django.db import models
from core.models import CoreModel

class ProductCategory(CoreModel):
    category_name = models.CharField(max_length=150, blank=True, null=True)
    category_image = models.ImageField(upload_to='category_image/', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['category_name']),
        ]

    def __str__(self) -> str:
        return self.category_name


class ProductCompany(CoreModel):  # Renamed from Company to ProductCompany
    name = models.CharField(max_length=150, blank=False, null=False)
    category = models.ForeignKey('product.ProductCategory', on_delete=models.CASCADE, related_name='product_companies')
    company_image = models.ImageField(upload_to='company_images/', blank=True, null=True)  # New field added

    def __str__(self):
        return self.name


class Product(CoreModel):
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # Changed to TextField for long text
    # price = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # updated
    category = models.ForeignKey('product.ProductCategory', blank=True, null=True, on_delete=models.DO_NOTHING)
    product_company = models.ForeignKey('product.ProductCompany', blank=True, null=True, on_delete=models.DO_NOTHING)
    is_published = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'price'])
        ]

    def __str__(self):
        return self.name


class ProductImage(CoreModel):
    product = models.ForeignKey('product.Product', blank=True, null=True, on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name if self.product else "No product"


class ProductSpecifications(CoreModel):
    product = models.ForeignKey('product.Product', blank=True, null=True, on_delete=models.DO_NOTHING)
    specification = models.TextField(blank=True, null=True)  # Changed to TextField for long text

    def __str__(self):
        return self.product.name if self.product else "No product"
