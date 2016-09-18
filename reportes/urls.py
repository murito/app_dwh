from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^nuevo/$', views.nuevo_reporte_view, name='reportes.nuevo'),
]
