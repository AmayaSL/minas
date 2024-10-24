"""
URL configuration for SIG project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webapp.views import bienvenido
from shapefile.views import verMapa, cargarArchivoVista, cargarArchivo #importación de los metodos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bienvenido, name='inicio'),
    
    path('ver_mapa/', verMapa, name='mapa'),
    #path('ver_shapefile/', verShapefile), #Creación del path para ver un registro
    #path('agregar_departamento/',nuevoDepartamento, name='departamento'), #Creacion del path para agregar un registro de departamento
    #path('agregar_municipio/',nuevoMunicipio), #Creacion del path para agregar un registro de municipio
    #path('agregar_puntoMina/',nuevoMinasPoint), #Creacion del path para agregar un registro de punto de mina
    path('cargar_archivo/', cargarArchivoVista),
    path('cargar_archivo/post/', cargarArchivo, name='cargar_archivo'),
]
