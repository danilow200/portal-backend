# Importando as bibliotecas necessárias
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.shortcuts import render
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from .models import Ticket, Fila, Desconto
from django.shortcuts import get_object_or_404
import csv
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

mes_ticket = {
    '01': 'Janeiro',
    '02': 'Fevereiro',
    '03': 'Março',
    '04': 'Abril',
    '05': 'Maio',
    '06': 'Junho',
    '07': 'Julho',
    '08': 'Agosto',
    '09': 'Setembro',
    '10': 'Outubro',
    '11': 'Novembro',
    '12': 'Dezembro'
}
# Função para converter uma string de data e hora para o formato ISO 8601


def convert_date(date_string):
    date, time = date_string.split(' ')
    day, month, year = date.split('/')
    hour, minute, second = time.split(':')
    return f'{year}-{month}-{day}T{hour}:{minute}:{second}.000Z'


def convert_mes(date_string):
    date, time = date_string.split(' ')
    day, month, year = date.split('/')
    return f'{mes_ticket[month]} - {year}'


def convert_formato_sla(time_str):
    mm, ss = map(int, time_str.split(':'))
    hh = mm // 60
    mm = mm % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def compara_data(data1, data2):
    formato = "%d/%m/%Y %H:%M:%S"
    data1_convertida = datetime.strptime(data1, formato)
    data2_convertida = datetime.strptime(data2, formato)

    return data1_convertida >= data2_convertida


@csrf_exempt
def Import_Excel_pandas(request):
    if request.method == 'POST' and 'myfile' in request.FILES:
        lista_de_filas = ['Campo Infraestrutura', 'Campo Despacho', 'Campo DWDM', 'GMP',
                          'Campo IP Core', 'Campo Ip Metro', 'Campo Fibra']
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        empexceldata = pd.read_csv(
            filename, encoding='ISO-8859-1', index_col=False)
        empexceldata = empexceldata.loc[empexceldata['Incidente - ITSM.Número do incidente'] != ' ']
        dbframe = empexceldata

        filas_salvas = []
        ticket_atual = dbframe['Incidente - ITSM.Número do incidente'][0]

        for index, row in dbframe.iterrows():
            if ticket_atual != row['Incidente - ITSM.Número do incidente']:
                ticket_atual = row['Incidente - ITSM.Número do incidente']
                filas_salvas = []

            if row['Incidente - ITSM.Número do incidente do pai'] == ' ' and ticket_atual == row['Incidente - ITSM.Número do incidente']:
                fila_nome = row['Tarefas do Incidente - ITSM.Grupo executor']
                fila_entrada = convert_date(
                    row['Tarefas do Incidente - ITSM.Entrou na fila em'])
                fila_saida = convert_date(
                    row['Tarefas do Incidente - ITSM.Tarefa executada em'])

                if compara_data(row['Tarefas do Incidente - ITSM.Entrou na fila em'], row['Incidente - ITSM.Data/hora de criação do incidente']):
                    valida = True
                    for fila_test in filas_salvas:
                        if fila_test.entrada == fila_entrada or fila_test.saida == fila_saida:
                            valida = False
                    if valida:
                        fila = Fila(nome=fila_nome,
                                    entrada=fila_entrada, saida=fila_saida)
                        fila.save()

                        filas_salvas.append(fila)

            if any(fila_salva.nome in lista_de_filas for fila_salva in filas_salvas) and ticket_atual == row['Incidente - ITSM.Número do incidente']:
                ticket = Ticket(ticket=row['Incidente - ITSM.Número do incidente'], estacao=row['Incidente - ITSM.Localização'],
                                descricao=row['Incidente - ITSM.Causa'], prioridade=row['Incidente - ITSM.Urgência'],
                                sla=convert_formato_sla(
                                    row['Incidente - ITSM.Prazo do SLA no formato H:MM']),
                                inicio=row['Incidente - ITSM.Data/hora de criação do incidente'],
                                fim=row['Incidente - ITSM.Fechado em_1'],
                                atendimento=row['Incidente - ITSM.Tempo total no formato H:MM:SS'],
                                mes=convert_mes(
                                    row['Incidente - ITSM.Fechado em_1']),
                                categoria=row['Incidente - ITSM.Categoria de Atuação'], status='ABERTO')
                ticket.save()  # Salve o objeto Ticket antes de adicionar uma Fila
                ticket.filas.add(*filas_salvas)

        return JsonResponse({
            'uploaded_file_url': uploaded_file_url,
            'message': 'Todas as operações de banco de dados foram concluídas.'
        })
    return render(request, 'Import_excel_db.html', {})


