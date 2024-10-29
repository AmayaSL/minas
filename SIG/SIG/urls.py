from django.contrib import admin
from django.urls import path
from webapp.views import bienvenido
from shapefile.views import verMapa, cargarArchivoVista, cargarArchivo #importación de los metodos

#Creacion de las rutas para acceder a los metodos
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bienvenido, name='inicio'),
    path('ver_mapa/', verMapa, name='mapa'),
    path('cargar_archivo/', cargarArchivoVista),
    path('cargar_archivo/post/', cargarArchivo, name='cargar_archivo'),
]
