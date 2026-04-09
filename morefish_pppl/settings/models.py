from django.db import models
from datetime import datetime


class AppVersion(models.Model):
    version_number = models.CharField(max_length=20, unique=True)
    release_date = models.DateField()

    def __str__(self):
        return f"Version {self.version_number} - Released on {self.release_date}"