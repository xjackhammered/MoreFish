from django.urls import path
from .views import (
    PoultryFarmListView,
    PoultryFarmDashboardView,
    PoultrySensorListView,
    PoultryDataGraphView,
    PoultryLatestReadingsView,
    PoultryNotificationListView,
    PoultryNotificationMarkReadView,
)

urlpatterns = [
    # Farm
    path('farms/list/',       PoultryFarmListView.as_view(),      name='poultry-farm-list'),
    path('farms/dashboard/',  PoultryFarmDashboardView.as_view(), name='poultry-farm-dashboard'),

    # Sensors
    path('sensor/list/',      PoultrySensorListView.as_view(),    name='poultry-sensor-list'),

    # Chart data
    path('data/graph/',       PoultryDataGraphView.as_view(),     name='poultry-data-graph'),

    # Latest reading snapshot (original endpoint — now enriched)
    path('api/latest-readings/', PoultryLatestReadingsView.as_view(), name='poultry-latest-readings'),

    # Notifications
    path('notifications/',              PoultryNotificationListView.as_view(),     name='poultry-notifications'),
    path('notifications/mark-read/',    PoultryNotificationMarkReadView.as_view(), name='poultry-notifications-mark-read'),
]