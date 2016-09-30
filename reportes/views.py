from django.shortcuts import render
from .forms import RegistroReporteForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from .models import Reporte
from django.contrib import messages
from django.db import connection
from itertools import islice
from django.http import JsonResponse

import MySQLdb
import csv
import ast
import os
import logging

#Obtenemos una instancia de logger para poder loguear en la consola
logger = logging.getLogger(__name__)


separadores = [",","\\t"]
findelineas = ["\\n","\\r", "\\r\\n"]

# Almacemanos el archivo en lugar de tratarlo desde la memoria para evitar
# problemas con archivos muy grandes
def almacena_archivo_desde_formulario(archivo, nombre):
    with open('media/temp/'+nombre, 'wb+') as destino:
        # Usamos chunks o trozos en lugar de hacer un read
        # para evitar sobrecargar la memoria en caso de archivos grandes
        for chunk in archivo.chunks():
            destino.write(chunk)

def crear_schema_tabla(nombre, separador, findelinea):
    # abrimos el archivo con codificacion ISO
    with open('media/temp/'+nombre, encoding="ISO-8859-1") as csvfile:
        #Obtenemos liena 1 para tomar las cabeceras
        linea = csvfile.readlines(1)
        #Extraemos los campos quitando el salto de liena y el retorno de carro
        # Las lineas seran divididas por comas
        campos = tuple(linea[0].strip('\n').strip('\r').split(separadores[separador]))



    # Preparamos la consulta quitandole al nombre del archivo la extension
    sql = "DROP TABLE IF EXISTS "+nombre[:-4]+"; "
    sql = "CREATE TABLE IF NOT EXISTS "+nombre[:-4]+"("

    # Recorremos los campos para crear la tabla
    for indice, campo in enumerate(campos):
        sql += "`"+campo+"` TEXT, "

    sql = sql[:-2]+")"

    return sql

# Create your views here.
def nuevo_reporte_view(request):
    if request.method == 'POST':
        form = RegistroReporteForm(request.POST, request.FILES)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            nombre = cleaned_data.get('nombre')
            separador = int(cleaned_data.get('separador'))
            findelinea = int(cleaned_data.get('findelinea'))
            campos_entre_comillas = cleaned_data.get('campos_entre_comillas')

            # Creamos la instancia del Formulario de Modelo pero siin guardar
            reporte_model = form.save(commit=False)

            # Llenamos los campos del modelo y guradamos para obtener el id del reporte
            reporte_model.nombre = nombre
            reporte_model.nombre_tabla = str(nombre).replace(' ','_').strip().lower()

            #alamacenamos el archivo para luego procesarlo
            nombre_archivo = reporte_model.nombre_tabla+'.'+request.FILES['archivo'].name[-3:]
            almacena_archivo_desde_formulario(request.FILES['archivo'], nombre_archivo)

            # generamos el script para crear la tabla
            sql = crear_schema_tabla(nombre_archivo, separador, findelinea)

            # conectamos con la base de datos con permisos de cargar archivos
            db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh', local_infile=1)

            #obtenemos el cursor
            cursor = db.cursor()

            # creamos la tabla
            cursor.execute(sql)
            db.commit()

            # Cargamos el archivo
            sql =  "LOAD DATA LOCAL INFILE '"+os.path.abspath("media/temp/"+nombre_archivo)+"' "
            sql += "INTO TABLE `"+reporte_model.nombre_tabla+"` "
            sql += "CHARACTER SET latin1 "
            sql += "FIELDS TERMINATED BY '"+separadores[separador]+"' "

            if campos_entre_comillas:
                sql += "ENCLOSED BY '\"' "

            sql += "ESCAPED BY '\\\\' "
            sql += "LINES TERMINATED BY '"+findelineas[findelinea]+"' "
            sql += "IGNORE 1 LINES "

            # ejecutamos la carga del archivo
            cursor.execute(sql)
            db.commit()

            #cerramos la conexion con el servidor
            db.close()

            #eliminamos el archivo temporal
            os.remove(os.path.abspath("media/temp/"+nombre_archivo))

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

def reporte_view(request, reporte_id, limit, offset):
    # conectamos con la base de datos con permisos de cargar archivos
    db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh')
    sql = "SELECT nombre_tabla  FROM reportes_reporte WHERE id = "+reporte_id

    #obtenemos el cursor
    cursor = db.cursor()

    cursor.execute(sql)
    data=cursor.fetchone()

    sql = "SELECT * FROM "+data[0]+" LIMIT "+limit+" OFFSET "+offset
    cursor.execute(sql)
    data=cursor.fetchall()
    headers = [i[0] for i in cursor.description]

    cursor.close()

    context = {
        'data': data,
        'headers': headers
    }
    return JsonResponse(context)
    #return render(request, 'reporte.html', context)
