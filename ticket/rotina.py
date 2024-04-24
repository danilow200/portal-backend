from django.http import JsonResponse
import json
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
from django.utils import timezone
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Código que irá rodar a rotina automaticamente


def rotina(request):
    try:
        # Obtenha o número do ticket da solicitação
        ticket_number = request.GET.get('q')

        if ticket_number:
            url = 'https://report.telebras.com.br/scripts/get_incidentes.php'

            lista_abertura = ['[PAD]$IPFA#', '[PAD]$IPAC#', '[PAD]$IPAR#', '[PAD]$IPAA#',
                              '[PAD]$IPFR#', '[PAD]$IPFE#', '[PAD]$IPOS#', '[PAD]$IPTS#',
                              '[RAD]$IPFA#', '[RAD]$IPAC#', '[RAD]$IPAR#', '[RAD]$IPAA#',
                              '[RAD]$IPFR#', '[RAD]$IPFE#', '[RAD]$IPOS#', '[RAD]$IPTS#',]

            lista_fechamento = ['[PAD]#IPFA$', '[PAD]#IPAC$', '[PAD]#IPAR$', '[PAD]#IPAA$',
                                '[PAD]#IPFR$', '[PAD]#IPFE$', '[PAD]#IPOS$', '[PAD]#IPTS$',
                                '[RAD]#IPFA$', '[RAD]#IPAC$', '[RAD]#IPAR$', '[RAD]#IPAA$',
                                '[RAD]#IPFR$', '[RAD]#IPFE$', '[RAD]#IPOS$', '[RAD]#IPTS$',]

            categoria_dicionario = {
                'IPFA': 'Acesso',
                'IPAC': 'Aguardando CIGR',
                'IPAR': 'Área de Risco',
                'IPAA': 'Atividade Agendada',
                'IPFR': 'Falha Restabelecida',
                'IPFE': 'Falta de Energia',
                'IPOS': 'Outros',
                'IPTS': 'Terceiros'
            }

            lista_tramitacao = [
                'Ocorrências: Direcionamento da tarefa Diagnosticar para o grupo N1',
                'Ocorrências: Direcionamento da tarefa Fechar para o grupo N1',
                'Ocorrências: Direcionamento da tarefa Fechar para o grupo N2_IP',
                'Ocorrências: Direcionamento da tarefa Fechar para o grupo CIM',
                'Ocorrências: Direcionamento da tarefa Restabelecer campo infraestrutura para o grupo Campo_Infra',
                'Ocorrências: Direcionamento da tarefa Restabelecer campo sobressalente para o grupo Campo_Sobressalente',
                'Ocorrências: Direcionamento da tarefa Restabelecer campo despacho para o grupo Campo_Despacho',
                'Ocorrências: Direcionamento da tarefa Restabelecer campo dwdm para o grupo Campo_DWDM',
                'Ocorrências: Direcionamento da tarefa Diagnosticar para o grupo Clientes',
                'Ocorrências: Direcionamento da tarefa Diagnosticar para o grupo N2_DWDM',
                'Ocorrências: Direcionamento da tarefa Diagnosticar para o grupo N2_IP',
                'Ocorrências: Direcionamento da tarefa Diagnosticar para o grupo N2 - Clientes'
            ]

            # Dicionário para armazenar os resultados
            resultados = []

            # Código que irá rodar a rotina automaticamente
            session = requests.Session()

            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontre o formulário e preencha com o número do ticket
            form = soup.find('form')
            form_data = {'ticket': ticket_number}

            # Submeta o formulário e obtenha a nova página
            response = session.post(url, data=form_data)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontre as tabelas na nova página
            tables = soup.find_all('table')

            # Crie um DataFrame para cada tabela
            tabela1 = pd.read_html(str(tables[0]))[
                0] if len(tables) > 0 else None
            tabela2 = pd.read_html(str(tables[1]))[
                0] if len(tables) > 1 else None
            tabela3 = pd.read_html(str(tables[2]))[
                0] if len(tables) > 2 else None

            lista_tabelas = [tabela1, tabela2, tabela3]
            tabelas_modificadas = []

            for tabela in lista_tabelas:
                if tabela is not None and len(tabela.columns) > 4:
                    tabela_modificada = tabela.drop(tabela.columns[4], axis=1)
                    tabelas_modificadas.append(tabela_modificada)
                else:
                    tabelas_modificadas.append(tabela)

            tabela1 = tabelas_modificadas[0]
            tabela2 = tabelas_modificadas[1]
            tabela3 = tabelas_modificadas[2]

            tabela2 = tabela2.iloc[::-1]
            tabela2.columns = range(tabela2.shape[1])
            tabela2 = tabela2.reset_index(drop=True)

            tabela3 = tabela3[['Código Ocorrência',
                               'Informações da ocorrência']]
            tabela3['Informações da ocorrência'] = tabela3['Informações da ocorrência'].astype(
                str)
            tabela3 = tabela3.groupby('Código Ocorrência')[
                'Informações da ocorrência'].agg(' '.join).reset_index()

            # Código que irá criar o dicionário com os descontos
            for i, row in tabela2.iterrows():
                texto = row[4]
                for codigo_texto in lista_abertura:
                    if codigo_texto in texto:
                        # Código de abertura
                        codigo = texto[texto.index(
                            codigo_texto)+5:texto.index(codigo_texto)+11]
                        categoria = categoria_dicionario.get(
                            codigo[1:-1], 'Desconhecido')
                        inicio = row[0]
                        # Crie um novo dicionário para este desconto
                        desconto = {'codigo': codigo, 'inicio': inicio,
                                    'fim': None, 'categoria': categoria}
                        resultados.append(desconto)
                for codigo_texto in lista_fechamento:
                    if codigo_texto in texto:
                        # Código de fechamento
                        codigo = texto[texto.index(
                            codigo_texto)+6:texto.index(codigo_texto)+10]
                        fim = row[0]
                        for desconto in resultados:
                            if codigo in desconto['codigo']:
                                desconto['fim'] = fim

            ultimo_codigo = codigo

            if ultimo_codigo.startswith('$'):
                # O último desconto na lista de resultados é o que não tem um código de fechamento correspondente
                resultados[-1]['fim'] = 'não tem fechamento'
                for tramitacao in lista_tramitacao:
                    if tabela3['Informações da ocorrência'].str.contains(tramitacao, na=False).any():
                        # Encontra a linha correspondente
                        linha = tabela3[tabela3['Informações da ocorrência'].str.contains(
                            tramitacao, na=False)].iloc[0]
                        # Extrai a string completa de "Informações da ocorrência"
                        info_ocorrencia = linha['Informações da ocorrência']
                        # Extrai apenas a data e hora da string
                        hora = info_ocorrencia.split(' - ')[0]
                        # Atribui a hora ao 'fim' do desconto
                        desconto['fim'] = hora
                        break

            return JsonResponse(resultados, safe=False)
        else:
            return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
