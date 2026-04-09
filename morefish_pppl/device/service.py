import time
from typing import Dict, List
import typing
from assets.models import AssetsProperties
from device.models import Device, DeviceData, InvalidValue, SensorConfiguration, Weather
from device.serializers import WeatherSerializer
from users.models import User
from django.db.models import Prefetch,QuerySet
from django.core.exceptions import ObjectDoesNotExist

class DeviceService():
    
    
    @staticmethod
    def get_asset_list(user:User,company_id:str=None):
        user_assets = []
        if company_id:
            
            user_assets = AssetsProperties.objects.filter(
                            company_id=company_id,
                        ).values("id","ast_name")
        
        else:
            
            user_assets = AssetsProperties.objects.filter(
                            ast_user=user,company_id=user.company_id,
                        ).values("id","ast_name")
        return user_assets
    
    
            
    
    @staticmethod
    def __organize_dashboard_data(user_assets:QuerySet)->List:
            weather = Weather.objects.filter(weather_district_id=user_assets.district_id).order_by('id').last()
            serialized_weather = WeatherSerializer(weather,many=False)
            
            asset_data = {
                "weather": serialized_weather.data,
                "asset_id": user_assets.id,
                "asset_name": user_assets.ast_name,
                "devices": []
            }

            try:
                device_data = {
                    "device_id": user_assets.device_asset.id,
                    "device_name": user_assets.device_asset.dev_name,
                    "device_status":user_assets.device_asset.get_dev_status_display(),
                    "sensors": []
                }
                                    
                # Fetch the last device data for each sensor
                last_device_data_by_sensor = {
                    sensor_config.id: user_assets.device_asset.device_data.filter(dvd_sen=sensor_config.sensor).values("id",'dvd_dev','dvd_sen','dvd_val','dvd_created_at').order_by('-id').first()
                    for sensor_config in user_assets.device_asset.sensorconfiguration_set.all()
                }
                

                for sensor_config in user_assets.device_asset.sensorconfiguration_set.all():
                    dev_sen_start_time = time.time()

                    last_data = last_device_data_by_sensor.get(sensor_config.id)
                    invalid_sensor_data = InvalidValue.objects.get(sensor_id=sensor_config.sensor_id)
                    last_dev_data = last_data['dvd_val'] if last_data else "No data recieved yet"
                    
                    try:
                        if last_data:
                            if float(last_data['dvd_val'])>invalid_sensor_data.max_invalid_value or float(last_data['dvd_val'])<invalid_sensor_data.min_invalid_value:
                                last_dev_data = "Invalid Data"
                    except ValueError:
                            last_dev_data = last_data['dvd_val'] if last_data else "No data recieved yet"
                    
                    
                    try:
                        if last_data:
                            if float(last_data['dvd_val'])>sensor_config.sensor.sensor_max or float(last_data['dvd_val'])<sensor_config.sensor.sensor_min:
                                val_status = "danger"
                            else:
                                val_status = "perfect"
                        else:
                            val_status = "invalid"
                    except ValueError:
                        val_status = "invalid"
                    sensor_data = {
                        "sensor_id": sensor_config.id,
                        "sensor_name": sensor_config.sensor.sensor_name,
                        "last_value": last_dev_data,
                        "sensor_unit": sensor_config.sensor.sensor_unit if sensor_config.sensor.sensor_unit else "",
                        "danger_status":val_status,
                        "sensor_icon":sensor_config.sensor.sensor_icon.url if sensor_config.sensor.sensor_icon else "",
                        "data_time":last_data['dvd_created_at'].strftime("%d %b %Y %I:%M %p") if last_data else "No data recieved yet",
                        "sensor_status":sensor_config.get_sensor_status_display(),
                    }

                    device_data["sensors"].append(sensor_data)
                    dev_sen_end_time = time.time()
                    print(f"dev sen duration {dev_sen_end_time-dev_sen_start_time}")

                asset_data["devices"].append(device_data)
            except Device.DoesNotExist:
                pass
            
        
            return asset_data
    
    @staticmethod
    def get_asset_data(asset_id:str,user:User,company_id:str=None) -> typing.Dict:
        if user.user_type == 1:
            
            print("ORGANIZATION")
            user_assets = AssetsProperties.objects.prefetch_related(
                            Prefetch(
                                "device_asset",
                                queryset=Device.objects.select_related("dev_dvg").prefetch_related(
                                    Prefetch("sensorconfiguration_set", queryset=SensorConfiguration.objects.select_related("sensor").all()),
                                    Prefetch("device_data", queryset=DeviceData.objects.filter(company_id=user.company_id).select_related('dvd_sen')),
                                ).filter(company_id=user.company_id),
                            )
                        ).get(
                            company_id=company_id, id=asset_id
                        )
        
        if user.user_type == 3:
            
            user_assets = AssetsProperties.objects.prefetch_related(
                            Prefetch(
                                "device_asset",
                                queryset=Device.objects.select_related("dev_dvg").prefetch_related(
                                    Prefetch("sensorconfiguration_set", queryset=SensorConfiguration.objects.select_related("sensor").all()),
                                    Prefetch("device_data", queryset=DeviceData.objects.filter(asset_id=asset_id).select_related('dvd_sen')),
                                ),
                            )
                        ).get(
                            ast_user=user, id=asset_id
                        )
        result_data = DeviceService.__organize_dashboard_data(user_assets=user_assets)
        return result_data
        
    @staticmethod
    def dashboard_data(user:User,company_id:str=None):
                
        user_assets = DeviceService.get_asset_data(user=user,company_id=company_id)
            
        result_data = DeviceService.__organize_dashboard_data(user_assets=user_assets)
        return result_data
            