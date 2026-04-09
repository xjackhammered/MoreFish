from django.urls import path

from store.product.views import CategoryList, ProductDetails, ProductList, SearchProductByCategory, \
    ProductCompanyByCategoryAPIView, SearchProductByCompany

urlpatterns = [
    path('category/list/',CategoryList.as_view()),
    path('list/',ProductList.as_view()),
    path('category/list/search/',SearchProductByCategory.as_view()),
    path('details/',ProductDetails.as_view()),
    path('product-companies/', ProductCompanyByCategoryAPIView.as_view(), name='product-company-by-category'),

    path('search-product-by-company/', SearchProductByCompany.as_view(), name='search-product-by-company'),

]
