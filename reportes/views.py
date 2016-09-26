from django.shortcuts import render
from .forms import RegistroReporteForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from .models import Reporte
from django.contrib import messages
from django.db import connection

import MySQLdb
import csv
import logging
#Obtenemos una instancia de logger para poder loguear en la consola
logger = logging.getLogger(__name__)

# Almacemanos el archivo en lugar de tratarlo desde la memoria para evitar
# problemas con archivos muy grandes
def almacena_archivo_desde_formulario(archivo, nombre):
    with open('media/temp/'+nombre, 'wb+') as destino:
        # Usamos chunks o trozos en lugar de hacer un read
        # para evitar sobrecargar la memoria en caso de archivos grandes
        for chunk in archivo.chunks():
            destino.write(chunk)

# Create your views here.
def nuevo_reporte_view(request):
    if request.method == 'POST':
        form = RegistroReporteForm(request.POST, request.FILES)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            nombre = cleaned_data.get('nombre')

            # Creamos la instancia del Formulario de Modelo pero siin guardar
            reporte_model = form.save(commit=False)

            # Llenamos los campos del modelo y guradamos para obtener el id del reporte
            reporte_model.nombre = nombre
            reporte_model.nombre_tabla = str(nombre).replace(' ','_').strip().lower()

            #alamacenamos el archivo para luego procesarlo
            nombre_archivo = reporte_model.nombre_tabla+'.'+request.FILES['archivo'].name[-3:]
            almacena_archivo_desde_formulario(request.FILES['archivo'], nombre_archivo)

            # conectamos con la base de datos con permisos de cargar archivos
            #db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh', local_infile=1)
            #obtenemos el cursor
            #cursor = db.cursor()

            # Cargamos el archivo
            #sql =  "LOAD DATA LOCAL INFILE 'media/temp/"+nombre_archivo+"'"
            #sql += "INTO TABLE "+reporte_model.nombre_tabla+" "
            #sql += "FIELDS TERMINATED BY ',' "
            #sql += "ENCLOSED BY '\"' "
            #sql += "ESCAPED BY '\\\\' "
            #sql += "LINES TERMINATED BY '\\r\\n' "
            #cursor.execute(sql);


            # Si vamos bien con la importacion gurdamos el registro del reportte
            reporte_model.save()

            # Agregamos la relacion del reporte con el usuario  y guradamos
            reporte_model.user_id.add(request.user)
            reporte_model.save()

            # redirigimos a home
            messages.success(request, 'El reporte se almaceno con exito.')
            return redirect(reverse('home'))
    else:
        form = RegistroReporteForm()

    context = { 'form': form }

    return render(request, 'nuevo_reporte.html', context)
