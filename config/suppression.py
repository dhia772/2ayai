from django.conf import settings
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render


def traiter_suppression(request, model, lookup, namespace, label, verifier):
    if not settings.DEBUG:
        raise Http404

    if request.method == 'GET':
        objet = get_object_or_404(model, **lookup)
        erreur = None
    else:
        with transaction.atomic():
            objet = get_object_or_404(model.objects.select_for_update(), **lookup)
            erreur = verifier(objet)
            if not erreur:
                try:
                    objet.delete()
                except ProtectedError:
                    erreur = 'Cet élément est lié à d’autres données et ne peut pas être supprimé.'
                else:
                    return redirect(f'{namespace}:liste')

    return render(request, 'suppression.html', {
        'objet': objet,
        'label': label,
        'detail_url': f'{namespace}:detail',
        'cle': next(iter(lookup.values())),
        'erreur': erreur,
    }, status=409 if erreur else 200)
