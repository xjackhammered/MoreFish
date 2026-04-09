import sys
from datetime import datetime, timedelta
from django.db.models import Max

from .models import Device, PoultryFarm, Sensor, SensorConfig, SensorReading

RANGE_SWITCHER = {
    'daily':      1,
    'weekly':     7,
    'monthly':    30,
    'half-yearly': 182,
    'yearly':     365,
}


def _base_dict(farm: PoultryFarm, sensor_name: str) -> dict:
    return {
        'farm_id':    farm.id,
        'farm_name':  farm.name,
        'sensor_key': sensor_name,
        'sensor_name': sensor_name,
        'unit':       '',
        'sensor_val': [],
        'time':       [],
        'date_time':  '',
    }


def _enrich_with_config(d: dict, device: Device, sensor_name: str):
    """Pull unit from Sensor via SensorConfig."""
    config = SensorConfig.objects.filter(
        device=device, sensor__name=sensor_name
    ).select_related('sensor').first()
    if config:
        d['unit'] = config.sensor.unit or ''
        # Optionally set display name if you add that field later
        d['sensor_name'] = config.sensor.name


# ─── DAILY ───────────────────────────────────────────────────────────────────
def get_daily_data(farm_id: int, sensor_name: str) -> list:
    try:
        farm   = PoultryFarm.objects.get(id=farm_id)
        device = farm.device
        d = _base_dict(farm, sensor_name)
        _enrich_with_config(d, device, sensor_name)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        qs = SensorReading.objects.filter(device=device, timestamp__gte=today).order_by('timestamp')
        count = qs.count()

        for idx, r in enumerate(qs):
            val = getattr(r, sensor_name, None)
            d['sensor_val'].append(str(round(float(val), 4)) if val is not None else '0')
            d['time'].append(r.timestamp.strftime('%I:%M %p'))
            if idx == count - 1:
                d['date_time'] = r.timestamp.strftime('%I:%M:%S %p , %d %b %Y')

        return [d]
    except Exception as e:
        return [{'error': f'line {sys.exc_info()[-1].tb_lineno}: {e}'}]


# ─── WEEKLY (3-hour sampled) ─────────────────────────────────────────────────
def get_weekly_data(farm_id: int, sensor_name: str, range_type: str = 'weekly') -> list:
    try:
        farm   = PoultryFarm.objects.get(id=farm_id)
        device = farm.device
        d = _base_dict(farm, sensor_name)
        _enrich_with_config(d, device, sensor_name)

        days     = RANGE_SWITCHER.get(range_type, 7)
        interval = timedelta(hours=3)

        for x in range(days, 0, -1):
            start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=x)
            end   = start.replace(hour=23, minute=59, second=59)
            day_qs = SensorReading.objects.filter(device=device, timestamp__range=[start, end])

            d['time'].append(end.strftime('%a'))

            current = start
            while current <= end:
                interval_end = current + interval
                reading = day_qs.filter(timestamp__range=[current, interval_end]).first()
                val = getattr(reading, sensor_name, None) if reading else None
                d['sensor_val'].append(str(round(float(val), 4)) if val is not None else '0')
                d['time'].append('')
                current = interval_end

            if x == 1:
                d['time'].pop()
                d['date_time'] = end.strftime('%a, %d %b %Y')

        return [d]
    except Exception as e:
        return [{'error': f'line {sys.exc_info()[-1].tb_lineno}: {e}'}]


# ─── MONTHLY (daily max) ─────────────────────────────────────────────────────
def get_monthly_data(farm_id: int, sensor_name: str, date_range: int = 30) -> list:
    try:
        farm   = PoultryFarm.objects.get(id=farm_id)
        device = farm.device
        d = _base_dict(farm, sensor_name)
        _enrich_with_config(d, device, sensor_name)

        increment = {30: -1, 180: -30}.get(date_range, -1)

        for x in range(date_range, 0, increment):
            start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=x)
            end   = start.replace(hour=23, minute=59, second=59)

            agg = SensorReading.objects.filter(
                device=device, timestamp__range=[start, end]
            ).aggregate(max_val=Max(sensor_name))

            val = agg['max_val']
            d['sensor_val'].append(str(round(float(val), 4)) if val is not None else '0')
            d['time'].append(
                start.strftime('%b %d') + '–' + end.strftime('%b %d')
                if date_range == 180
                else end.strftime('%m/%d/%y')
            )
            if x == 1:
                d['date_time'] = end.strftime('%m/%d/%y')

        seen, deduped = set(), []
        for t in d['time']:
            if t not in seen:
                seen.add(t)
                deduped.append(t)
        d['time'] = deduped

        return [d]
    except Exception as e:
        return [{'error': f'line {sys.exc_info()[-1].tb_lineno}: {e}'}]


# ─── YEARLY (monthly max) ─────────────────────────────────────────────────────
def get_yearly_data(farm_id: int, sensor_name: str, range_type: str = 'yearly') -> list:
    def month_names(n):
        now = datetime.now()
        result = [{'month': now.strftime('%m'), 'year': now.strftime('%Y'), 'label': now.strftime('%b %y')}]
        for _ in range(n):
            now = now.replace(day=1) - timedelta(days=1)
            result.append({'month': now.strftime('%m'), 'year': now.strftime('%Y'), 'label': now.strftime('%b %y')})
        return result[::-1]

    try:
        farm   = PoultryFarm.objects.get(id=farm_id)
        device = farm.device
        d = _base_dict(farm, sensor_name)
        _enrich_with_config(d, device, sensor_name)

        months = month_names(11 if range_type == 'yearly' else 5)

        for idx, m in enumerate(months):
            agg = SensorReading.objects.filter(
                device=device,
                timestamp__month=m['month'],
                timestamp__year=m['year'],
            ).aggregate(max_val=Max(sensor_name))

            val = agg['max_val']
            d['sensor_val'].append(str(round(float(val), 4)) if val is not None else '0')
            d['time'].append(m['label'])
            if idx == len(months) - 1:
                d['date_time'] = m['label']

        return [d]
    except Exception as e:
        return [{'error': f'line {sys.exc_info()[-1].tb_lineno}: {e}'}]