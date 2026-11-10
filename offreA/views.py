from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_safe

from config.suppression import traiter_suppression
from .models import Offre


@require_safe
def liste_offres(request):
    offres = Offre.objects.select_related('expedition', 'transporteur', 'vehicule').order_by('-date_proposition', '-pk')
    return render(request, 'offres/liste.html', {'offres': offres})


@require_safe
def detail_offre(request, pk):
    offre = get_object_or_404(Offre.objects.select_related('expedition', 'transporteur', 'vehicule'), pk=pk)
    return render(request, 'offres/detail.html', {'offre': offre, 'suppressions_demo': settings.DEBUG})


@require_http_methods(['GET', 'POST'])
@csrf_protect
def supprimer_offre(request, pk):
    return traiter_suppression(
        request, Offre, {'pk': pk}, 'offres', 'l’offre', verifier_suppression,
    )


def verifier_suppression(offre):
    if offre.statut == 'acceptee':
        return 'Une offre acceptée doit rester dans l’historique de l’expédition.'
