from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^nuevo/$', views.nuevo_reporte_view, name='reportes.nuevo'),
    url(r'^reporte/(?P<reporte_id>\d+)/(?P<limit>\d+)/(?P<offset>\d+)/', views.reporte_view, name='reportes.obtener_reporte'),
]
