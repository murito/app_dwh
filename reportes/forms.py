from django import forms
from django.forms import ModelForm
from .models import Reporte

OPCIONES_SEPARADOR = (
    (0, ("Comma")),
    (1, ("Tab")),
)

OPCIONES_FINLINEA = (
    (0, ("Salto de linea")),
    (1, ("Retorno de carro")),
    (1, ("Retorno de carro y salto de liena")),
)

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
    separador = forms.ChoiceField(choices=OPCIONES_SEPARADOR, widget=forms.Select(attrs={'class':'form-control'}))
    findelinea = forms.ChoiceField(choices=OPCIONES_FINLINEA, widget=forms.Select(attrs={'class':'form-control'}))
    campos_entre_comillas = forms.BooleanField(initial=True, required=False)
