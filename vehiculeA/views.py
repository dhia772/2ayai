from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_safe

from config.suppression import traiter_suppression
from .models import Vehicule


@require_safe
def liste_vehicules(request):
    vehicules = Vehicule.objects.select_related('entreprise').order_by('immatriculation')
    return render(request, 'vehicules/liste.html', {'vehicules': vehicules})


@require_safe
def detail_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule.objects.select_related('entreprise'), pk=pk)
    return render(request, 'vehicules/detail.html', {'vehicule': vehicule, 'suppressions_demo': settings.DEBUG})


@require_http_methods(['GET', 'POST'])
@csrf_protect
def supprimer_vehicule(request, pk):
    return traiter_suppression(
        request, Vehicule, {'pk': pk}, 'vehicules', 'le véhicule', verifier_suppression,
    )


def verifier_suppression(vehicule):
    if not vehicule.disponible:
        return 'Ce véhicule est indisponible.'
