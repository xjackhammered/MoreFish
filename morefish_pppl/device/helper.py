import sys
from datetime import datetime, timedelta
from decimal import Decimal

import pytz
from django.db.models import Max, Subquery, Min
from django.db.models.functions import TruncMonth
from pytz import timezone
from assets.models import AssetsProperties
from device.models import DeviceDataHistory, InvalidValue

# from device.models import DeviceDataHistory, ProblemDevices, Sensor
from device.serializers import DeviceDataSerializer
from helper import unique
from users.models import User


def pond_wise_devices_daily_data(
    asset_id, request=None, user: User = None, company: int = None, sensor_id:str=None 
):
    
    try:
        result = list()
        temp_dict = {
            "asset_id": asset_id,
            "asset_name": AssetsProperties.objects.get(id=asset_id).ast_name,
            "sensor_val": list(),
            "sensor_name":"",
            "time": list(),
            "date_time": "",
        }
        
        invalid_values = InvalidValue.objects.first()

        if company:
            company_id = company
        else:
            company_id = user.company_id

        # device_data = DeviceDataHistory.objects.select_related('dvd_dev').filter(dvd_dev=device.id,dvd_created_at__gte=datetime.now()-timedelta(days=1)).order_by('dvd_created_at')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        device_data = (
            DeviceDataHistory.objects.select_related("dvd_dev","dvd_sen")
            .filter(
                asset_id=asset_id, dvd_created_at__gte=today, company_id=company_id, dvd_sen_id=sensor_id
            )
            .order_by("dvd_created_at")
        )
        if device_data:
            temp_dict["sensor_name"] = device_data.first().dvd_sen.sensor_name
        for idx, data in enumerate(device_data):
            temp_dict["sensor_val"].append(str(round(float(data.dvd_val), 4)))
            temp_dict["time"].append(data.dvd_created_at.strftime("%I:%M %p"))
            if idx == len(device_data) - 1:
                temp_dict["date_time"] = data.dvd_created_at.strftime(
                    "%I:%M:%S %p , %d %b %Y"
                )

        result.append(temp_dict)
        return result
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def pond_wise_devices_sensors_daily_data(devices, request=None):
    try:
        florida = timezone("Asia/Dhaka")
        florida_time = datetime.now(florida)
        time_stamp = florida_time.strftime("%Y-%m-%d %H:%M:%S")
        yesterday = datetime.today() - timedelta(days=1)
        before_date = yesterday.strftime("%Y-%m-%d %H:%M:%S")

        ph_result = list()
        temp_result = list()
        tds_result = list()
        all_device_data = []
        sensors = ["ph", "tds", "temp"]
        for sensor in sensors:
            for device in devices:
                if sensor == "ph":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "ph": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    device_data = DeviceDataHistory.objects.filter(
                        dvd_dev_id=device.id,
                        dvd_created_at__range=(before_date, time_stamp),
                    )
                    for idx, data in enumerate(device_data):
                        temp_dict["ph"].append(data.dvd_ph)
                        temp_dict["time"].append(
                            data.dvd_created_at.strftime("%I:%M %p")
                        )
                        if idx == len(device_data) - 1:
                            temp_dict["date_time"] = data.dvd_created_at.strftime(
                                "%I:%M:%S %p , %d %b %Y"
                            )

                    ph_result.append(temp_dict)

                if sensor == "temp":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "temp": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    device_data = DeviceDataHistory.objects.filter(
                        dvd_dev_id=device.id,
                        dvd_created_at__range=(before_date, time_stamp),
                    )
                    for idx, data in enumerate(device_data):
                        temp_dict["temp"].append(data.dvd_temp)
                        temp_dict["time"].append(
                            data.dvd_created_at.strftime("%I:%M %p")
                        )
                        if idx == len(device_data) - 1:
                            temp_dict["date_time"] = data.dvd_created_at.strftime(
                                "%I:%M:%S %p , %d %b %Y"
                            )

                    temp_result.append(temp_dict)
                if sensor == "tds":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "tds": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    device_data = DeviceDataHistory.objects.filter(
                        dvd_dev_id=device.id,
                        dvd_created_at__range=(before_date, time_stamp),
                    )
                    for idx, data in enumerate(device_data):
                        temp_dict["tds"].append(data.dvd_tds)
                        temp_dict["time"].append(
                            data.dvd_created_at.strftime("%I:%M %p")
                        )
                        if idx == len(device_data) - 1:
                            temp_dict["date_time"] = data.dvd_created_at.strftime(
                                "%I:%M:%S %p , %d %b %Y"
                            )

                    tds_result.append(temp_dict)

        sensor_data = {"PH": ph_result, "TEMP": temp_result, "TDS": tds_result}

        return sensor_data
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def pond_wise_devices_sensors_weekly_data(devices, type):
    try:
        switcher = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "half-yearly": 182,
            "yearly": 365,
        }

        ph_result = list()
        temp_result = list()
        tds_result = list()
        all_device_data = []
        sensors = ["ph", "tds", "temp"]
        for sensor in sensors:
            for device in devices:
                if sensor == "ph":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "ph": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for x in range(switcher.get(type), 0, -1):
                        start = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ) - timedelta(days=x)
                        end = start.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id, dvd_created_at__range=[start, end]
                            )
                            .aggregate(Max("dvd_ph"))
                        )
                        temp_dict["ph"].append(
                            {True: "0", False: max_values["dvd_ph__max"]}[
                                max_values["dvd_ph__max"] == None
                            ]
                        )
                        temp_dict["time"].append(end.strftime("%a"))
                        if x == 1:
                            temp_dict["date_time"] = end.strftime("%a, %d %b %Y")

                    ph_result.append(temp_dict)

                if sensor == "temp":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "temp": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for x in range(switcher.get(type), 0, -1):
                        start = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ) - timedelta(days=x)
                        end = start.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id, dvd_created_at__range=[start, end]
                            )
                            .aggregate(Max("dvd_temp"))
                        )
                        temp_dict["temp"].append(
                            {True: "0", False: max_values["dvd_temp__max"]}[
                                max_values["dvd_temp__max"] == None
                            ]
                        )
                        temp_dict["time"].append(end.strftime("%a"))
                        if x == 1:
                            temp_dict["date_time"] = end.strftime("%a, %d %b %Y")

                    temp_result.append(temp_dict)

                if sensor == "tds":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "tds": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for x in range(switcher.get(type), 0, -1):
                        start = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ) - timedelta(days=x)
                        end = start.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id, dvd_created_at__range=[start, end]
                            )
                            .aggregate(Max("dvd_tds"))
                        )
                        temp_dict["tds"].append(
                            {True: "0", False: max_values["dvd_tds__max"]}[
                                max_values["dvd_tds__max"] == None
                            ]
                        )
                        temp_dict["time"].append(end.strftime("%a"))
                        if x == 1:
                            temp_dict["date_time"] = end.strftime("%a, %d %b %Y")

                    tds_result.append(temp_dict)

            sensor_data = {"PH": ph_result, "TEMP": temp_result, "TDS": tds_result}

        return sensor_data
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def pond_wise_devices_sensor_monthly_data(devices, date_range):
    try:
        increment_switcher = {"daily": 1, "weekly": 7, 30: -1, 180: -30, 365: -365}

        ph_result = list()
        temp_result = list()
        tds_result = list()
        all_device_data = []
        sensors = ["ph", "tds", "temp"]
        for sensor in sensors:
            for device in devices:
                if sensor == "ph":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "ph": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for x in range(date_range, 0, increment_switcher.get(date_range)):
                        start = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ) - timedelta(days=x)
                        end = start.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id, dvd_created_at__range=[start, end]
                            )
                            .aggregate(Max("dvd_ph"))
                        )
                        temp_dict["ph"].append(
                            {True: "0", False: max_values["dvd_ph__max"]}[
                                max_values["dvd_ph__max"] == None
                            ]
                        )
                        # temp_dict['temp'].append(
                        #     {True: '0', False: max_values['dvd_temp__max']}[max_values['dvd_temp__max'] == None])
                        # temp_dict['tds'].append(
                        #     {True: '0', False: max_values['dvd_tds__max']}[max_values['dvd_tds__max'] == None])

                        if date_range == 180:
                            temp_dict["time"].append(
                                start.strftime("%b %d") + "-" + end.strftime("%b %d")
                            )
                        elif date_range == 30:
                            temp_dict["time"].append(end.strftime("%D"))

                        if x == 1:
                            temp_dict["date_time"] = end.strftime("%a, %d %b %Y")

                    temp_dict["time"] = unique(temp_dict["time"])

                    ph_result.append(temp_dict)

                if sensor == "temp":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "temp": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for x in range(date_range, 0, increment_switcher.get(date_range)):
                        start = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ) - timedelta(days=x)
                        end = start.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id, dvd_created_at__range=[start, end]
                            )
                            .aggregate(Max("dvd_temp"))
                        )
                        temp_dict["temp"].append(
                            {True: "0", False: max_values["dvd_temp__max"]}[
                                max_values["dvd_temp__max"] == None
                            ]
                        )
                        if date_range == 180:
                            temp_dict["time"].append(
                                start.strftime("%b %d") + "-" + end.strftime("%b %d")
                            )
                        elif date_range == 30:
                            temp_dict["time"].append(end.strftime("%D"))

                        if x == 1:
                            temp_dict["date_time"] = end.strftime("%a, %d %b %Y")

                    temp_dict["time"] = unique(temp_dict["time"])
                    temp_result.append(temp_dict)

                if sensor == "tds":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "tds": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for x in range(date_range, 0, increment_switcher.get(date_range)):
                        start = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ) - timedelta(days=x)
                        end = start.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id, dvd_created_at__range=[start, end]
                            )
                            .aggregate(Max("dvd_tds"))
                        )
                        temp_dict["tds"].append(
                            {True: "0", False: max_values["dvd_tds__max"]}[
                                max_values["dvd_tds__max"] == None
                            ]
                        )

                        if date_range == 180:
                            temp_dict["time"].append(
                                start.strftime("%b %d") + "-" + end.strftime("%b %d")
                            )
                        elif date_range == 30:
                            temp_dict["time"].append(end.strftime("%D"))

                        if x == 1:
                            temp_dict["date_time"] = end.strftime("%a, %d %b %Y")

                    temp_dict["time"] = unique(temp_dict["time"])
                    tds_result.append(temp_dict)

        sensor_data = {"PH": ph_result, "TEMP": temp_result, "TDS": tds_result}

        return sensor_data
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def pond_wise_devices_weekly_data2(
    devices, type, user: User = None, company: int = None
):
    ph_problem_device = ""
    tds_problem_device = ""
    temp_problem_device = ""
    do_problem_device = ""
    ammonia_problem_device = ""
    alkalinity_problem_device = ""
    hardness_problem_device = ""
    invalid_values = InvalidValue.objects.first()
    print("LINE 526", devices)
    print("LINE 527", user)
    try:
        switcher = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "half-yearly": 182,
            "yearly": 365,
        }
        result = list()
        print("total devices", len(devices))
        for device in devices:
            temp_dict = {
                "device_id": device.id,
                "device_name": device.dev_name,
                "ph": list(),
                "temp": list(),
                "tds": list(),
                "ammonia": list(),
                "do": list(),
                "alkalinity": list(),
                "hardness": list(),
                "time": list(),
                "date_time": "",
            }
            if device.dev_status == 0:
                temp_dict["status"] = "Offline"
            elif device.dev_status == 1:
                temp_dict["status"] = "Online"
            elif device.dev_status == 2:
                temp_dict["status"] = "Problem"

            
            for x in range(switcher.get(type), 0, -1):
                start = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(days=x)
                end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                if company:
                    company_id = company
                else:
                    company_id = user.company_id
                print("LINE 606", company_id)
                max_values = (
                    DeviceDataHistory.objects.select_related("dvd_dev")
                    .filter(
                        dvd_dev=device.id,
                        company_id=company_id,
                        dvd_created_at__range=[start, end],
                    )
                    .aggregate(
                        Max("dvd_ph"),
                        Max("dvd_temp"),
                        Max("dvd_tds"),
                        Max("dvd_ammonia"),
                        Max("dvd_do"),
                        Max("dvd_alkalinity"),
                        Max("dvd_hardness"),
                    )
                )
                # print("LINE 622",max_values)
                # print(max_values)
                temp_dict["ph"].append(
                    {True: "0", False: max_values["dvd_ph__max"]}[
                        max_values["dvd_ph__max"] == None
                    ]
                )
                #### temp ####
                temp_dict["temp"].append(
                    {True: "0", False: max_values["dvd_temp__max"]}[
                        max_values["dvd_temp__max"] == None
                    ]
                )
                ###### tds ######
                temp_dict["tds"].append(
                    {True: "0", False: max_values["dvd_tds__max"]}[
                        max_values["dvd_tds__max"] == None
                    ]
                )
                ###### ammonia #######

                temp_dict["ammonia"].append(
                    {True: "0", False: max_values["dvd_ammonia__max"]}[
                        max_values["dvd_ammonia__max"] == None
                    ]
                )

                ######## do ##########
                temp_dict["do"].append(
                    {True: "0", False: max_values["dvd_do__max"]}[
                        max_values["dvd_do__max"] == None
                    ]
                )

                ########## hardness ########
                temp_dict["hardness"].append(
                    {True: "0", False: max_values["dvd_hardness__max"]}[
                        max_values["dvd_hardness__max"] == None
                    ]
                )

                ####### time #######
                temp_dict["time"].append(end.strftime("%a"))
                if x == 1:
                    temp_dict["date_time"] = end.strftime("%a, %d %b %Y")

            result.append(temp_dict)
        return result
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def pond_wise_devices_weekly_data(
    asset_id, type, user: User = None, company: int = None, sensor_id:str=None
):

    try:
        switcher = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "half-yearly": 182,
            "yearly": 365,
        }
        result = list()
        temp_dict = {
            "asset_id": asset_id,
            "asset_name": AssetsProperties.objects.get(id=asset_id).ast_name,
            "sensor_val":list(),
            "sensor_name":"",
            "time": list(),
            "date_time": "",
        }
            
        for x in range(switcher.get(type), 0, -1):
            start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=x)
            end = start.replace(hour=23, minute=59, second=59, microsecond=999999)

            interval = timedelta(hours=3)

            # Initialize the start time
            current_time = start
            if company:
                company_id = company
            else:
                company_id = user.company_id
            

            agg_values = DeviceDataHistory.objects.select_related("dvd_dev","dvd_sen").filter(
                asset_id=asset_id,
                company_id=company_id,
                dvd_created_at__range=[start, end],
                dvd_sen_id = sensor_id
            )
            
            if agg_values:
                temp_dict["sensor_name"] = agg_values.first().dvd_sen.sensor_name
            
            temp_dict["time"].append(end.strftime("%a"))
            
            while current_time <= end:
                # Calculate the end time of the 3-hour interval
                interval_end = current_time + interval

                # Filter the 'agg_values' queryset for the current 3-hour interval
                interval_data = agg_values.filter(
                    dvd_created_at__range=[current_time, interval_end]
                ).first()
                print("Interval data",interval_data)
                # Process the data for the current 3-hour interval
                val = interval_data
                # Process the data point as needed
                # data_point contains one data point within the current 3-hour interval
                if val is None:
                    print("VALUE IS NONE")

                
                if val is None:
                    temp_dict["sensor_val"].extend(["0"])
                else:
                    temp_dict["sensor_val"].extend([val.dvd_val])
                
                
                if x == 1:
                    temp_dict["date_time"] = end.strftime("%a, %d %b %Y")
                temp_dict["time"].append("")
                # Move to the next 3-hour interval
                current_time = interval_end
                print(current_time)
            temp_dict["time"].pop()
        result.append(temp_dict)
        return result
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def pond_wise_devices_monthly_data(
    asset_id, date_range, user: User = None, company: int = None, sensor_id:str=None
):
    
    try:
        print("range", date_range)
        increment_switcher = {"daily": 1, "weekly": 7, 30: -1, 180: -30, 365: -365}
        result = list()
        temp_dict = {
            "asset_id": asset_id,
            "asset_name": AssetsProperties.objects.get(id=asset_id).ast_name,
            "sensor_val": list(),
            "sensor_name":"",
            "time": list(),
            "date_time": "",
        }
            
        if company:
            company_id = company
        else:
            company_id = user.company_id

        for x in range(date_range, 0, increment_switcher.get(date_range)):
            start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=x)
            end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
            max_values = DeviceDataHistory.objects.select_related("dvd_dev","dvd_sen").filter(
                    asset_id=asset_id,
                    dvd_created_at__range=[start, end],
                    company_id=company_id,
                    dvd_sen_id = sensor_id
                )
            
            if max_values:
                temp_dict['sensor_name']=max_values.first().dvd_sen.sensor_name
            
            max_values = max_values.aggregate(
                    Max("dvd_val"),
                )
            
            
            ####### sensor value ########
            temp_dict["sensor_val"].append(
                {True: "0", False: max_values["dvd_val__max"]}[
                    max_values["dvd_val__max"] == None
                ]
            )

            
            ########## time ###########
            if date_range == 180:
                temp_dict["time"].append(
                    start.strftime("%b %d") + "-" + end.strftime("%b %d")
                )
            elif date_range == 30:
                temp_dict["time"].append(end.strftime("%D"))

            if x == 1:
                temp_dict["date_time"] = end.strftime("%D")

        temp_dict["time"] = unique(temp_dict["time"])
        result.append(temp_dict)
        return result
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def month_names(number):
    now = datetime.now()
    result = [
        {
            "month": now.strftime("%m"),
            "year": now.strftime("%Y"),
            "month_year": now.strftime("%b %y"),
        }
    ]
    for _ in range(0, number):
        now = now.replace(day=1) - timedelta(days=1)
        result.append(
            {
                "month": now.strftime("%m"),
                "year": now.strftime("%Y"),
                "month_year": now.strftime("%b %y"),
            }
        )

    return result[::-1]  # returning reversed array using slicing approach


