# Importando as bibliotecas necessárias
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.shortcuts import render
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from .models import Ticket, Fila

# Função para converter uma string de data e hora para o formato ISO 8601
def convert_date(date_string):
  date, time = date_string.split(' ')
  day, month, year = date.split('/')
  hour, minute, second = time.split(':')
  return f'{year}-{month}-{day}T{hour}:{minute}:{second}.000Z'

# Função de view para importar um arquivo Excel
def Import_Excel_pandas(request):
    # Verifica se a requisição é do tipo POST e se um arquivo foi enviado
    if request.method == 'POST' and request.FILES['myfile']: 

        # Lista de grupos de execução
        lista_de_filas = ['Campo Infraestrutura', 'Campo Despacho', 'Campo DWDM', 'GMP', 
                          'Campo Sobressalente', 'Campo IP Core', 'Campo Ip Metro', 'Campo Fibra']

        # Obtém o arquivo enviado na requisição
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        # Salva o arquivo no sistema de arquivos
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)              
        # Lê o arquivo em um DataFrame do pandas
        empexceldata = pd.read_csv(filename, encoding='ISO-8859-1', index_col=False)
        # Filtra o DataFrame para remover linhas onde o número do incidente é um espaço em branco
        empexceldata = empexceldata.loc[empexceldata['Incidente - ITSM.Número do incidente'] != ' ']
        dbframe = empexceldata
        # Itera sobre cada linha do DataFrame
        for index, row in dbframe.iterrows():
            # Se o número do incidente pai for um espaço em branco e o grupo executor estiver na lista_de_filas
            if row['Incidente - ITSM.Número do incidente do pai'] == ' ':
                if row['Tarefas do Incidente - ITSM.Grupo executor'] in lista_de_filas:
                    # Cria um novo objeto Fila e salva no banco de dados
                    fila = Fila.objects.create(nome=row['Tarefas do Incidente - ITSM.Grupo executor'],
                                    entrada=convert_date(row['Tarefas do Incidente - ITSM.Entrou na fila em']), 
                                    saida=convert_date(row['Tarefas do Incidente - ITSM.Tarefa executada em']))           
                    fila.save()
                    # Obtém ou cria um novo objeto Ticket e adiciona a Fila a ele
                    ticket, created = Ticket.objects.get_or_create(ticket=row['Incidente - ITSM.Número do incidente'])
                    ticket.filas.add(fila)
                    ticket.save()
            
        # Renderiza a página 'Import_excel_db.html' com a URL do arquivo enviado
        return render(request, 'Import_excel_db.html', {
            'uploaded_file_url': uploaded_file_url
        })   
    # Se a requisição não for do tipo POST ou não tiver um arquivo, renderiza a página 'Import_excel_db.html' sem a URL do arquivo
    return render(request, 'Import_excel_db.html',{})

def get_tickets(request):
    if request.method == 'GET':
        # Obtém todos os tickets do banco de dados
        tickets = Ticket.objects.all()
        # Prepara uma lista para armazenar os dados dos tickets
        tickets_list = []
        # Itera sobre cada ticket
        for ticket in tickets:
            # Obtém as filas associadas ao ticket
            filas = ticket.filas.all()
            # Prepara uma lista para armazenar os dados das filas
            filas_list = []
            # Itera sobre cada fila
            for fila in filas:
                # Adiciona os detalhes da fila à lista de filas
                filas_list.append({
                    'nome': fila.nome,
                    'entrada': fila.entrada,
                    'saida': fila.saida
                })
            # Adiciona os detalhes do ticket e das filas associadas à lista de tickets
            tickets_list.append({
                'ticket': ticket.ticket,
                'filas': filas_list
            })
        # Retorna os tickets e as filas associadas como uma resposta HTTP
        return JsonResponse(tickets_list, safe=False)