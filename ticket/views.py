# Importando as bibliotecas necessárias
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.shortcuts import render
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from .models import Ticket, Fila, Desconto
from django.shortcuts import get_object_or_404

# Função para converter uma string de data e hora para o formato ISO 8601
def convert_date(date_string):
  date, time = date_string.split(' ')
  day, month, year = date.split('/')
  hour, minute, second = time.split(':')
  return f'{year}-{month}-{day}T{hour}:{minute}:{second}.000Z'

def Import_Excel_pandas(request):
    if request.method == 'POST' and request.FILES['myfile']: 
        lista_de_filas = ['Campo Infraestrutura', 'Campo Despacho', 'Campo DWDM', 'GMP', 
                          'Campo Sobressalente', 'Campo IP Core', 'Campo Ip Metro', 'Campo Fibra']
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)              
        empexceldata = pd.read_csv(filename, encoding='ISO-8859-1', index_col=False)
        empexceldata = empexceldata.loc[empexceldata['Incidente - ITSM.Número do incidente'] != ' ']
        dbframe = empexceldata
        for index, row in dbframe.iterrows():
            if row['Incidente - ITSM.Número do incidente do pai'] == ' ':
                fila = Fila.objects.create(nome=row['Tarefas do Incidente - ITSM.Grupo executor'],
                                entrada=convert_date(row['Tarefas do Incidente - ITSM.Entrou na fila em']), 
                                saida=convert_date(row['Tarefas do Incidente - ITSM.Tarefa executada em']))           
                fila.save()
                ticket, created = Ticket.objects.get_or_create(ticket=row['Incidente - ITSM.Número do incidente'], estacao=row['Incidente - ITSM.Localização'], descricao=row['Incidente - ITSM.Causa'], prioridade=row['Incidente - ITSM.Urgência'], sla=row['Incidente - ITSM.Prazo do SLA no formato H:MM'], atendimento=row['Incidente - ITSM.Tempo total no formato H:MM:SS'], categoria=row['Incidente - ITSM.Categoria de Atuação'])
                ticket.filas.add(fila)
                if any(f.nome in lista_de_filas for f in ticket.filas.all()):
                    ticket.save()
                else:
                    ticket.delete()
        return render(request, 'Import_excel_db.html', {
            'uploaded_file_url': uploaded_file_url
        })   
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
                'estacao': ticket.estacao,
                'descricao': ticket.descricao,
                'prioridade': ticket.prioridade,
                'sla': ticket.sla,
                'atendimento': ticket.atendimento,
                'categoria': ticket.categoria,
                'filas': filas_list
            })
        # Retorna os tickets e as filas associadas como uma resposta HTTP
        return JsonResponse(tickets_list, safe=False)
    
# def create_desconto(request, ticket_id):
#     ticket = get_object_or_404(Ticket, pk=ticket_id)
#     ticket.atendimento = ticket.atendimento_descontado()
#     print(ticket.atendimento)
#     # ticket.save()