from django.shortcuts import render, get_object_or_404, redirect
from shapefile.forms import MinasPointForm
from django.contrib.gis.geos import Point, GEOSGeometry
from shapefile.models import MinasPoint
from django.http import JsonResponse
from django.core.serializers import serialize
from rest_framework.response import Response
from rest_framework import status
import shapefile
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
import os
import geopandas as gpd
import pandas as pd
import tempfile
from decimal import Decimal


# Create your views here.



def verMapa(request):
    # Obtener los puntos y serializarlos a GeoJSON
    puntos = MinasPoint.objects.all()
    geojson_data = serialize('geojson', puntos, geometry_field='geom', fields=('ocupacion', 'genero', 'lugar_deto'))

    # Verifica si la solicitud es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(geojson_data, safe=False)

    # Si no es AJAX, renderiza la plantilla HTML
    return render(request, 'gis/mapa.html', {'geojson_data': geojson_data})

#def nuevoDepartamento(request):
#    if request.method == 'POST':
 #       formaDepartamento = DepartamentoForm(request.POST)
  #      if formaDepartamento.is_valid():
   #         formaDepartamento.save()
 #           return redirect('inicio')
  #  else:
   #     formaDepartamento = DepartamentoForm()

    #return render(request, 'departamentos/agregar_departamento.html' , {'formaDepartamento': formaDepartamento})

#def nuevoMunicipio(request):
 #   if request.method == 'POST':
  #      formaMunicipio = MunicipioForm(request.POST)
   #     if formaMunicipio.is_valid():
    #        formaMunicipio.save()
     #       return redirect('inicio')
  #  else:
   #     formaMunicipio = MunicipioForm()
#
 #   return render(request, 'municipios/agregar_municipio.html' , {'formaMunicipio': formaMunicipio})



#def nuevoMinasPoint(request):
 #   if request.method == 'POST':
  #      formaMinasPoint = MinasPointForm(request.POST)
   #     if formaMinasPoint.is_valid():
    #        # Obtener las coordenadas de X y Y
     #       x = formaMinasPoint.cleaned_data['x']
      #      y = formaMinasPoint.cleaned_data['y']
       #     point = Point(x, y, srid=4326)  # Crea un objeto Point con las coordenadas
#
 #           # Guardar la instancia de MinasPoint
  #          mina = formaMinasPoint.save(commit=False)
   #         mina.geom = point  # Asigna el objeto Point al campo geom
    #        mina.save()
#
 #           return redirect('inicio')  # Redirige a la vista de inicio
  #  else:
   #     formaMinasPoint = MinasPointForm()
#
 #   return render(request, 'minas/agregar_puntoMina.html', {'formaMinasPoint': formaMinasPoint})



def cargarArchivoVista(request):
    return render(request, 'archivo/cargar_archivo.html')  # Invoca la plantilla con el formulario


