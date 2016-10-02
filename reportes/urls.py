from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^nuevo/$', views.nuevo_reporte_view, name='reportes.nuevo'),
    url(r'^reporte/(?P<reporte_id>\d+)/(?P<nombre_tabla>\w+)/', views.reporte_view, name='reportes.obtener_reporte'),
    url(r'^cabeceras_reporte/(?P<reporte_id>\d+)/(?P<nombre_tabla>\w+)/', views.obtener_cabeceras_reporte, name='reportes.obtener_cabeceras_reporte'),
]
