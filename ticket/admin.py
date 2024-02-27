from django.contrib import admin
from .models import Ticket, Desconto, Fila

# Register your models here.
admin.site.register(Ticket)
admin.site.register(Desconto)
admin.site.register(Fila)

