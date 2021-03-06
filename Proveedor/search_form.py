#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField, HiddenField, BooleanField 
from wtforms import SelectMultipleField, DateField, DateTimeField
from wtforms import widgets
from wtforms.validators import DataRequired

etiquetas_data = [('irregulares','Fechas irregulares (Coincidencia de fechas)'),
('cercanas','Fechas cercanas (Fechas menores a 5 dias)'),
('mayor','Montos irregulares (Monto contratado mayor al referencial')]

moneda_data = [('S/.','Soles'),
('US$','Dolares'),
('EUR,$','Euros')]


class SearchFormProveedor(Form):
    page = HiddenField('page')
    proveedor = HiddenField('proveedor')
    term = TextField('term')
    monto = TextField('monto')
    tipo_moneda = SelectMultipleField(
        choices=moneda_data,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
        )

    etiquetas = SelectMultipleField(
        choices=etiquetas_data,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
        )
    fecha_inicial = DateTimeField('Fecha de inicio', format='%Y-%m-%d')
    fecha_final = DateTimeField('Fecha de fin', format='%Y-%m-%d')


class SearchFormEntidad(Form):
    page = HiddenField('page')
    entidad = HiddenField('entidad')
    term = TextField('term')
    monto = TextField('monto')
    tipo_moneda = SelectMultipleField(
        choices=moneda_data,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
        )

    etiquetas = SelectMultipleField(
        choices=etiquetas_data,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
        )
    fecha_inicial = DateTimeField('Fecha de inicio', format='%Y-%m-%d')
    fecha_final = DateTimeField('Fecha de fin', format='%Y-%m-%d')

class SearchTerm(Form):
    termino = TextField('Termino de busqueda')