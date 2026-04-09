# from django.contrib import admin
# from .models import Product, ProductCategory, ProductImage, ProductSpecifications
#
# # Register Product model with the admin site
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description', 'price']
#     search_fields = ['name', 'description']
#     list_filter = ['price']
#
# # Register ProductImage model with the admin site
# @admin.register(ProductImage)
# class ProductImageAdmin(admin.ModelAdmin):
#     list_display = ['product', 'image', 'is_default']
#     list_filter = ['is_default']
#
# @admin.register(ProductCategory)
# class ProductImageAdmin(admin.ModelAdmin):
#     list_display = ['category_name', 'category_image']
# # Register ProductSpecifications model with the admin site
# @admin.register(ProductSpecifications)
# class ProductSpecificationsAdmin(admin.ModelAdmin):
#     list_display = ['product', 'specification']

#
# from django.contrib import admin
# from django import forms
# from .models import (
#     Product,
#     ProductCategory,
#     ProductCompany,
#     ProductImage,
#     ProductSpecifications,
# )
#
# ##############################################
# # Custom Admin Forms for Excluding Core Fields
# ##############################################
#
# class ProductCategoryAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductCategory
#         fields = ['category_name', 'category_image']
#
#
# class ProductSpecificationsAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductSpecifications
#         fields = ['product', 'specification']
#
#
# class ProductCompanyAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductCompany
#         fields = ['name', 'category']
#
#
# class ProductImageAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = ['product', 'image', 'is_default']
#
#
# ##############################################
# # Inline Forms
# ##############################################
#
# class ProductSpecificationsInlineForm(forms.ModelForm):
#     new_specification = forms.CharField(
#         required=False,
#         label="New Specification",
#         widget=forms.TextInput(attrs={'placeholder': 'Enter new specification if not listed'})
#     )
#
#     class Meta:
#         model = ProductSpecifications
#         fields = ['specification', 'new_specification']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         specs = ProductSpecifications.objects.exclude(specification__isnull=True)\
#                                              .exclude(specification__exact='')\
#                                              .values_list('specification', flat=True).distinct()
#         choices = [('', '---------')] + [(spec, spec) for spec in specs]
#         self.fields['specification'].widget = forms.Select(choices=choices)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         new_spec = cleaned_data.get("new_specification", "").strip()
#         if new_spec:
#             cleaned_data["specification"] = new_spec
#         if not cleaned_data.get("specification"):
#             raise forms.ValidationError("Please select an existing specification or add a new one.")
#         return cleaned_data
#
# class ProductSpecificationsInline(admin.TabularInline):
#     model = ProductSpecifications
#     extra = 1
#     form = ProductSpecificationsInlineForm
#     fields = ['specification', 'new_specification']
#
#
# class ProductImageInlineForm(forms.ModelForm):
#     existing_image = forms.ModelChoiceField(
#         queryset=ProductImage.objects.all(),
#         required=False,
#         label="Select Existing Image",
#         help_text="Choose an already uploaded image (or leave blank to upload a new one)."
#     )
#
#     class Meta:
#         model = ProductImage
#         fields = ['existing_image', 'image', 'is_default']
#
#     def clean(self):
#         cleaned_data = super().clean()
#         existing = cleaned_data.get("existing_image")
#         new_upload = cleaned_data.get("image")
#         if existing and new_upload:
#             raise forms.ValidationError("Please select either an existing image or upload a new one, not both.")
#         if not existing and not new_upload:
#             raise forms.ValidationError("Please select an existing image or upload a new one.")
#         return cleaned_data
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if self.cleaned_data.get("existing_image"):
#             instance.image = self.cleaned_data["existing_image"].image
#         if commit:
#             instance.save()
#         return instance
#
# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1
#     form = ProductImageInlineForm
#     fields = ['existing_image', 'image', 'is_default']
#
#
# ##############################################
# # Product Admin Form (Excludes 'deleted_at' & Overrides Widgets)
# ##############################################
#
# class ProductAdminForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         exclude = ['deleted_at']  # Exclude the unwanted core field.
#         widgets = {
#             'name': forms.Textarea(attrs={'rows': 3}),
#             'description': forms.Textarea(attrs={'rows': 3}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if 'category' in self.data:
#             try:
#                 category_id = int(self.data.get('category'))
#                 self.fields['product_company'].queryset = ProductCompany.objects.filter(category_id=category_id)
#             except (ValueError, TypeError):
#                 self.fields['product_company'].queryset = ProductCompany.objects.none()
#         elif self.instance.pk:
#             self.fields['product_company'].queryset = ProductCompany.objects.filter(category=self.instance.category)
#         else:
#             self.fields['product_company'].queryset = ProductCompany.objects.none()
#
#
# ##############################################
# # Admin Registrations
# ##############################################
#
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     form = ProductAdminForm
#     list_display = ['name', 'description', 'price', 'category', 'product_company', 'is_published']
#     search_fields = ['name', 'description']
#     list_filter = ['price', 'category', 'product_company', 'is_published']
#     inlines = [ProductImageInline, ProductSpecificationsInline]
#
#     class Media:
#         js = ('admin/js/product_admin.js',)  # Optional: Include JS for dynamic filtering enhancements.
#
#
# @admin.register(ProductCategory)
# class ProductCategoryAdmin(admin.ModelAdmin):
#     form = ProductCategoryAdminForm
#     list_display = ['category_name', 'category_image']
#     search_fields = ['category_name']
#
#
# @admin.register(ProductCompany)
# class ProductCompanyAdmin(admin.ModelAdmin):
#     form = ProductCompanyAdminForm
#     list_display = ['name', 'category']
#     search_fields = ['name']
#     list_filter = ['category']
#
#
# @admin.register(ProductImage)
# class ProductImageAdmin(admin.ModelAdmin):
#     form = ProductImageAdminForm
#     list_display = ['product', 'image', 'is_default']
#     list_filter = ['is_default']
#
#
# @admin.register(ProductSpecifications)
# class ProductSpecificationsAdmin(admin.ModelAdmin):
#     form = ProductSpecificationsAdminForm
#     list_display = ['product', 'specification']



