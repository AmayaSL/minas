#Importacion de las librerias
from django.shortcuts import render
from django.contrib.gis.geos import GEOSGeometry
from shapefile.models import MinasPoint
from django.http import JsonResponse
from django.core.serializers import serialize
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
import os
import geopandas as gpd
import pandas as pd
import tempfile


# Create your views here.



def verMapa(request): #Creacion de la funcion para mostrar el mapa con los puntos
    #Obtener los puntos y serializarlos a GeoJSON
    puntos = MinasPoint.objects.all() #En la variable puntos se obtiene todo con la ayuda del metodo "all()" del modelo MinasPoint
    geojson_data = serialize('geojson', puntos, geometry_field='geom', fields=('ocupacion', 'genero', 'lugar_deto')) #Se convierte el punto en formato geojson para mostrarlo en el mapa y se epecifica que campos quiere que se muestre en cada punto del mapa

    # Verifica si la solicitud es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(geojson_data, safe=False)

    # Si no es AJAX, renderiza la plantilla HTML
    return render(request, 'mapa/mapa.html', {'geojson_data': geojson_data})

def cargarArchivoVista(request): #Creacion de la funcion para cargar la vista donde se va a cargar el archivo
    return render(request, 'archivo/cargar_archivo.html')  # Invoca la plantilla con el formulario


