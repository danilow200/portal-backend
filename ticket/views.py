from http.client import HTTPResponse
from django.shortcuts import render
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from .models import Ticket

# Create your views here.

def Import_Excel_pandas(request):
    if request.method == 'POST' and request.FILES['myfile']:      
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)              
        empexceldata = pd.read_csv(filename, encoding='ISO-8859-1', index_col=False)
        empexceldata = empexceldata.loc[empexceldata['Incidente - ITSM.Número do incidente'] != ' ']
        dbframe = empexceldata
        for _, row in dbframe.iterrows():
            obj = Ticket.objects.create(ticket=row['Incidente - ITSM.Número do incidente'], fila=row['Tarefas do Incidente - ITSM.Grupo executor'],
                                            entrada=row['Tarefas do Incidente - ITSM.Entrou na fila em'], saida=row['Tarefas do Incidente - ITSM.Tarefa executada em'])           
            obj.save()
        return render(request, 'Import_excel_db.html', {
            'uploaded_file_url': uploaded_file_url
        })   
    return render(request, 'Import_excel_db.html',{})



from tablib import Dataset
from .resources import TicketResource

def Import_excel(request):
    if request.method == 'POST' :
        Ticket =TicketResource()
        dataset = Dataset()
        new_ticket = request.FILES['myfile']
        data_import = dataset.load(new_ticket.read())
        result = TicketResource.import_data(dataset,dry_run=True)
        if not result.has_errors():
            TicketResource.import_data(dataset,dry_run=False)        
    return render(request, 'Import_excel_db.html',{})