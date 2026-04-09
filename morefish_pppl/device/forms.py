# from django import forms
# from device.models import Device, SensorCalibration, RetrievedCalibration
# from rawdata.calculation import analogToPH,analogToTDS,analogToTemperature

# def convert_ph_value(device_id,value):
#     calibration_value = SensorCalibration.objects.get(device_id = device_id)
#     return analogToPH(value,calibration_value.ph_calibration_value)

# def convert_tds_value(device_id,value):
#     calibration_value = SensorCalibration.objects.get(device_id = device_id)
#     return analogToTDS(value,calibration_value.tds_calibration_value)

# def convert_temperature_value(device_id,value):
#     calibration_value = SensorCalibration.objects.get(device_id = device_id)
#     return analogToTemperature(value,calibration_value.temp_calibration_value)

# # class RawDataCalulationAdminForm(forms.Form):
# #     device = forms.ModelChoiceField(queryset=Device.objects.all(), empty_label=None)
# #     pH_raw_value = forms.IntegerField(required=False)
# #     tds_raw_value = forms.IntegerField(required=False)
# #     temperature_raw_value = forms.IntegerField(required=False)
# #     converted_ph_value = forms.CharField(required=False, disabled=True)
# #     converted_tds_value = forms.CharField(required=False, disabled=True)
# #     converted_temperature_value = forms.CharField(required=False, disabled=True)

# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)

# #         if self.is_bound and self.data.get('device'):
# #             device_id = self.data['device']
# #             ph_raw = self.data['pH_raw_value']
# #             tds_raw = self.data['tds_raw_value']
# #             temp_raw = self.data['temperature_raw_value']
# #             converted_values = {}

# #             print("PH_RAW",type(ph_raw))

# #             if self.data.get('pH_raw_value'):
# #                 converted_values['converted_ph_value'] = convert_ph_value(device_id, int(ph_raw))
            
# #             if self.data.get('tds_raw_value'):
# #                 converted_values['converted_tds_value'] = convert_tds_value(device_id, int(tds_raw))
            
# #             if self.data.get('temperature_raw_value'):
# #                 converted_values['converted_temperature_value'] = convert_temperature_value(device_id, int(temp_raw))
            

# #             self.initial.update(converted_values)
# #             self.data = self.data.copy()  # Create a mutable copy of the data
# #             self.data.update(converted_values)
# #             self._changed_data = None
            
            
# # class CalibrationForm(forms.ModelForm):
# #     class Meta:
# #         model = RetrievedCalibration
# #         fields = '__all__'

# #     # Add custom validation for manual input fields
# #     def clean(self):
# #         cleaned_data = super().clean()
# #         ph_value = cleaned_data.get('ph_value')
# #         tds_value = cleaned_data.get('tds_value')
# #         temp_value = cleaned_data.get('temp_value')

# #         if ph_value is None and tds_value is None and temp_value is None:
# #             raise forms.ValidationError("At least one manual input field must be filled.")

# #         return cleaned_data