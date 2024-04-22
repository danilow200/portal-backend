from django.shortcuts import render
import pandas as pd
from django.db import transaction
from .models import Estacao, Localidade, Lider
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

@csrf_exempt
def import_excel_to_estacao(request):
    try:
        if request.method == 'POST' and 'myfile' in request.FILES:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            # Load the Excel spreadsheet into a pandas DataFrame
            df = pd.read_excel(filename, skiprows=2, index_col=False)
            print(df)

            # Create stations
            create_estacoes(df)
            return JsonResponse(df.to_dict(safe=False))
        return render(request, 'import_estacao.html')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def create_estacoes(df):
    with transaction.atomic():
        for _, row in df.iterrows():
            # Find the corresponding locality or create a new one
            localidade, _ = Localidade.objects.get_or_create(localidade=row['Localidade'])

            lider, _ = Lider.objects.get_or_create(nome=row['Lider'])

            # Create a new instance of the Estacao model
            estacao = Estacao(
                codigo=row['Estação'],
                localidade=localidade,
                descricao=row['Descrição'],
                tipo=row['Tipo'],
                status=row['Status'],
                latitude=row['Latitude'],
                longitude=row['Longitude'],
                cedente=row['Cedente'],
                cm=row['CM'],
                os_padtec=row['OS Padtec'],
                lider=lider,
            )
            estacao.save()
