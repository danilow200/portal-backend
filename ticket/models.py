import pandas as pd
import numpy as np
from django.db import models

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
  prioridade = models.IntegerField()
  sla = models.CharField(max_length=50)
  atendimento = models.CharField(max_length=50)
  categoria = models.CharField(max_length=50)
  filas = models.ManyToManyField(Fila)

  def __str__(self):
      return self.fila.nome

  objects = models.Manager()
