from django.db.models import Q
from .models import PoultryFarm, Device, SensorConfig, PoultryDeviceData


class PoultryService:

    @staticmethod
    def get_farm_list(user, company_id=None):
        if user.user_type == 1:  
            qs = PoultryFarm.objects.filter(company=user.company)
        else:
            qs = PoultryFarm.objects.filter(users=user)
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs.values('id', 'name', 'location')

    @staticmethod
    def get_farm_dashboard(farm_id, user):
        farm = PoultryFarm.objects.get(id=farm_id)
        device = getattr(farm, 'device', None)
        if not device:
            return {
                'farm_id': farm.id,
                'farm_name': farm.name,
                'device': None
            }

        latest_data = {
            d.sensor_id: d.value
            for d in PoultryDeviceData.objects.filter(device=device).select_related('sensor')
        }

        configs = SensorConfig.objects.filter(device=device).select_related('sensor')
        sensors = []
        for cfg in configs:
            sensor = cfg.sensor
            value = latest_data.get(sensor.id)
            danger_status = 'perfect'
            if value is not None:
                try:
                    fval = float(value)
                    if (sensor.min_invalid is not None and fval < sensor.min_invalid) or \
                       (sensor.max_invalid is not None and fval > sensor.max_invalid):
                        danger_status = 'invalid'
                    elif fval > sensor.max_value:
                        danger_status = 'danger'
                    elif fval < sensor.min_value:
                        danger_status = 'danger'
                except (TypeError, ValueError):
                    pass

            sensors.append({
                'sensor_id': sensor.id,
                'name': sensor.name,
                'unit': sensor.unit,
                'last_value': str(value) if value is not None else 'No data',
                'danger_status': danger_status,
                'data_time': device.latest_reading_timestamp.strftime('%d %b %Y %I:%M %p') if device.latest_reading_timestamp else '',
                'sensor_status': cfg.sensor_status,
            })

        device_status_label = {0: 'Offline', 1: 'Online', 2: 'Problem'}.get(device.dev_status, 'Unknown')
        return {
            'farm_id': farm.id,
            'farm_name': farm.name,
            'device': {
                'device_id': device.id,
                'device_name': device.name or device.client_id,
                'device_status': device_status_label,
                'client_id': device.client_id,
                'sensors': sensors,
            }
        }