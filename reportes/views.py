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
import re
import numbers

from messytables import CSVTableSet, type_guess, \
types_processor, headers_guess, headers_processor, \
offset_processor, any_tableset

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


def crear_schema_tabla_v2(nombre):
    # conectamos con la base de datos con permisos de cargar archivos
    db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh')

    fh = open('media/temp/'+nombre, 'rb')

    # Cargamos el archivo y creamos el objeto
    table_set = CSVTableSet(fh)

    # Obtenemos la tabla cero
    row_set = table_set.tables[0]

    # Obtenemos los nombres de las columnas
    offset, headers = headers_guess(row_set.sample)
    row_set.register_processor(headers_processor(headers))

    # Recorremos una fila abajo parra saltar la cabecera
    row_set.register_processor(offset_processor(offset + 1))

    # Obtenemos los tipos de datos de cada columna
    types = type_guess(row_set.sample, strict=True)

    # Aplicamos los tipos encontrados en cada fila del conjunto
    row_set.register_processor(types_processor(types))

    # Preparamos la consulta quitandole al nombre del archivo la extension
    sql = "DROP TABLE IF EXISTS "+nombre[:-4]+"; "
    cursor = db.cursor()
    cursor.execute(sql)
    cursor.close()
    db.commit()


    db.close()

    sql = "CREATE TABLE IF NOT EXISTS "+nombre[:-4]+"("

    # solo recorremos el row 1
    for row in row_set:
        for field in row:
            if str(field.type) == "Integer":
                sql += "`"+field.column.replace(" ","_")+"` INT(11), "
            elif str(field.type) == "Decimal":
                sql += "`"+field.column.replace(" ","_")+"` DECIMAL(64,10), "
            elif str(field.type) == "Bool":
                sql += "`"+field.column.replace(" ","_")+"` INT(1), "
            else:
                sql += "`"+field.column.replace(" ","_")+"` VARCHAR("+str(len(field.value))+"), "
        break

    sql = sql[:-2]+")"

    return sql

# Create your views here.
def nuevo_reporte_view(request):
    if request.method == 'POST':
        form = RegistroReporteForm(request.POST, request.FILES)

        if form.is_valid():
            # conectamos con la base de datos con permisos de cargar archivos
            db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh', local_infile=1)

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

            #creamos el schema de una nuvea forma
            sql = crear_schema_tabla_v2(nombre_archivo)

            #obtenemos el cursor
            cursor = db.cursor()

            # creamos la tabla
            cursor.execute(sql)
            db.commit()
            cursor.close()


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
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            cursor.close()


            db.close()

            # Si vamos bien con la importacion gurdamos el registro del reportte
            reporte_model.save()

            # Agregamos la relacion del reporte con el usuario  y guradamos
            reporte_model.user_id.add(request.user)
            reporte_model.save()


            #eliminamos el archivo temporal
            os.remove(os.path.abspath("media/temp/"+nombre_archivo))

            # redirigimos a home
            messages.success(request, 'El reporte se almaceno con exito.')
            return redirect(reverse('home'))
    else:
        form = RegistroReporteForm()

    context = { 'form': form }

    return render(request, 'nuevo_reporte.html', context)


def obtener_cabeceras_reporte(request, reporte_id, nombre_tabla):
    # conectamos con la base de datos con permisos de cargar archivos
    db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh')

    sql = "SELECT * FROM "+nombre_tabla+" LIMIT 1;"

    cursor = db.cursor()
    cursor.execute(sql)
    data=cursor.fetchone()

    headers = [i[0] for i in cursor.description]
    cursor.close()

    db.close()

    context = {
        'headers': headers
    }

    return JsonResponse(context)


def reporte_view(request, reporte_id, nombre_tabla):
    db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh', cursorclass = MySQLdb.cursors.SSCursor)

    offset = request.GET['start']
    limit = request.GET['length']
    draw = request.GET['draw']
    orderby = request.GET.get('order[0][column]', '')
    order = request.GET.get('order[0][dir]', '')


    #obtenemos el total de registros
    #sql = "SELECT COUNT(*) AS total FROM "+nombre_tabla <= esto tarda mucho con tablas grandes
    sql = "SELECT table_rows AS total "
    sql += "FROM information_schema.tables "
    sql += "WHERE table_name = '"+nombre_tabla+"'"

    cursor = db.cursor()
    cursor.execute(sql)
    total=cursor.fetchone()
    try:
        cursor.close()
    except Err:
        pass

    # obetenemos los registros paginados
    sql = "SELECT * FROM "+nombre_tabla

    if orderby != "" and order != "":
        sql_ = "SELECT  nombre_campo('"+nombre_tabla+"',"+str(orderby)+") "
        cursor = db.cursor()
        cursor.execute(sql_)
        orderby_=cursor.fetchone()
        cursor.close()

        sql += " ORDER BY `"+orderby_[0]+"` "+order

    sql += " LIMIT "+offset+", "+limit

    cursor = db.cursor()
    cursor.execute(sql)
    data=cursor.fetchall()
    try:
        cursor.close()
    except Err:
        pass

    db.close()

    context = {
        'draw': draw,
        'data': data,
        'recordsTotal': total[0],
        'recordsFiltered': total[0]
    }

    return JsonResponse(context)

def eliminar_columna_reporte(request, columna, reporte):
    # conectamos con la base de datos con permisos de cargar archivos
    db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh')

    sql = "SELECT nombre_campo('"+reporte+"', "+columna+"); "
    cursor = db.cursor();
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()

    sql = "ALTER TABLE `dwh`.`"+reporte+"` DROP `"+data[0]+"` "
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()

    db.close()

    context = {
        'success': "true"
    }

    return JsonResponse(context)

def eliminar_reporte(request, id, nombre_tabla):
    # conectamos con la base de datos con permisos de cargar archivos
    db = MySQLdb.connect(host='localhost', user='root', passwd='', db='dwh')

    sql = "DROP TABLE IF EXISTS "+nombre_tabla
    cursor = db.cursor();
    cursor.execute(sql)
    cursor.close()
    db.commit()

    sql = "DELETE FROM reportes_reporte WHERE id = "+id
    cursor = db.cursor();
    cursor.execute(sql)
    cursor.close()
    db.commit()

    db.close()

    context = {
        'success': "true"
    }

    return JsonResponse(context)
