from http.client import HTTPResponse
from django.shortcuts import render
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from .models import Ticket, Fila

def convert_date(date_string):
  date, time = date_string.split(' ')
  day, month, year = date.split('/')
  hour, minute, second = time.split(':')
  return f'{year}-{month}-{day}T{hour}:{minute}:{second}.000Z'

# Create your views here.

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
                if row['Tarefas do Incidente - ITSM.Grupo executor'] in lista_de_filas:
                    fila = Fila.objects.create(nome=row['Tarefas do Incidente - ITSM.Grupo executor'],
                                    entrada=convert_date(row['Tarefas do Incidente - ITSM.Entrou na fila em']), 
                                    saida=convert_date(row['Tarefas do Incidente - ITSM.Tarefa executada em']))           
                    fila.save()
                    ticket, created = Ticket.objects.get_or_create(ticket=row['Incidente - ITSM.Número do incidente'])
                    ticket.filas.add(fila)
                    ticket.save()
            
        return render(request, 'Import_excel_db.html', {
            'uploaded_file_url': uploaded_file_url
        })   
    return render(request, 'Import_excel_db.html',{})

