# Importando as bibliotecas necessárias
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

# Definindo a view HomeView
class HomeView(APIView):
  # Definindo que o usuário precisa estar autenticado para acessar essa view
  permission_classes = (IsAuthenticated, )
  
  # Definindo a resposta para requisições GET
  def get(self, request):
    # Criando o conteúdo da resposta
    content = {'message': f'Olá, {request.user.username}! Login Funcionando'}
    # Retornando a resposta
    return Response(request.user.username)
  
# Definindo a view LogoutView
class LogoutView(APIView):
  # Definindo que o usuário precisa estar autenticado para acessar essa view
  permission_classes = (IsAuthenticated,)
  
  # Definindo a resposta para requisições POST
  def post(self, request):
    try:
      # Obtendo o token de atualização da requisição
      refresh_token = request.data["refresh_token"]
      # Criando um objeto de token a partir do token de atualização
      token = RefreshToken(refresh_token)
      # Adicionando o token à lista de tokens invalidados
      token.blacklist()
      # Retornando uma resposta indicando que o conteúdo foi resetado
      return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
      # Se ocorrer um erro, retorna uma resposta indicando uma requisição inválida
      return Response(status=status.HTTP_400_BAD_REQUEST)
