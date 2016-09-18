from django.shortcuts import render
from .forms import RegistroReporteForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from .models import Reporte
from django.contrib import messages

import logging
logger = logging.getLogger(__name__)


# Create your views here.
def nuevo_reporte_view(request):
    if request.method == 'POST':
        form = RegistroReporteForm(request.POST, request.FILES)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            nombre = cleaned_data.get('nombre')
            archivo = cleaned_data.get('archivo')

            # Creamos la instancia del Formulario de Modelo pero siin guardar
            reporte_model = form.save(commit=False)

            # Llenamos los campos del modelo y guradamos para obtener el id del reporte
            reporte_model.nombre = nombre
            reporte_model.nombre_tabla = str(nombre).replace(' ','_').strip().lower()
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
