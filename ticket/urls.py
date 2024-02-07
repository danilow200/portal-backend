# Importando as bibliotecas necessárias
from django.urls import path
from . import views  
from backend import settings
from django.conf.urls.static import static

# Definindo as rotas da aplicação
urlpatterns =[
  # Rota para a página inicial que aponta para a função 'Import_Excel_pandas' em 'views'
  path("",views.Import_Excel_pandas,name="Import_Excel_pandas"),
  # Rota para a página 'Import_Excel_pandas' que também aponta para a função 'Import_Excel_pandas' em 'views'
  path('Import_Excel_pandas/', views.Import_Excel_pandas,name="Import_Excel_pandas"), 
  path('get_tickets/', views.get_tickets, name="get_tickets"),
] 

# Se o modo DEBUG estiver ativado nas configurações
if settings.DEBUG:
  # Adiciona as rotas para servir arquivos estáticos durante o desenvolvimento
  urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)