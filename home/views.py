from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from reportes.models import Reporte

@login_required
def index_view(request):
    reportes = Reporte.objects.filter(user_id=request.user.id).select_related()

    return render(request, 'index.html', {'reportes': reportes})