@api_view(['POST']) #Especifica que solo se aceptan solicitudes HTTP de tipo post
def cargarArchivo(request): #Creacion de la funcion para cargar los archivos a la base de datos

    shapefiles = request.FILES.getlist('shapefiles')  # Obtiene todos los archivos cargados

    required_files = ['.shp', '.shx', '.dbf', '.cpg', '.prj', '.qmd'] #Se crea una lista con las extensiones necesarias para la carga del shapefile
    uploaded_files = {ext: 0 for ext in required_files} #Inicializa todos los valores de la lista en 0

    # Verifica las extensiones
    for shapefile in shapefiles: #Recorre todo lo que se encuentra en shapefiles
        extension = os.path.splitext(shapefile.name)[1] #En la variable extension con divide el nombre del archivo en dos, el nombre y la extension, luego obtiene la posicion uno, ya que este corresponde a la extension, teniendo en cuenta que 0 seria el nombre
        if extension in uploaded_files: #La extension capturada en dicha variable se compara con el diccionario, si lo encuentra se incrementa en 1, para comprobar que el archivo esta
            uploaded_files[extension] += 1

    # Verifica que cada tipo de archivo se haya subido una sola vez
    for ext, count in uploaded_files.items(): 
        if count != 1:
            return Response({'error': f'Falta o hay múltiples archivos para: {ext}'}, status=status.HTTP_400_BAD_REQUEST)

    # Guarda los archivos en un directorio temporal
    try:
        with tempfile.TemporaryDirectory() as temp_dir: #Crea una variable temporal para leer los archivos
            file_paths = {} #Crea e inicializa un diccionario vacio
            for shapefile in shapefiles: #Recorre la lista shapefiles, donde se obtuviero los archivos cargados
                extension = os.path.splitext(shapefile.name)[1] #Extae la extension
                file_path = os.path.join(temp_dir, f'temp_shapefile{extension}') #La extension extraida se le añade a "temp_shapefile"
                with open(file_path, 'wb') as f: #Abre el archivo en modo binario, esto para guardar el archivo en el disco y mejorar el rendimiento
                    for chunk in shapefile.chunks(): #Lee cada archivo subido y lo escribe en el temporal
                        f.write(chunk)
                file_paths[extension] = file_path #añade al diccionario cada extension del archivo y la ruta en el temporal

            shp_path = file_paths.get('.shp') #Obtiene el ".shp" en la variable "shp_path"

            if not shp_path: #Se comprueba que se haya extraido correctamente y que "shp_path" no este vacia
                return Response({'error': 'El archivo .shp no se guardó correctamente'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            def con(arc):  #Se crea una función para convertir los archivos que no estan el formato EPSG:4326
                if(gdf.crs != "EPSG:4326"): #Si el archivo se encuentra en un formato diferente al 4326 entra al if para la posterior transformación
                    return gdf.to_crs(epsg=4326) #Se transforma el formato y se retorna 
                else: #Si el formato es el correcto se retorna lo mismo que ingreso al metodo
                    return arc
                
            gdf = gpd.read_file(shp_path) #Se lee el shapefile almacenado en "shp_path"
            archvico_convertido = con(gdf) #Se invoca a la funcion para la conversion al formato 4326 y se envia como parametro el shapefile leido. Luego, se almacena en la variable en el formato correcto
                      
            for _, row in archvico_convertido.iterrows(): #Se itera sobre cada fila del shapefile
                def limpiar_coordenada(coordenada_str): #Se crea una funcion para que los valores de Y y X lleguen a la base de datos de manera adecuada
                    partes = coordenada_str.split('.') # Reemplazar puntos, manteniendo el primer punto decimal
    
                    # Unir partes, eliminando todos los puntos excepto el primero que aparece
                    if len(partes) > 1:
                        entero = partes[0].replace('.', '')  # Eliminar puntos del entero
                        decimal = ''.join(partes[1:])  # Unir la parte decimal, si hay más de un punto
                        return f"{entero}.{decimal}"  # Retornar el número final
                    else:
                        return coordenada_str.replace('.', '')  # Si no hay punto, eliminar todos

                y_str = row['Y']  # Se etrae en una variable el valor de Y original
                x_str = row['X']  # Se etrae en una variable el valor de X original

                # Limpiar Y
                y_limpio = limpiar_coordenada(y_str) #Se invoca el metodo para limpiar la coordenada y se pasa esta por parametro la coordenada a limpiar, luego, se almacena en una variable
                y = float(y_limpio)  # Convierte a float

                # Limpiar X
                x_limpio = limpiar_coordenada(x_str) #Se invoca el metodo para limpiar la coordenada y se pasa esta por parametro la coordenada a limpiar, luego, se almacena en una variable
                x = float(x_limpio)  # Convierte a float


                # Verificar que X e Y no sean nulos
                if pd.isnull(y) or pd.isnull(x):
                    return Response({'error': 'El shapefile contiene puntos sin coordenadas válidas'}, status=status.HTTP_400_BAD_REQUEST)

                geometry=GEOSGeometry(row['geometry'].wkt) #Se extrae el valor del punto y se guarda en la variable 

                # Si X e Y son válidos, procedemos a crear el objeto
                MinasPoint.objects.create(
                    departamen = row['Departamen'], #Se extrae el valor directamente desde el shapefile
                    cod_dep=row['Cod_dep'], #Se extrae el valor directamente desde el shapefile
                    municipio = row['Municipio'], #Se extrae el valor directamente desde el shapefile
                    cod_mun=row['Cod_mun'], #Se extrae el valor directamente desde el shapefile
                    zona = row['Zona'], #Se extrae el valor directamente desde el shapefile
                    vereda = row['Vereda'], #Se extrae el valor directamente desde el shapefile
                    ano=row['Ano'], #Se extrae el valor directamente desde el shapefile
                    mes=row['Mes'], #Se extrae el valor directamente desde el shapefile
                    edad=row['Edad'], #Se extrae el valor directamente desde el shapefile
                    ocupacion=row['Ocupacion'], #Se extrae el valor directamente desde el shapefile
                    genero=row['Genero'], #Se extrae el valor directamente desde el shapefile
                    condicion=row['Condicion'], #Se extrae el valor directamente desde el shapefile
                    y=y, #Se pasa la variable procesada, luego de darle el formato correcto
                    x=x, #Se pasa la variable procesada, luego de darle el formato correcto
                    lugar_deto=row['Lugar_deto'], #Se extrae el valor directamente desde el shapefile
                    actividad=row['Actividad'], #Se extrae el valor directamente desde el shapefile
                    y_cmt12=row['Y_CMT12'], #Se extrae el valor directamente desde el shapefile
                    x_cmt12=row['X_CMT12'], #Se extrae el valor directamente desde el shapefile
                    geom=geometry #Se pasa la variable que contiene el valor del punto
                )

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) #Si hubo algun error durante la carga devuelve un error interno del servidor

    return Response({'status': 'Archivos cargados correctamente'}, status=status.HTTP_201_CREATED) #Devuelve un mensaje para verificar que el archivo se cargo correctamente
