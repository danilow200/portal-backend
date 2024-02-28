import pandas as pd
import numpy as np
from django.db import models
from django.utils import timezone

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
  filas = models.ManyToManyField(Fila)

  def __str__(self):
      return str(self.ticket)

class Desconto(models.Model):
  inicio = models.DateTimeField(default=timezone.now)
  fim = models.DateTimeField(default=timezone.now)
  ticket = models.ForeignKey('Ticket', related_name='descontos', on_delete=models.CASCADE)

  def __str__(self):
     return str(self.fim - self.inicio)

  objects = models.Manager()
