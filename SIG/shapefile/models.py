from django.contrib.gis.db import models


# Create your models here.

class MinasPoint(models.Model):
        gid = models.AutoField(primary_key=True)
        departamen = models.CharField(80)
        cod_dep = models.CharField(80)
        municipio = models.CharField(80)
        cod_mun = models.CharField(80)
        zona = models.CharField(80)
        vereda = models.CharField(80)
        ano = models.CharField(80)
        mes = models.CharField(80)
        edad = models.CharField(80)
        ocupacion = models.CharField(80)
        genero = models.CharField(80)
        condicion = models.CharField(80)
        y = models.FloatField()
        x = models.FloatField()
        lugar_deto = models.CharField(80)
        actividad = models.CharField(80)
        y_cmt12 = models.CharField(80)
        x_cmt12 = models.CharField(80)
        geom = models.GeometryField(srid=4326)
        

        def __str__(self):
            return str(self.gid)

