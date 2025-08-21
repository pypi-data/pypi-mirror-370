from django.db import models

class Wilaya(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100, unique=True)
    ar_name = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.code})"
    class Meta:
        verbose_name_plural = "Wilayas"
        verbose_name = "Wilaya"


class Commune(models.Model):
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, related_name="communes")
    post_code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)
    ar_name = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.post_code}) in {self.wilaya.name}"
    
    class Meta:
        verbose_name_plural = "Communes"
        verbose_name = "Commune"