def pond_wise_devices_yearly_data(
    asset_id, type, user: User = None, company: int = None, sensor_id:str=None
):
    
    try:
        months = month_names({True: 12, False: 6}[type == "yearly"])
        result = list()
        temp_dict = {
            "asset_id": asset_id,
            "asset_name": AssetsProperties.objects.get(id=asset_id).ast_name,
            "sensor_val": list(),
            "sensor_name":"",
            "time":list(),
            "date_time": "",
        }
        
        
        if company:
            company_id = company
        else:
            company_id = user.company_id

        for idx, x in enumerate(months):
            max_values = DeviceDataHistory.objects.select_related("dvd_dev","dvd_sen").filter(
                    asset_id=asset_id,
                    dvd_created_at__month=x["month"],
                    dvd_created_at__year=x["year"],
                    company_id=company_id,
                    dvd_sen_id = sensor_id
                )
            
            if max_values:
                temp_dict["sensor_name"] = max_values.first().dvd_sen.sensor_name
            
            max_values=max_values.values(
                    "dvd_val",
                ).aggregate(
                    Max("dvd_val"),
                )
            ########## sensor_val ###########
            temp_dict["sensor_val"].append(
                {True: "0", False: max_values["dvd_val__max"]}[
                    max_values["dvd_val__max"] == None
                ]
            )

            ######## time #########
            temp_dict["time"].append(x["month_year"])
            if idx == len(months) - 1:
                temp_dict["date_time"] = x["month_year"]
        result.append(temp_dict)
        return result
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response


