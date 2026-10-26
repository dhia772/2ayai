from django.contrib.admin import AdminSite
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone


class TransConnectAdminSite(AdminSite):
    site_header = 'TransConnect | Opérations'
    site_title = 'TransConnect Admin'
    index_title = 'Pilotage des expéditions et de la flotte'
    index_template = 'admin/transconnect_index.html'

    def get_urls(self):
        return [path('health-check/', self.admin_view(self.health_check), name='health_check')] + super().get_urls()

    def health_check(self, request):
        from config.health import integrity_checks
        permissions = ['EntrepriseA.view_entreprisea', 'VehiculeA.view_vehicule', 'ExpeditionA.view_expedition', 'OffreA.view_offre']
        if not request.user.has_perms(permissions):
            raise PermissionDenied
        checks = integrity_checks()
        context = {**self.each_context(request), 'title': 'Contrôle d’intégrité', 'checks': checks, 'total': sum(c['count'] for c in checks), 'generated_at': timezone.now()}
        if request.GET.get('format') == 'json':
            response = JsonResponse({k: context[k] for k in ('checks', 'total', 'generated_at')}, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            response['Content-Disposition'] = 'attachment; filename="integrity-report.json"'
            return response
        return TemplateResponse(request, 'admin/health_check.html', context)
