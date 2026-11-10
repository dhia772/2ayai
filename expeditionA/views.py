from django.conf import settings
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ExpeditionForm
from .models import Expedition


class ListeExpeditions(ListView):
    template_name = 'expeditions/liste.html'
    context_object_name = 'expeditions'

    def get_queryset(self):
        return (
            Expedition.objects
            .filter(statut='publiee')
            .select_related('entreprise')
            .order_by('-created_at')
        )


class DetailExpedition(DetailView):
    model = Expedition
    template_name = 'expeditions/detail.html'
    context_object_name = 'expedition'
    slug_field = 'reference'
    slug_url_kwarg = 'reference'
    queryset = Expedition.objects.select_related('entreprise')

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte['offres'] = (
            self.object.offres
            .select_related('transporteur', 'vehicule')
            .order_by('-date_proposition', '-pk')
        )
        contexte['actions_demo'] = settings.DEBUG
        return contexte


class DeleteExpedition(DeleteView):
    model = Expedition
    template_name = 'suppression.html'
    slug_field = 'reference'
    slug_url_kwarg = 'reference'
    success_url = reverse_lazy('expeditions:liste')
    http_method_names = ['get', 'head', 'post', 'options']

    def dispatch(self, request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte.update(
            objet=self.object,
            label='l’expédition',
            detail_url='expeditions:detail',
            cle=self.object.reference,
        )
        return contexte

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = get_object_or_404(
                    Expedition.objects.select_for_update(),
                    pk=self.object.pk,
                )
                if self.object.statut == 'publiee':
                    return super().form_valid(form)

                erreur = 'Seules les expéditions publiées peuvent être supprimées.'
        except ProtectedError:
            erreur = 'Cette expédition ne peut pas être supprimée car elle a des offres.'

        contexte = self.get_context_data(form=form, erreur=erreur)
        return self.render_to_response(contexte, status=409)


class CreateExpedition(CreateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = 'expeditions/formulaire.html'
    success_url = reverse_lazy('expeditions:liste')


class UpdateExpedition(UpdateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = 'expeditions/formulaire.html'
    slug_field = 'reference'
    slug_url_kwarg = 'reference'
    success_url = reverse_lazy('expeditions:liste')

    def dispatch(self, request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404
        return super().dispatch(request, *args, **kwargs)
