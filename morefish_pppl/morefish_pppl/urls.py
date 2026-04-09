"""
URL configuration for morefish_pppl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from morefish_pppl import settings
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView
from rest_framework.routers import DefaultRouter


admin.site.site_header = 'Morefish Dashboard'
admin.site.site_title = 'Morefish Dashboard'
admin.site.index_title = 'Morefish'

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('auth/',include("users.urls")),
    path('assets/', include("assets.urls")),
    path('devices/', include("device.urls")),
    path('notification/', include("notification.urls")),
    path('product/',include('store.product.urls')),
    path('cart/',include('store.cart.urls')),
    path('order/',include('store.order.urls')),
    path('settings/',include('settings.urls')),
    path('api/schema',SpectacularAPIView.as_view(),name='schema'),
    path('api/schema/docs',SpectacularSwaggerView.as_view(url_name="schema")),
    
    path("poultry_care/", include("poultry_care.urls")),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(
        path('__debug__/', include(debug_toolbar.urls)),
        # Your other URL patterns go here
    )