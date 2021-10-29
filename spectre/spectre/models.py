from django.db import models

class WeatherPoint(models.Model):
    def __str__(self):
        return f'{self.time} {self.temp}'
    time = models.IntegerField(primary_key=True)
    temp = models.FloatField()
