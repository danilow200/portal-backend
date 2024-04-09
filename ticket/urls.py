# Importando as bibliotecas necessárias
from django.urls import path
from . import views
from backend import settings
from django.conf.urls.static import static
from . import rotina

# Definindo as rotas da aplicação
urlpatterns = [
    # Rota para a página inicial que aponta para a função 'Import_Excel_pandas' em 'views'
    path("", views.Import_Excel_pandas, name="Import_Excel_pandas"),
    # Rota para a página 'Import_Excel_pandas' que também aponta para a função 'Import_Excel_pandas' em 'views'
    path('Import_Excel_pandas/', views.Import_Excel_pandas,
         name="Import_Excel_pandas"),
    path('get_tickets/', views.get_tickets, name="get_tickets"),
    path('get_tickets/<str:filtros>/', views.get_tickets, name="get_tickets"),
    path('update_ticket/<int:ticket_id>/',
         views.update_ticket, name='update_ticket'),
    path('delete_ticket/<int:ticket_id>/',
         views.delete_ticket, name='delete_ticket'),
    path('get_descontos/', views.get_descontos, name="get_descontos"),
    path('post_desconto/<int:ticket_id>/',
         views.post_desconto, name='post_desconto'),
    path('update_desconto/<int:desconto_id>/',
         views.update_desconto, name='update_desconto'),
    path('delete_desconto/<int:desconto_id>/',
         views.delete_desconto, name='delete_desconto'),
    path('exporta_csv/', views.exporta_csv, name='exporta_csv'),
    path('busca_ticket/',
         views.busca_ticket, name='busca_ticket'),
    path('busca_desconto/', views.busca_desconto, name='busca_desconto'),
    path('rotina/', rotina.rotina, name='rotina'),
]

# Se o modo DEBUG estiver ativado nas configurações
if settings.DEBUG:
    # Adiciona as rotas para servir arquivos estáticos durante o desenvolvimento
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_URL)
