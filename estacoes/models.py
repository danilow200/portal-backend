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

    def __str__(self):
        return self.codigo

class Estado(models.Model):
    nome = models.CharField(max_length=50, choices=ESTADOS)
    def __str__(self):
        return self.nome

class Localidade (models.Model):
    localidade = models.CharField(max_length=100)
    uf = models.ForeignKey(Estado, on_delete=models.CASCADE)
    cnl = models.CharField(max_length=50)
    ibge = models.CharField(max_length=50)

    def __str__(self):
        return self.localidade

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

    def __str__(self):
        return self.estacao
    
class Tecnico (models.Model):
    nome = models.CharField(max_length=50)
    cpf = models.CharField(max_length=50)
    rg = models.CharField(max_length=50)
    cm = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    telefone = models.CharField(max_length=50)
    lider = models.ForeignKey('Lider', on_delete=models.CASCADE)
    coordenador = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
    
class Lider (models.Model):
    nome = models.CharField(max_length=50)
    estados = models.ManyToManyField(Estado, blank=True)
    email = models.CharField(max_length=50)
    telefone = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
    
class Coordenador (models.Model):
    nome = models.CharField(max_length=50)
    estados = models.ManyToManyField(Estado, blank=True)
    email = models.CharField(max_length=50)
    telefone = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

