from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Reporte(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    nombre_tabla = models.CharField(max_length=100, default="")
    user_id = models.ManyToManyField(User, related_name= 'user_id')

    def __str__(self):
        return self.nombre
