from django.shortcuts import render
import pandas as pd
import csv
from django.db import transaction
from .models import Estacao, Localidade, Lider, Estado, Tecnico
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

@csrf_exempt
def import_localidades(request):
    try:
        if request.method == 'POST' and 'myfile' in request.FILES:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            localidades_data = pd.read_csv(filename, encoding='UTF-8', index_col=False, dtype={'IBGE': str})
            localidades_data = localidades_data.dropna()

            for index, row in localidades_data.iterrows():
                estado, created = Estado.objects.get_or_create(nome=row['UF'])
                localidade = Localidade(localidade=row['Município'], uf=estado, cnl=row['CNL'], ibge=row['IBGE'])
                localidade.save()

            return JsonResponse({
                'uploaded_file_url': uploaded_file_url,
                'message': 'Todas as operações de banco de dados foram concluídas.'
            })
    except Exception as e:
        return JsonResponse({'burro': str(e)}, status=500)
    return render(request, 'upload_localidades.html', {})

@csrf_exempt
def import_estacoes(request):
    if request.method == 'POST' and 'myfile' in request.FILES:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        estacoes_data = pd.read_excel(filename, skiprows=2)
        # estacoes_data = estacoes_data.dropna()

        for index, row in estacoes_data.iterrows():
            municipio, uf = row['Localidade'].split(' - ')
            localidade = Localidade.objects.filter(localidade=municipio, uf__nome=uf).first()

            if localidade is not None:
                estacao = Estacao(codigo=row['Estação'], localidade=localidade, descricao=row['Descrição'], 
                                  tipo=row['Tipo'], status=row['Status'], cedente=row['Cedente'], 
                                  os_padtec=row['OS Padtec'], latitude=row['Latitude'], longitude=row['Longitude'], cm=row['CM'])
                estacao.save()

        return JsonResponse({
            'uploaded_file_url': uploaded_file_url,
            'message': 'Todas as operações de banco de dados foram concluídas.'
        })
    return render(request, 'import_estacao.html', {})

@csrf_exempt
def import_tecnicos(request):
    if request.method == 'POST' and 'myfile' in request.FILES:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        tecnicos_data = pd.read_csv(filename, encoding='utf-8-sig')
        for index, row in tecnicos_data.iterrows():
            nome_lider = row['Lider']
            lider = None
            if pd.notna(nome_lider):
                try:
                    lider = Lider.objects.get(nome=nome_lider)
                except ObjectDoesNotExist:
                    print(f"Líder {nome_lider} não encontrado.")
            Tecnico.objects.create(
                nome=row['Nome'],
                cm=row['CM'],
                rg=row['RG'],
                cpf=row['CPF'],
                email=row['E-mail'],
                telefone=row['Telefone'],
                lider=lider
            )

        return JsonResponse({
            'uploaded_file_url': uploaded_file_url,
            'message': 'Todas as operações de banco de dados foram concluídas.'
        })
    return render(request, 'import_tecnico.html', {})
