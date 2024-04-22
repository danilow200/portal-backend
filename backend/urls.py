# Importando as bibliotecas necessárias
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

# Definindo as rotas da aplicação
urlpatterns = [
    # Rota para a página de administração do Django
    path('admin/', admin.site.urls),
    # Rota para obter um par de tokens (acesso e atualização) usando a biblioteca 'rest_framework_simplejwt'
    path('token/', 
          jwt_views.TokenObtainPairView.as_view(), 
          name ='token_obtain_pair'),
    # Rota para atualizar um token de acesso usando um token de atualização
    path('token/refresh/', 
          jwt_views.TokenRefreshView.as_view(), 
          name ='token_refresh'),
    # Incluindo as rotas definidas no aplicativo 'authentification'
    path('', include('authentification.urls')),
    # Incluindo as rotas definidas no aplicativo 'ticket'
    path('',include('ticket.urls')),
    path('',include('estacoes.urls')),
]
