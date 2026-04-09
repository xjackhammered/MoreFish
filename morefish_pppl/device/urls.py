from django.urls import path
#
from .views import ComplainCategoryView, ComplainListView, ComplainSubmitView, DeviceDataSet, \
    DeviceIndividualSensorData, DownloadCSVView, DownloadExcelAssetDataView, GenerateAssetDataExcel, GenerateCSVAPIView, \
    GetDevicesForCompanyView, PondData, PondList, SensorList, UserManualDataAPIView, UserManualDataListAPIView, \
    WeatherReportView, DataHistoryPondWise, AssetsListWithData, DeviceListWithData, CameraListWithAssets, \
    MachineControl, MachineList, AeratorCommandAPI

urlpatterns = [
    path('data/pond/list',PondList.as_view()),

    # app dashboard realtime data
    path('data/pond/data',PondData.as_view()),

    path('data/with/assets/', AssetsListWithData.as_view()),
    path('sensor/list/',SensorList.as_view()),
    path('machine/control/', MachineControl.as_view()),
    path('machine/list/', MachineList.as_view()),
    path('camera/list/with/assets/', CameraListWithAssets.as_view()),
    path('list/with/data/', DeviceListWithData.as_view()),
    path('individula/sensor/data/<str:pond>/', DeviceIndividualSensorData.as_view()),
    path('data/graph/', DeviceDataSet.as_view()),
    path('data/history/<str:pond>/', DataHistoryPondWise.as_view()),
    path('weather/report/', WeatherReportView.as_view()),
    path('user-manual-data/', UserManualDataAPIView.as_view(), name='user-manual-data'),
    path('manual-data-list/', UserManualDataListAPIView.as_view(), name='user-manual-data-list'),
    path('generate-csv/', GenerateCSVAPIView.as_view(), name='generate-csv'),
    path('complain/submit/', ComplainSubmitView.as_view()),
    path('complain/list/', ComplainListView.as_view()),
    path('complain/category/', ComplainCategoryView.as_view()),
    path('MoreFish_Report/<str:file_name>/', DownloadCSVView.as_view(), name='csv-download'),
    path('get-devices-for-company/', GetDevicesForCompanyView.as_view(), name='get_devices_for_company'),
    path('generate/devicedata/report/', GenerateAssetDataExcel.as_view(), name='generate-csv'),
    path('Morefish_Asset_report/<str:start_date>/<str:end_date>/<str:file_name>/', DownloadExcelAssetDataView.as_view(), name='download-excel-assetwisedata'),

    # aerator control
    path('aerators/command/', AeratorCommandAPI.as_view(), name='aerator-command'),
]    