@api_view(['POST'])
def cargarArchivo(request):

    shapefiles = request.FILES.getlist('shapefiles')  # Obtiene todos los archivos cargados

    required_files = ['.shp', '.shx', '.dbf', '.cpg', '.prj', '.qmd']
    uploaded_files = {ext: 0 for ext in required_files}

    # Verifica las extensiones
    for shapefile in shapefiles:
        extension = os.path.splitext(shapefile.name)[1]
        if extension in uploaded_files:
            uploaded_files[extension] += 1

    # Verifica que cada tipo de archivo se haya subido una sola vez
    for ext, count in uploaded_files.items():
        if count != 1:
            return Response({'error': f'Falta o hay múltiples archivos para: {ext}'}, status=status.HTTP_400_BAD_REQUEST)

    # Guarda los archivos en un directorio temporal
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = {}
            for shapefile in shapefiles:
                extension = os.path.splitext(shapefile.name)[1]
                file_path = os.path.join(temp_dir, f'temp_shapefile{extension}')
                with open(file_path, 'wb') as f:
                    for chunk in shapefile.chunks():
                        f.write(chunk)
                file_paths[extension] = file_path

            shp_path = file_paths.get('.shp')

            if not shp_path:
                return Response({'error': 'El archivo .shp no se guardó correctamente'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            def con(arc): 
                print(f"ANTES DEL IF")
                if(gdf.crs != "EPSG:4326"):
                    print(f"ENTROOOOO")
                    #transformacion
                    return gdf.to_crs(epsg=4326)
                    # geometry=GEOSGeometry(conversion.geometry.wkt, srid=4326)
                    # print(f"Punto geom dentro del if: {geometry}")
                else:
                    # geometry=GEOSGeometry(row['geometry'].wkt)
                    # print(f"Punto geom : {geometry}")
                    return arc
                
            # Después de leer el shapefile
            gdf = gpd.read_file(shp_path)
            archvico_convertido = con(gdf)
            

            # Imprimir las coordenadas para verificar
            print(f"Impresion: {archvico_convertido.geometry}")
            print("-----------------------------------------")
            print(archvico_convertido.head())  # Imprime las primeras filas del DataFrame
            print(archvico_convertido.columns)  # Imprime los nombres de las columnas

            print(f"Formato: {archvico_convertido.crs}")
            print(f"Tipo de datos: {archvico_convertido.geom_type.value_counts()}")
            
            print(f"Y antes del for: {archvico_convertido.head().Y[0]}")
          
            # Procesar cada fila en el DataFrame
            for _, row in archvico_convertido.iterrows():
                 
                def limpiar_coordenada(coordenada_str):
                    # Reemplazar puntos, manteniendo el primer punto decimal
                    partes = coordenada_str.split('.')
    
                    # Unir partes, eliminando todos los puntos excepto el primero que aparece
                    if len(partes) > 1:
                        entero = partes[0].replace('.', '')  # Eliminar puntos del entero
                        decimal = ''.join(partes[1:])  # Unir la parte decimal, si hay más de un punto
                        return f"{entero}.{decimal}"  # Retornar el número final
                    else:
                        return coordenada_str.replace('.', '')  # Si no hay punto, eliminar todos

                # Ejemplo de uso
                y_str = row['Y']  # Ejemplo de Y original
                x_str = row['X']             # Ejemplo de X original

                # Limpiar Y
                y_cleaned = limpiar_coordenada(y_str)
                y = float(y_cleaned)  # Convertir a float si es necesario

                # Limpiar X
                x_cleaned = limpiar_coordenada(x_str)
                x = float(x_cleaned)  # Convertir a float si es necesario

                print(f"Y corregido: {y_cleaned}, X corregido: {x_cleaned}")


                # Verificar que X e Y no sean nulos
                if pd.isnull(y) or pd.isnull(x):
                    return Response({'error': 'El shapefile contiene puntos sin coordenadas válidas'}, status=status.HTTP_400_BAD_REQUEST)

                

                print("Los datos como vienen: ")
                print(f"Tipo de dato: {archvico_convertido.crs}")
                # print(f"Y original {row['Y']}")
                # print(f"X original: {row['X']}")
                # print("Los archivos que esta cargando a la BD son: ")
                # print(f"Y: {y}")
                # print(f"X: {x}")
                print("------------------------------")
                
                # if(gdf.crs != "EPSG:4326"):
                #     #transformacion
                #     conversion=gdf.to_crs(epsg=4326)
                #     geometry=GEOSGeometry(conversion.geometry)
                #     print(f"Punto geom dentro del if: {geometry}")
                # else:
                #     geometry=GEOSGeometry(row['geometry'].wkt)
                #     print(f"Punto geom : {geometry}")
                geometry=GEOSGeometry(row['geometry'].wkt)

                # Si X e Y son válidos, procedemos a crear el objeto
                MinasPoint.objects.create(
                    departamen = row['Departamen'],
                    cod_dep=row['Cod_dep'],
                    municipio = row['Municipio'],
                    cod_mun=row['Cod_mun'],
                    zona = row['Zona'],
                    vereda = row['Vereda'],
                    ano=row['Ano'],
                    mes=row['Mes'],
                    edad=row['Edad'],
                    ocupacion=row['Ocupacion'],
                    genero=row['Genero'],
                    condicion=row['Condicion'],
                    y=y,  # Usar el valor directamente de la fila
                    x=x,  # Usar el valor directamente de la fila
                    lugar_deto=row['Lugar_deto'],
                    actividad=row['Actividad'],
                    y_cmt12=row['Y_CMT12'],
                    x_cmt12=row['X_CMT12'],
                    #geom= Point(x, y, srid=4326)
                    geom=geometry
                )

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'Archivos cargados correctamente'}, status=status.HTTP_201_CREATED)
