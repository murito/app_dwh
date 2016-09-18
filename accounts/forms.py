from django import forms
from django.contrib.auth.models import User

class RegistroUserForm(forms.Form):
    nombre = forms.CharField()
    apellido = forms.CharField()
    username = forms.CharField(min_length=5)
    email = forms.EmailField()
    password = forms.CharField(min_length=5, widget=forms.PasswordInput())
    confirmar_password = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        """Comprueba que no exista un username igual en la db"""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username):
            raise forms.ValidationError('Nombre de usuario ya registrado.')
        return username

    def clean_email(self):
        """Comprueba que no exista un email igual en la db"""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError('Ya existe un email igual en la db.')
        return email

    def clean_confirmar_password(self):
        """Comprueba que password y password2 sean iguales."""
        password = self.cleaned_data['password']
        confirmar_password = self.cleaned_data['confirmar_password']
        if password != confirmar_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return confirmar_password

    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(min_length=5,widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(min_length=5,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_password = forms.CharField(min_length=5,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
