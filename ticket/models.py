import pandas as pd
import numpy as np
from django.db import models
from django.utils import timezone
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from django.db.models import Sum, F

CATEGORIAS = (
    ('DWDM', 'DWDM'),
    ('FIBRA', 'FIBRA'),
    ('INFRA', 'INFRA'),
    ('IP', 'IP'),
    ('RADIO', 'RADIO'),
    ('CLIENTE', 'CLIENTE'),
    ('VIASAT', 'VIASAT'),
    ('DESCONHECIDO', 'Desconhecido'),
)

PRIORIDADES = (
    ('ALTA', 'Alta'),
    ('MÉDIA', 'Média'),
    ('BAIXA', 'Baixa'),
)

STATUS = (
    ('VIOLADO', 'Violado'),
    ('NÃO VIOLADO', 'Não Violado'),
    ('DESCONTO MAIOR QUE PERÍODO', 'Desconto maior que período'),
    # Adicione mais status conforme necessário
)

class Fila(models.Model):
    nome = models.CharField(max_length=200)
    entrada = models.CharField(max_length=200)
    saida = models.CharField(max_length=200)

    def __str__(self):
        return self.nome


class Ticket(models.Model):
    ticket = models.IntegerField(primary_key=True)
    estacao = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100)
    prioridade = models.CharField(max_length=50)
    sla = models.CharField(max_length=50)
    atendimento = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    status = models.CharField(max_length=50, choices=STATUS, default='ABERTO')
    filas = models.ManyToManyField(Fila)
    ultimo_desconto_aplicado = models.DurationField(default=timedelta)

    def __str__(self):
        return str(self.ticket)

    def aplicar_desconto(self, desconto):
        h, m, s = map(int, self.atendimento.split(':'))
        atendimento_timedelta = timedelta(hours=h, minutes=m, seconds=s)

        if desconto > atendimento_timedelta:
            self.status = 'DESCONTO MAIOR QUE PERÍODO'
            self.save()
            return

        self.ultimo_desconto_aplicado = desconto
        self.atendimento = self.atendimento_descontado(desconto)
        self.save()

    def reverter_desconto(self, desconto):
        h, m, s = map(int, self.atendimento.split(':'))
        atendimento_timedelta = timedelta(hours=h, minutes=m, seconds=s)

        self.atendimento = str(atendimento_timedelta + desconto)
        self.save()

    def atendimento_descontado(self, desconto):
        h, m, s = map(int, self.atendimento.split(':'))
        atendimento_timedelta = timedelta(hours=h, minutes=m, seconds=s)

        return str(atendimento_timedelta - desconto)


class Desconto(models.Model):
    inicio = models.DateTimeField(default=timezone.now)
    fim = models.DateTimeField(default=timezone.now)
    ticket = models.ForeignKey(
        'Ticket', related_name='descontos', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):

        desconto = self.fim - self.inicio
        super().save(*args, **kwargs)  # chama o método save original

        # Atualiza o campo atendimento do Ticket com o tempo de atendimento descontado
        self.ticket.aplicar_desconto(desconto)

    def delete(self, *args, **kwargs):
        desconto = self.fim - self.inicio
        self.ticket.reverter_desconto(desconto)

        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.fim - self.inicio)

    objects = models.Manager()
