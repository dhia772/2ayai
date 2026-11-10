from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from .models import EntrepriseA


@require_safe
def liste_entreprises(request):
    entreprises = EntrepriseA.objects.order_by('raison_sociale', 'pk')
    return render(request, 'entreprises/liste.html', {'entreprises': entreprises})


@require_safe
def detail_entreprise(request, pk):
    entreprise = get_object_or_404(EntrepriseA, pk=pk)
    return render(request, 'entreprises/detail.html', {'entreprise': entreprise})
