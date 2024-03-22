from django.contrib import admin
from .models import Ticket, Desconto, Fila

class DescontoAdmin(admin.ModelAdmin):
   def save_model(self, request, obj, form, change):
       obj.auditor = request.user
       super().save_model(request, obj, form, change)
# Register your models here.
admin.site.register(Ticket)
# admin.site.register(Desconto)
admin.site.register(Fila)
admin.site.register(Desconto, DescontoAdmin)