#
#
#
# from django.contrib import admin
# from django import forms
# from .models import (
#     Product,
#     ProductCategory,
#     ProductCompany,
#     ProductImage,
#     ProductSpecifications,
# )
#
# ##############################################
# # Custom Admin Forms for Excluding Core Fields
# ##############################################
#
# class ProductCategoryAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductCategory
#         fields = ['category_name', 'category_image']
#
#
# class ProductSpecificationsAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductSpecifications
#         fields = ['product', 'specification']
#
#
# class ProductCompanyAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductCompany
#         fields = ['name', 'category']
#
#
# class ProductImageAdminForm(forms.ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = ['product', 'image', 'is_default']
#
#
# ##############################################
# # Inline Forms
# ##############################################
#
# class ProductSpecificationsInlineForm(forms.ModelForm):
#     new_specification = forms.CharField(
#         required=False,
#         label="New Specification",
#         widget=forms.TextInput(attrs={'placeholder': 'Enter new specification if not listed'})
#     )
#
#     class Meta:
#         model = ProductSpecifications
#         fields = ['specification', 'new_specification']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Get distinct, nonempty specification values from the database
#         specs = ProductSpecifications.objects.exclude(specification__isnull=True)\
#                                              .exclude(specification__exact='')\
#                                              .values_list('specification', flat=True).distinct()
#         choices = [('', '---------')] + [(spec, spec) for spec in specs]
#         self.fields['specification'].widget = forms.Select(choices=choices)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         new_spec = cleaned_data.get("new_specification", "").strip()
#         # If a new specification is provided, override the dropdown value
#         if new_spec:
#             cleaned_data["specification"] = new_spec
#         if not cleaned_data.get("specification"):
#             raise forms.ValidationError("Please select an existing specification or add a new one.")
#         return cleaned_data
#
# class ProductSpecificationsInline(admin.TabularInline):
#     model = ProductSpecifications
#     extra = 1
#     form = ProductSpecificationsInlineForm
#     fields = ['specification', 'new_specification']
#
#
# # class ProductImageInlineForm(forms.ModelForm):
# #     existing_image = forms.ModelChoiceField(
# #         queryset=ProductImage.objects.all(),
# #         required=False,
# #         label="Select Existing Image",
# #         help_text="Choose an already uploaded image (or leave blank to upload a new one)."
# #     )
# #
# #     class Meta:
# #         model = ProductImage
# #         fields = ['existing_image', 'image', 'is_default']
# #
# #     def clean(self):
# #         cleaned_data = super().clean()
# #         existing = cleaned_data.get("existing_image")
# #         new_upload = cleaned_data.get("image")
# #         if existing and new_upload:
# #             raise forms.ValidationError("Please select either an existing image or upload a new one, not both.")
# #         if not existing and not new_upload:
# #             raise forms.ValidationError("Please select an existing image or upload a new one.")
# #         return cleaned_data
# #
# #     def save(self, commit=True):
# #         instance = super().save(commit=False)
# #         if self.cleaned_data.get("existing_image"):
# #             instance.image = self.cleaned_data["existing_image"].image
# #         if commit:
# #             instance.save()
# #         return instance
#
# class ProductImageInlineForm(forms.ModelForm):
#     existing_image = forms.ModelChoiceField(
#         queryset=ProductImage.objects.all(),
#         required=False,
#         label="Select Existing Image",
#         help_text="Choose an already uploaded image or leave blank to upload a new one."
#     )
#
#     class Meta:
#         model = ProductImage
#         fields = ['existing_image', 'image', 'is_default']
#
#     def clean(self):
#         cleaned_data = super().clean()
#         existing = cleaned_data.get("existing_image")
#         new_upload = cleaned_data.get("image")
#
#         # New inline (no primary key yet)
#         if not self.instance.pk:
#             if existing and new_upload:
#                 raise forms.ValidationError(
#                     "Please select either an existing image or upload a new one, not both."
#                 )
#             if not existing and not new_upload:
#                 raise forms.ValidationError(
#                     "Please select an existing image or upload a new one."
#                 )
#         else:
#             # Existing inline: allow the user to keep the old image
#             if existing and new_upload:
#                 raise forms.ValidationError(
#                     "Please select either an existing image or upload a new one, not both."
#                 )
#
#         return cleaned_data
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         existing = self.cleaned_data.get("existing_image")
#         new_upload = self.cleaned_data.get("image")
#
#         if existing:
#             # If the user chose an existing image, override
#             instance.image = existing.image
#         # If new_upload is set, instance.image is updated from the form
#         # If both are empty and it's an existing record, we keep the old file
#
#         if commit:
#             instance.save()
#         return instance
#
#
# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1
#     form = ProductImageInlineForm
#     fields = ['existing_image', 'image', 'is_default']
#
#
# ##############################################
# # Product Admin Form (Excludes 'deleted_at' & Overrides Widgets)
# ##############################################
#
# class ProductAdminForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         exclude = ['deleted_at']  # Exclude the unwanted core field.
#         widgets = {
#             'name': forms.Textarea(attrs={'rows': 3}),
#             'description': forms.Textarea(attrs={'rows': 3}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Load all ProductCompany instances manually without filtering by category.
#         self.fields['product_company'].queryset = ProductCompany.objects.all()
#
#
# ##############################################
# # Admin Registrations
# ##############################################
#
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     form = ProductAdminForm
#     list_display = ['name', 'description', 'price', 'category', 'product_company', 'is_published']
#     search_fields = ['name', 'description']
#     list_filter = ['price', 'category', 'product_company', 'is_published']
#     inlines = [ProductImageInline, ProductSpecificationsInline]
#     # Removed the dynamic filtering JavaScript since it's not needed.
#
# @admin.register(ProductCategory)
# class ProductCategoryAdmin(admin.ModelAdmin):
#     form = ProductCategoryAdminForm
#     list_display = ['category_name', 'category_image']
#     search_fields = ['category_name']
#
# @admin.register(ProductCompany)
# class ProductCompanyAdmin(admin.ModelAdmin):
#     form = ProductCompanyAdminForm
#     list_display = ['name', 'category']
#     search_fields = ['name']
#     list_filter = ['category']
#
# @admin.register(ProductImage)
# class ProductImageAdmin(admin.ModelAdmin):
#     form = ProductImageAdminForm
#     list_display = ['product', 'image', 'is_default']
#     list_filter = ['is_default']
#
# @admin.register(ProductSpecifications)
# class ProductSpecificationsAdmin(admin.ModelAdmin):
#     form = ProductSpecificationsAdminForm
#     list_display = ['product', 'specification']



