from django.db import models

class PowerReport(models.Model):
    file_path = models.CharField(max_length=255)
    report_path = models.CharField(max_length=255)
    generated_at = models.DateTimeField(auto_now_add=True)
