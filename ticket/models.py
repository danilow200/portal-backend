import pandas as pd
import numpy as np
from django.db import models
from django.utils import timezone
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from django.db.models import Sum, F
from django.contrib.auth.models import User
import getpass

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

CATEGORIAS_D = (
    ('Acesso', 'Acesso'),
    ('Aguardando CIGR', 'Aguardando CIGR'),
    ('Área de Risco', 'Área de Risco'),
    ('Atividade Agendada', 'Atividade Agendada'),
    ('Falta de Energia', 'Falta de Energia'),
    ('Sobressalente', 'Sobressalente'),
    ('Terceiros', 'Terceiros'),
    ('Falha Restabelecida', 'Falha Restabelecida'),
    ('Outros', 'Outros'),
)

PRIORIDADES = (
    ('Alta', 'Alta'),
    ('Média', 'Média'),
    ('Baixa', 'Baixa'),
)

STATUS = (
    ('VIOLADO', 'Violado'),
    ('NÃO VIOLADO', 'Não Violado'),
    ('DESCONTO MAIOR QUE PERÍODO', 'Desconto maior que período'),
    ('EXPURGADO', 'Expurgado'),
    ('NEUTRALIZADO', 'Neutralizado'),
)


def converte_hora(input_str):

    # se o desconto for menos de 24h ele já retorna
    if len(input_str.split(":")) == 3 and len(input_str.split(" ")) == 1:
        return input_str

    days_str, time_str = input_str.split(', ')

    # remove a palavra 'days' ou 'day' para obter o número de dias como um inteiro
    days = int(days_str.replace(' days', '').replace(' day', ''))

    hours_str, minutes_str, seconds_str = time_str.split(':')
    hours = int(hours_str)
    minutes = int(minutes_str)
    seconds = int(seconds_str)

    total_hours = days * 24 + hours

    return '{:02}:{:02}:{:02}'.format(total_hours, minutes, seconds)


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
    prioridade = models.CharField(max_length=50, choices=PRIORIDADES)
    sla = models.CharField(max_length=50)
    inicio = models.CharField(max_length=50, null=True)
    fim = models.CharField(max_length=50, null=True)
    atendimento = models.CharField(max_length=50)
    mes = models.CharField(max_length=50, null=True)
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

        atendimento_revertido = atendimento_timedelta + desconto
        total_seconds = int(atendimento_revertido.total_seconds())
        horas_revertidas = total_seconds // 3600
        minutos_revertidos = (total_seconds // 60) % 60
        segundos_revertidos = total_seconds % 60

        self.atendimento = f"{horas_revertidas:02d}:{minutos_revertidos:02d}:{segundos_revertidos:02d}"
        self.save()

    def save(self, *args, **kwargs):
        if self.status == 'NEUTRALIZADO':
            self.atendimento = self.sla
        super().save(*args, **kwargs)

    def atendimento_descontado(self, desconto):
        h, m, s = map(int, self.atendimento.split(':'))
        atendimento_timedelta = timedelta(hours=h, minutes=m, seconds=s)

        return converte_hora(str(atendimento_timedelta - desconto))


class Desconto(models.Model):
    inicio = models.DateTimeField(default=datetime.min)
    fim = models.DateTimeField(default=datetime.min)
    desconto_anterior = models.DurationField(default=timedelta)
    ticket = models.ForeignKey(
        'Ticket', related_name='descontos', on_delete=models.CASCADE)
    aplicado = models.BooleanField(default=False)
    aplicado_anterior = models.BooleanField(default=False)
    categoria = models.CharField(max_length=150, choices=CATEGORIAS_D)
    auditor = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        usuario_autenticado = kwargs.pop('username', None)

        if usuario_autenticado:
            self.auditor = usuario_autenticado

        inicio_ticket = timezone.make_aware(
            datetime.strptime(self.ticket.inicio, "%d/%m/%Y %H:%M:%S"))
        fim_ticket = timezone.make_aware(
            datetime.strptime(self.ticket.fim, "%d/%m/%Y %H:%M:%S"))

        if self.inicio < inicio_ticket or self.fim > fim_ticket:
            raise ValueError(
                "Os campos 'inicio' e 'fim' do Desconto devem estar dentro do intervalo do Ticket correspondente.")

        desconto_atual = self.fim - self.inicio
        diferenca_desconto = desconto_atual - self.desconto_anterior

        if self.aplicado:
            self.aplicado_anterior = True
            if not self.desconto_anterior == desconto_atual:
                self.ticket.aplicar_desconto(diferenca_desconto)
                self.desconto_anterior = desconto_atual

        super().save(*args, **kwargs)

        if self.aplicado and not self.desconto_anterior == desconto_atual:
            self.ticket.aplicar_desconto(diferenca_desconto)
            self.desconto_anterior = desconto_atual
            super().save(*args, **kwargs)

        if self.aplicado_anterior and not self.aplicado:
            self.ticket.reverter_desconto(self.desconto_anterior)
            self.desconto_anterior = timedelta()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        desconto = self.fim - self.inicio
        self.ticket.reverter_desconto(desconto)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket} - {converte_hora(str(self.fim - self.inicio))}"

    objects = models.Manager()
