#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, g, render_template, url_for, request, redirect
from sqlalchemy import create_engine, or_, and_, func, extract, desc, asc
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from search_form import SearchFormProveedor
from search_form import SearchTerm
from search_form import SearchFormEntidad
import models, settings
import search, advance_search
import json

from flask.ext.cache import Cache

app = Flask(
    __name__,
    static_folder=settings.STATIC_PATH,
    static_url_path=settings.STATIC_URL_PATH
)

#app.config.from_object('settings')

app.config['CACHE_TYPE'] = 'simple'

# register the cache instance and binds it on to your app 
app.cache = Cache(app) 

db_engine = create_engine(
    settings.DATABASE_DSN,
    echo=settings.DEBUG
)

@app.before_request
def before_request():
    g.db = sessionmaker(
        bind=db_engine
    )()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/como', methods=['GET', 'POST'])
#@app.cache.cached(timeout=300)  # cache this view for 5 minutes
def como():
    return render_template('como.html')

@app.route('/acerca', methods=['GET', 'POST'])
#@app.cache.cached(timeout=300)  # cache this view for 5 minutes
def acerca():
    return render_template('acerca.html')

@app.route('/', methods=['GET', 'POST'])
@app.cache.cached(timeout=300)  # cache this view for 5 minutes
def index():

    return render_template(
        'index.html'
    )

def topEmpresas(anio):

    empresas = g.db.query(
                    models.Empresa.id,
                    models.Empresa.razon_social,
                    func.count(models.Contrataciones.empresa_id).label("cant")
                ).join(
                    models.Contrataciones
                ).filter(
                    extract('year', models.Contrataciones.fecha_bue_pro).label("anio") == anio
                ).order_by(
                    func.count(models.Contrataciones.empresa_id).desc()
                ).group_by(
                        models.Empresa.id
                ).limit(15)

    return empresas


def topEntidades(anio):

    entidades = g.db.query(
                    models.EntidadGobierno.id,
                    models.EntidadGobierno.nombre,
                    func.count(models.Contrataciones.entidad_id).label("cant")
                ).join(
                    models.Contrataciones
                ).order_by(
                    func.count(models.Contrataciones.entidad_id).desc()
                ).filter(
                    extract('year', models.Contrataciones.fecha_bue_pro).label("anio") == anio
                ).group_by(
                        models.EntidadGobierno.id
                ).limit(15)

    return entidades

@app.route('/buscar/<string:type>/', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/buscar/<string:type>/<int:page>', methods=['GET', 'POST'])
def buscar(type, page):
    
    form = SearchTerm(request.form)
    
    searchObj = search.Search()
    
    limit = 25

    termino = 'none'

    if request.args.get('termino'):
            
        termino = request.args.get('termino')
    
    if type == "contratos":

        contrataciones, pagination = searchObj.get_results_contrataciones(termino, page, limit)

        if termino == 'none':
            termino = ''
        
        return render_template(
            'buscar.html',
            termino=termino,
            pagination=pagination,
            contrataciones=contrataciones,
        )

    elif type == "entidades":

        entidades, pagination = searchObj.get_results_entidades(termino, page, limit)

        if termino == 'none':
            termino = ''

        return render_template(
            'buscar_entidad.html',
            termino=termino,
            pagination=pagination,
            entidades=entidades
        )

    elif type == "irregulares":

        irregulares, pagination = searchObj.get_results_irregulares(termino, page, limit)

        if termino == 'none':
            termino = ''

        return render_template(
            'buscar_irregulares.html',
            pagination=pagination,
            irregulares=irregulares,
            termino=termino
        )


    elif type == "empresas":

        empresas, pagination = searchObj.get_results_empresas(termino, page, limit)

        if termino == 'none':
            termino = ''

        return render_template(
            'buscar_empresa.html',
            termino=termino,
            pagination=pagination,
            empresas=empresas
        )

    else: 
        return redirect('/')


@app.route('/entidad/<int:id>', methods=['GET', 'POST'])
def entidad(id):

    form = SearchFormEntidad()

    searchObj = advance_search.AdvanceSearchEntidad()

    entidad = g.db.query(
        models.EntidadGobierno.id,
        models.EntidadGobierno.nombre,
        models.TipoGobierno.tipo,
    ).join(
            models.TipoGobierno
    ).filter(
        models.EntidadGobierno.id == id
    ).first()

    page = 1

    if form.page.data:
        page = int(form.page.data)
            
    entidad.contrataciones, pagination = searchObj.get_results_contrataciones(id, form, page, 25)
    entidad.max = searchObj.get_max_ammount(id, form)
    entidad.min = searchObj.get_min_ammount(id, form)

    return render_template(
        'entidad.html',
        entidad=entidad,
        pagination=pagination,
        form=form,
    )


@app.route('/contrato/<int:id>', methods=['GET', 'POST'])
def contrato(id):

    contrato = g.db.query(
        models.Contrataciones.proceso,
        models.Contrataciones.objeto_pro,
        models.Contrataciones.fecha_pub,
        models.Contrataciones.fecha_bue_pro,
        models.Contrataciones.etiqueta_fecha,
        models.Contrataciones.modalidad_sel,
        models.Contrataciones.tipo_moneda,
        models.Contrataciones.monto,
        models.Contrataciones.valor_ref,
        models.Contrataciones.etiqueta_monto,
        models.Contrataciones.descripcion,        
        models.Contrataciones.empresa_id,
        models.Empresa.razon_social,
        models.Empresa.ruc,
        models.Contrataciones.detalle_contrato,
        models.Contrataciones.detalle_seace,
        models.EntidadGobierno.tipo_gobierno_id,
        models.TipoGobierno.tipo,
        models.Contrataciones.entidad_id,
        models.EntidadGobierno.nombre,
    ).join(
        models.Empresa,
        models.EntidadGobierno,
        models.TipoGobierno
    ).filter(
        models.Contrataciones.id == id
    ).first()

    return render_template(
        'contrato.html',
        contrato=contrato,
    )


@app.route('/proveedor/<int:id>', methods=['GET', 'POST'])
def proveedor(id):

    form = SearchFormProveedor()

    searchObj = advance_search.AdvanceSearch()
        
    proveedor = g.db.query(
        models.Empresa
        ).filter(models.Empresa.id == id).first()

    page = 1

    if form.page.data:
        page = int(form.page.data)
            
    proveedor.contrataciones, pagination = searchObj.get_results_contrataciones(id, form, page, 25)
    proveedor.max = searchObj.get_max_ammount(id, form)
    proveedor.min = searchObj.get_min_ammount(id, form)

    return render_template(
    'proveedor.html',
     proveedor=proveedor,
     pagination=pagination,
     form=form
    )


@app.route('/api/get/search/<string:type>', methods=['GET'])
def get_search(type):
    termino = request.args.get('term')
    searchObj = search.Search()
    entidades, pagination = searchObj.get_results_contrataciones(termino, 1, 5)

    list = []

    for e in entidades:
        list.append(e.descripcion)

    return json.dumps(list)

if __name__ == '__main__':
    app.run(
        debug=settings.DEBUG,
    )