from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    Product,
    ProductCategory,
    ProductCompany,
    ProductImage,
    ProductSpecifications,
)

##############################################
# Custom Admin Forms for Excluding Core Fields
##############################################

class ProductCategoryAdminForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['category_name', 'category_image']


class ProductSpecificationsAdminForm(forms.ModelForm):
    class Meta:
        model = ProductSpecifications
        fields = ['product', 'specification']


class ProductCompanyAdminForm(forms.ModelForm):
    class Meta:
        model = ProductCompany
        fields = ['name', 'category', 'company_image']


class ProductImageAdminForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['product', 'image', 'is_default']


##############################################
# Inline Forms
##############################################

class ProductSpecificationsInlineForm(forms.ModelForm):
    """
    Inline form for ProductSpecifications using a textarea for the specification.
    """
    class Meta:
        model = ProductSpecifications
        fields = ['specification']
        widgets = {
            'specification': forms.Textarea(
                attrs={'rows': 5, 'placeholder': 'Enter detailed specification'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        spec = cleaned_data.get("specification", "").strip()
        if not spec:
            raise forms.ValidationError("Please enter a specification.")
        return cleaned_data


class ProductSpecificationsInline(admin.TabularInline):
    model = ProductSpecifications
    extra = 1
    form = ProductSpecificationsInlineForm
    fields = ['specification']


class ProductImageInlineForm(forms.ModelForm):
    """
    Inline form for ProductImage without an existing image dropdown.
    For new records, an image upload is required.
    For existing records, leaving 'image' blank keeps the current file.
    """
    class Meta:
        model = ProductImage
        fields = ['image', 'is_default']

    def clean(self):
        cleaned_data = super().clean()
        image_upload = cleaned_data.get("image")
        if not self.instance.pk and not image_upload:
            raise forms.ValidationError("Please upload an image for this new record.")
        return cleaned_data


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    form = ProductImageInlineForm
    fields = ['image', 'is_default']


##############################################
# Product Admin Form (Excludes 'deleted_at' & Overrides Widgets)
##############################################

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['deleted_at']  # Exclude the unwanted core field.
        widgets = {
            'name': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter detailed description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_company'].queryset = ProductCompany.objects.all()


##############################################
# Admin Registrations
##############################################

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'description', 'price', 'category', 'product_company', 'is_published']
    search_fields = ['name', 'description']
    list_filter = ['price', 'category', 'product_company', 'is_published']
    inlines = [ProductImageInline, ProductSpecificationsInline]


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    form = ProductCategoryAdminForm
    list_display = ['category_name', 'category_image']
    search_fields = ['category_name']


@admin.register(ProductCompany)
class ProductCompanyAdmin(admin.ModelAdmin):
    form = ProductCompanyAdminForm
    list_display = ['name', 'category', 'company_image_preview']
    search_fields = ['name']
    list_filter = ['category']

    def company_image_preview(self, obj):
        if obj.company_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.company_image.url)
        return "-"
    company_image_preview.short_description = "Image"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    form = ProductImageAdminForm
    list_display = ['product', 'image', 'is_default']
    list_filter = ['is_default']


@admin.register(ProductSpecifications)
class ProductSpecificationsAdmin(admin.ModelAdmin):
    form = ProductSpecificationsAdminForm
    list_display = ['product', 'specification']
