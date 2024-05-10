from django.urls import path
from . import views
from backend import settings
from django.conf.urls.static import static

urlpatterns = [
    path('import_estacao/', views.import_estacoes, name='import_estacoes'),
    path('upload_localidades/', views.import_localidades, name='upload'),
    path('import_tecnico/', views.import_tecnicos, name='import_tecnicos'),
    # Add more paths here
]

if settings.DEBUG:
    # Adiciona as rotas para servir arquivos estáticos durante o desenvolvimento
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_URL)