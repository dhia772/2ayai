from django.urls import path
from . import views

app_name = 'entreprises'

urlpatterns = [
    path('', views.liste_entreprises, name='liste'),
    path('<int:pk>/', views.detail_entreprise, name='detail'),
]