def get_tickets(request, filtros=None):
    mes_atendimento = request.GET.get('mes_atendimento', None)
    tickets = Ticket.objects.all()

    if mes_atendimento or filtros:
        tickets = tickets.filter(
            Q(mes=mes_atendimento) | Q(prioridade=filtros) | Q(categoria=filtros) |
            Q(status=filtros) | Q(filas__nome=filtros)
        ).distinct()

    context = {"tickets": tickets}  # Tornar global

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

        descontos = ticket.descontos.all()
        descontos_list = []
        for desconto in descontos:
            descontos_list.append({
                'inicio': desconto.inicio,
                'fim': desconto.fim,
                'aplicado': desconto.aplicado
            })
        # Adiciona os detalhes do ticket e das filas associadas à lista de tickets
        tickets_list.append({
            'ticket': ticket.ticket,
            'estacao': ticket.estacao,
            'descricao': ticket.descricao,
            'prioridade': ticket.prioridade,
            'sla': ticket.sla,
            'inicio': ticket.inicio,
            'fim': ticket.fim,
            'mes': ticket.mes,
            'atendimento': ticket.atendimento,
            'categoria': ticket.categoria,
            'status': ticket.status,
            'filas': filas_list,
            'descontos': descontos_list
        })
    # Retorna os tickets e as filas associadas como uma resposta HTTP
    return JsonResponse(tickets_list, safe=False)


@csrf_exempt
def update_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            # Obtém o ticket que precisa ser atualizado
            ticket = Ticket.objects.get(ticket=ticket_id)

            # Atualiza os atributos do ticket com os dados enviados na requisição
            for key, value in request.POST.items():
                setattr(ticket, key, value)

            # Salva as alterações no banco de dados
            ticket.save()

            return JsonResponse({'status': 'success'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def delete_ticket(request, ticket_id):
    if request.method == 'DELETE':
        try:
            # Obtém o ticket que precisa ser deletado
            ticket = Ticket.objects.get(ticket=ticket_id)

            # Deleta todas as filas associadas ao ticket
            ticket.filas.all().delete()

            # Deleta o ticket
            ticket.delete()

            return JsonResponse({'status': 'success'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def exporta_csv(request):
    # Cria uma resposta HTTP do tipo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tickets.csv"'

    # Cria um escritor CSV
    writer = csv.writer(response)
    # Escreve o cabeçalho do CSV
    writer.writerow(['Ticket', 'Estação', 'Descrição', 'Prioridade',
                    'SLA', 'Atendimento', 'Categoria', 'Status', 'Filas'])

    # Obtém todos os tickets do banco de dados
    tickets = Ticket.objects.all()

    # Itera sobre cada ticket
    for ticket in tickets:
        # Obtém as filas associadas ao ticket
        filas = ticket.filas.all()
        # Prepara uma lista para armazenar os nomes das filas
        filas_nomes = [fila.nome for fila in filas]
        # Escreve os detalhes do ticket e das filas associadas no CSV
        writer.writerow([ticket.ticket, ticket.estacao, ticket.descricao, ticket.prioridade,
                        ticket.sla, ticket.atendimento, ticket.categoria, ticket.status, ', '.join(filas_nomes)])

    return response


def get_descontos(request):
    descontos = Desconto.objects.all()

    print(descontos)

    descontos_list = []
    for desconto in descontos:
        descontos_list.append({
            'ticket': desconto.ticket.ticket,
            'inicio': desconto.inicio,
            'fim': desconto.fim,
            'aplicado': desconto.aplicado
        })

    return JsonResponse(descontos_list, safe=False)


def define_auditor(request):
    usuario_logado = request.user.username
    Desconto.auditor = usuario_logado
# def create_desconto(request, ticket_id):
#     ticket = get_object_or_404(Ticket, pk=ticket_id)
#     ticket.atendimento = ticket.atendimento_descontado()
#     print(ticket.atendimento)
#     # ticket.save()
