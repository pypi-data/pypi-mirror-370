from django.db import models

class Wilaya(models.Model):
    name_ar = models.CharField(max_length=100, unique=True)
    name_fr = models.CharField(max_length=100)

    def __str__(self):
        return self.name_ar

class Commune(models.Model):
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, related_name="communes")
    name_ar = models.CharField(max_length=100)
    name_fr = models.CharField(max_length=100)

    class Meta:
        unique_together = ('wilaya', 'name_ar')

    def __str__(self):
        return f"{self.name_ar}, {self.wilaya.name_ar}"
