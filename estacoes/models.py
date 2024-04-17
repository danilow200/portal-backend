from django.db import models

ESTADOS = (
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AM', 'Amazonas'),
    ('AP', 'Amapá'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MG', 'Minas Gerais'),
    ('MS', 'Mato Grosso do Sul'),
    ('MT', 'Mato Grosso'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('PR', 'Paraná'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('RS', 'Rio Grande do Sul'),
    ('SC', 'Santa Catarina'),
    ('SE', 'Sergipe'),
    ('SP', 'São Paulo'),
    ('TO', 'Tocantins')
)
# Create your models here.
class Estacao (models.Model):
    codigo = models.CharField(max_length=15)
    localidade = models.ForeignKey('Localidade', on_delete=models.CASCADE)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    geolocalizacao = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    cedente = models.CharField(max_length=50)
    cm = models.CharField(max_length=50)
    os_padtec = models.CharField(max_length=50)
    lider = models.ForeignKey('Lider', on_delete=models.CASCADE)
    coordenador = models.CharField(max_length=50)

class Localidade (models.Model):
    municipio = models.CharField(max_length=100)
    uf = models.CharField(max_length=50)
    cnl = models.CharField(max_length=50)
    ibge = models.CharField(max_length=50)

class Preventiva (models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE)
    localidade = models.ForeignKey(Localidade, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    cedente = models.CharField(max_length=50)
    cm = models.CharField(max_length=50)
    geolocalizacao = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    periodicidade = models.CharField(max_length=50)
    controle_acesso = models.CharField(max_length=10)
    acompanhamento = models.CharField(max_length=10)
    estrutura = models.CharField(max_length=50)
    cameras = models.IntegerField()

class Tecnico (models.Model):
    nome = models.CharField(max_length=50)
    cpf = models.CharField(max_length=50)
    rg = models.CharField(max_length=50)
    cm = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    telefone = models.CharField(max_length=50)
    lider = models.ForeignKey('Lider', on_delete=models.CASCADE)
    coordenador = models.CharField(max_length=50)

class Lider (models.Model):
    nome = models.CharField(max_length=50)
    estados = models.CharField(max_length=50, choices=ESTADOS, null=True)
    email = models.CharField(max_length=50)
    regiao = models.CharField(max_length=50)
    telefone = models.CharField(max_length=50)