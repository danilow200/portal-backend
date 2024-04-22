from django.contrib import admin
from .models import Estacao, Localidade, Preventiva, Tecnico, Lider, Estado, Coordenador

# Register your models here.
admin.site.register(Estacao)
admin.site.register(Localidade)
admin.site.register(Preventiva)
admin.site.register(Tecnico)
admin.site.register(Lider)
admin.site.register(Estado)
admin.site.register(Coordenador)