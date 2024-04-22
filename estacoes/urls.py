from django.urls import path
from . import views
from backend import settings
from django.conf.urls.static import static

urlpatterns = [
    path('import_excel_to_estacao/', views.import_excel_to_estacao, name='import_excel_to_estacao'),
    # Add more paths here
]

if settings.DEBUG:
    # Adiciona as rotas para servir arquivos estáticos durante o desenvolvimento
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_URL)