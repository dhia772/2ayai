from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='expeditions:liste'), name='accueil'),
    path('admin/', admin.site.urls),
    path('expeditions/', include('expeditionA.urls')),
    path('vehicules/', include('vehiculeA.urls')),
    path('offres/', include('offreA.urls')),
    path('entreprises/', include('entrepriseA.urls')),
]
