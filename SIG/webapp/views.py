from django.shortcuts import render

# Create your views here.

def bienvenido(request): #Metodo para volver a la pagina de inicio
    return render(request, 'bienvenido.html')
