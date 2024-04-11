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


def upload_excel(request):
    try:
        if request.method == 'POST':
            excel_file = request.FILES['excel_file']
            # Ler a planilha específica
            data = pd.read_excel(
                excel_file, sheet_name='Codigos com desconto automatico')

            # Remover a primeira linha e a primeira coluna
            data = data.iloc[1:, 1:]

            # Definir a primeira linha como cabeçalho
            data.columns = data.iloc[0]
            data = data[1:]

            # Redefinir os índices
            data = data.reset_index(drop=True)

            # Selecionar apenas as colunas desejadas
            data = data[['Tickets', 'Categoria',
                        'Data de Abertura', 'Data de Fechamento']]

            # Converter o DataFrame para um dicionário e retornar uma JsonResponse
            return JsonResponse(data.to_dict(orient='records'), safe=False)
        return render(request, 'upload.html')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
