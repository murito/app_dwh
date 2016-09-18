from django import forms
from django.forms import ModelForm
from .models import Reporte

class RegistroReporteForm(ModelForm):
    archivo = forms.FileField()

    class Meta:
        model = Reporte
        fields = ['nombre']
        exclude = ['nombre_tabla', 'user_id']

    #validamos la extension del archivo
    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        if not archivo.name[-3:] in ['xls', 'csv', 'json']:
            raise forms.ValidationError('El formato del archivo no esta permitido.')

    #Agregamos la clase de bootstrap para que se vea bonito
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