def pond_wise_devices_sensor_yearly_data(devices, type):
    try:
        months = month_names({True: 12, False: 6}[type == "yearly"])

        ph_result = list()
        temp_result = list()
        tds_result = list()
        all_device_data = []
        sensors = ["ph", "tds", "temp"]
        for sensor in sensors:
            for device in devices:
                if sensor == "ph":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "ph": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for idx, x in enumerate(months):
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id,
                                dvd_created_at__month=x["month"],
                                dvd_created_at__year=x["year"],
                            )
                            .values("dvd_ph", "dvd_created_at")
                            .aggregate(Max("dvd_ph"))
                        )
                        temp_dict["ph"].append(
                            {True: "0", False: max_values["dvd_ph__max"]}[
                                max_values["dvd_ph__max"] == None
                            ]
                        )
                        temp_dict["time"].append(x["month_year"])
                        if idx == len(months) - 1:
                            temp_dict["date_time"] = x["month_year"]

                    ph_result.append(temp_dict)

                if sensor == "temp":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "temp": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for idx, x in enumerate(months):
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id,
                                dvd_created_at__month=x["month"],
                                dvd_created_at__year=x["year"],
                            )
                            .values("dvd_temp", "dvd_created_at")
                            .aggregate(Max("dvd_temp"))
                        )
                        temp_dict["temp"].append(
                            {True: "0", False: max_values["dvd_temp__max"]}[
                                max_values["dvd_temp__max"] == None
                            ]
                        )
                        temp_dict["time"].append(x["month_year"])
                        if idx == len(months) - 1:
                            temp_dict["date_time"] = x["month_year"]
                    temp_result.append(temp_dict)

                if sensor == "tds":
                    temp_dict = {
                        "device_id": device.id,
                        "device_name": device.dev_name,
                        "device_location": device.dev_location,
                        "tds": list(),
                        "time": list(),
                        "date_time": "",
                    }
                    if device.dev_status == 0:
                        temp_dict["status"] = "Offline"
                    elif device.dev_status == 1:
                        temp_dict["status"] = "Online"
                    elif device.dev_status == 2:
                        temp_dict["status"] = "Problem"

                    for idx, x in enumerate(months):
                        max_values = (
                            DeviceDataHistory.objects.select_related("dvd_dev")
                            .filter(
                                dvd_dev=device.id,
                                dvd_created_at__month=x["month"],
                                dvd_created_at__year=x["year"],
                            )
                            .values("dvd_tds", "dvd_created_at")
                            .aggregate(Max("dvd_tds"))
                        )
                        temp_dict["tds"].append(
                            {True: "0", False: max_values["dvd_tds__max"]}[
                                max_values["dvd_tds__max"] == None
                            ]
                        )
                        temp_dict["time"].append(x["month_year"])
                        if idx == len(months) - 1:
                            temp_dict["date_time"] = x["month_year"]
                    tds_result.append(temp_dict)

            sensor_data = {"PH": ph_result, "TEMP": temp_result, "TDS": tds_result}

        return sensor_data
    except Exception as e:
        response = "on line {}".format(sys.exc_info()[-1].tb_lineno), str(e)
        return response
