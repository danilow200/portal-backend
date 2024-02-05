# Importando o módulo os que fornece uma maneira de usar funcionalidades dependentes do sistema operacional
import os

# Importando a função get_asgi_application do módulo django.core.asgi
from django.core.asgi import get_asgi_application

# Configurando a variável de ambiente 'DJANGO_SETTINGS_MODULE' para apontar para o módulo de configurações do seu projeto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Criando uma instância da aplicação ASGI do Django
application = get_asgi_application()
