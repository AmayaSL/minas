from django.forms import ModelForm, EmailInput, TextInput, NumberInput
from shapefile.models import MinasPoint
from django import forms
from django.contrib.gis.geos import Point




class MinasPointForm(forms.ModelForm):
    class Meta:
        model = MinasPoint
        fields = ['departamen', 'cod_dep', 'municipio', 'cod_mun', 'zona', 
                  'vereda', 'ano', 'mes', 'edad', 'ocupacion', 'genero', 
                  'condicion', 'y', 'x', 'lugar_deto', 'actividad', 
                  'y_cmt12', 'x_cmt12']  # Sin geom
        widgets = {
            'ano': forms.TextInput(attrs={'type': 'text'}),
            'mes': forms.TextInput(attrs={'type': 'text'}),
            'edad': forms.TextInput(attrs={'type': 'text'}),
            'ocupacion': forms.TextInput(attrs={'type': 'text'}),
            'genero': forms.TextInput(attrs={'type': 'text'}),
            'condicion': forms.TextInput(attrs={'type': 'text'}),
            'y': forms.NumberInput(attrs={'type': 'number'}),
            'x': forms.NumberInput(attrs={'type': 'number'}),
            'actividad': forms.TextInput(attrs={'type': 'text'}),
            'y_cmt12': forms.TextInput(attrs={'type': 'text'}),
            'x_cmt12': forms.TextInput(attrs={'type': 'text'}),
            
            
        }
