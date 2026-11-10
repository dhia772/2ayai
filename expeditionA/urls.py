from django.urls import path

from . import views

app_name = 'expeditions'

urlpatterns = [
    path('', views.ListeExpeditions.as_view(), name='liste'),
    path('ajouter/', views.CreateExpedition.as_view(), name='ajouter'),
    path('<str:reference>/', views.DetailExpedition.as_view(), name='detail'),
    path('<str:reference>/modifier/', views.UpdateExpedition.as_view(), name='modifier'),
    path(
        '<str:reference>/supprimer/',
        views.DeleteExpedition.as_view(),
        name='supprimer',
    ),
]
