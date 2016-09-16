from django.conf.urls import url

from . import views

urlpatterns = [
    # /home/
    url(regex=r'^$', view=views.index_view, name='home'),
]
