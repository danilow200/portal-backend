import pandas as pd
import numpy as np
from django.db import models

class Ticket(models.Model):
  ticket = models.CharField(max_length=200)
  fila = models.CharField(max_length=200)
  entrada = models.CharField(max_length=200)
  saida = models.CharField(max_length=200)

  def __str__(self):
    return self.fila
                
  objects = models.Manager()