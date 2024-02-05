"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

# Importando o módulo os que fornece uma maneira de usar funcionalidades dependentes do sistema operacional
import os

# Importando a função get_wsgi_application do módulo django.core.wsgi
from django.core.wsgi import get_wsgi_application

# Configurando a variável de ambiente 'DJANGO_SETTINGS_MODULE' para apontar para o módulo de configurações do seu projeto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Criando uma instância da aplicação WSGI do Django
application = get_wsgi_application()
