# -*- coding: utf-8 -*-
# Created on Mon Oct 28 09:13:22 2019
# @author: pabmontenegro

import pandas as pd
import numpy as np
import datetime
from sodapy import Socrata
#from selenium import webdriver
import webbrowser

direccion_metatabla="https://dl.dropboxusercontent.com/s/84lt7ddrt73vzzu/tabla_final.txt?dl=0"

def sodapy_base(api_id,token=None,limite_filas=1000000000):
    """ La función se conecta al API de Socrata y retorna la base de datos descargada del Portal de Datos Abiertos
    como dataframe.

    :param api_id: (str) Identificación de la base de datos asociado con la API de Socrata.
    :param token: (str) *opcional* - token de usuario de la API Socrata.
    :return: base de datos en formato dataframe.
    """
    client = Socrata("www.datos.gov.co",
                     app_token=token)

    results = client.get(api_id,limit=limite_filas)
    base_original = pd.DataFrame.from_records(results)
    return(base_original)

# OBTENER LA TABLA QUE TIENE DATOS ABIERTOS CON INFORMACIÓN DE LAS BASES DE DATOS
def asset_inventory(token=None,limite_filas=1000000000):
    """ Se conecta al API de Socrata y retorna la base de datos *Asset Inventory* descargada del Portal de Datos Abiertos
    como dataframe. Este conjunto de datos es un inventario de los recursos en el sitio.

    :param token: (str) *opcional* - token de usuario de la API Socrata.
    :return: base de datos en formato dataframe.
    """
    client = Socrata("www.datos.gov.co",app_token=token)
    results = client.get("uzcf-b9dh",limit=limite_filas)
    asset_inventory = pd.DataFrame.from_records(results)
    return(asset_inventory)

def asset_inventory_espanol(token=None):
    """ Se conecta al API de Socrata y retorna la base de datos *Asset Inventory* descargada del Portal de Datos Abiertos
    como dataframe, selecciona columnas de interés y las renombra con un término en español. Este conjunto de datos es un inventario de los recursos en el sitio.

    :param token: (str) *opcional* - token de usuario de la API Socrata.
    :return: base de datos en formato dataframe.
    """
    asset=asset_inventory(token=token)
    
    dic_rename={
         "uid":"numero_api",
         "name":"nombre",
         "description":"descripcion",
         "owner":"dueno",
         "type":"tipo",
         "category":"categoria",
         "tags":"terminos_clave",
         "url":"url",
         "creation_date":"fecha_creacion",
         "last_data_updated_date":"fecha_actualizacion",
         "informacindedatos_frecuenciadeactualizacin":"actualizacion_frecuencia",
         "row_count":"filas",
         "column_count":"columnas",
         "contact_email":"correo_contacto",
         "license":"licencia",
         "attribution":"entidad",
         "attribution_link":"entidad_url",
         "informacindelaentidad_sector":"entidad_sector",
         "informacindelaentidad_departamento":"entidad_departamento",
         "informacindelaentidad_orden":"entidad_orden",
         "informacindelaentidad_reaodependencia":"entidad_dependencia",
         "informacindelaentidad_municipio":"entidad_municipio",
         "informacindedatos_idioma":"idioma",
         "informacindedatos_coberturageogrfica":"cobertura",
         "publication_stage":"base_publica"
         }
    
    lista_columnas=list(dic_rename.keys())
    asset=asset[lista_columnas].rename(columns=dic_rename)
    
    # Cambiar las fechas
    asset["fecha_creacion"]=asset["fecha_creacion"].apply(lambda x:x[0:10])
    asset["fecha_actualizacion"]=asset["fecha_actualizacion"].apply(lambda x:x[0:10])
    
    # Pasar filas y columnas a float
    asset["filas"]=asset["filas"].astype(float)
    asset["columnas"]=asset["columnas"].astype(float)
    
    # Traducir las categorías de 'base_publica'
    asset["base_publica"]=asset["base_publica"].map({"published":"Si","unpublished":"No"})
    
    # Traducir las categorías de 
    asset["tipo"]=asset["tipo"].map({
            "dataset":"conjunto de datos",
            "federatet_href":"enlace externo",
            "href":"enlace externo",
            "map":"mapa",
            "chart":"grafico",
            "filter":"vista filtrada",
            "file":"archivo o documento",
            "visualization":"visualizacion",
            "story":"historia",
            "datalens":"lente de datos",
            "form":"formulario",
            "calendar":"calendario",
            "invalid_datatype":"tipo_invalido"})

    return(asset)


def mostrar_metadatos(api_id,token=None):
    """ Se conecta al API de Socrata y retorna los metadatos asociados a la base del api_id.

    :param api_id: (str) Identificación de la base de datos asociado con la API de Socrata.
    :param token: (str) *opcional* - token de usuario de la API Socrata.
    :return: serie de pandas con los metadatos.
    """
    
    dic_rename={
     "numero_api":"No. identificación API",
     "nombre":"Nombre",
     "descripcion":"Descripción",
     "dueno":"Dueño",
     "tipo":"Tipo de datos",
     "categoria":"Categoría",
     "terminos_clave":"Términos clave",
     "url":"URL",
     "fecha_creacion":"Fecha de creación",
     "fecha_actualizacion":"Fecha de última actualización",
     "actualizacion_frecuencia":"Frecuencia de actualización",
     "filas":"Número de filas",
     "columnas":"Número de columnas",
     "correo_contacto":"Correo electrónico del contacto",
     "licencia":"Licencia",
     "entidad":"Entidad creadora de la base de datos",
     "entidad_url":"URL de entidad",
     "entidad_sector":"Sector de la entidad",
     "entidad_departamento":"Departamento de la entidad",
     "entidad_orden":"Orden de la entidad",
     "entidad_dependencia":"Dependencia de la entidad",
     "entidad_municipio":"Municipio de la entidad",
     "idioma":"Idioma",
     "cobertura":"Cobertura", 
     "base_publica":"Base pública"
     }

    asset=asset_inventory_espanol(token=token).rename(columns=dic_rename)
    lista_nombres=dic_rename.values()
    asset=asset[lista_nombres]
    base_info=asset[asset["No. identificación API"]==api_id]
    base_info=pd.Series(base_info.iloc[0])
    base_info=base_info.replace("","CAMPO NO DILIGENCIADO").replace(np.nan,"CAMPO NO DILIGENCIADO")
    return(base_info)

def pagina_metadatos(api_id,token=None):
    """

    :param api_id: (str) Identificación de la base de datos asociado con la API de Socrata.
    :param token: (str) *opcional* - token de usuario de la API Socrata.
    :return: Abre en el navegador el link de datos abiertos asociado al api_id ingresado.
    """
    asset=asset_inventory(token=token)
    url=asset.loc[asset["uid"]==api_id,"url"].iloc[0]
    return webbrowser.open(url)
    

############ METADATOS
# COMPARAR LAS FILAS DE LOS METADATOS CON LA BASE DE DATOS MICRO
def comparar_tamano(api_id,token=None):
    """ Se conecta al API de Socrata y consulta el número de filas y columnas de los metadatos de la base de datos asociada con el *api_id* para construir una tabla, adicionalmente se agregan los datos actuales del número de filas y columnas de la base de datos.

    :param api_id: (str) Identificación de la base de datos asociado con la API de Socrata.
    :param token: (str) *opcional* - token de usuario de la API Socrata.
    :return: serie de pandas con el número de columnas y filas según los datos y metadatos.
    """
    
    client=Socrata("www.datos.gov.co",app_token=token)
    results=client.get(api_id,limit=1000000000)
    base_original=pd.DataFrame.from_records(results)
    
    tabla_conj=pd.read_csv(direccion_metatabla)
    tabla_conj=tabla_conj.loc[tabla_conj.loc[:,"tipo"]=="Conjunto de Datos"]

    meta_fila=tabla_conj.loc[tabla_conj.loc[:,"api_id"]==api_id].loc[:,"meta_filas"].iloc[0]
    micro_fila=base_original.shape[0]

    meta_col=tabla_conj.loc[tabla_conj.loc[:,"api_id"]==api_id].loc[:,"meta_columnas"].iloc[0]
    micro_col=base_original.shape[1]

    comparacion=pd.Series(
        data=[meta_fila,micro_fila,meta_col,micro_col],
        index=["filas_metadatos","filas_datos","columnas_metadatos","columnas_datos"]
        )
    
    return(comparacion)

#     
def filtrar_asset(columnas_valor,token=None):
    """ Permite filtrar la base de datos de *Asset Inventory* de acuerdo a diferentes términos de búsqueda. Como son fechas, textos y otros.

    :param columnas_valor: (dictinario) {'nombre de columna':'valor a buscar o rangos'}. Correponde al nombre de la columna a consultar y el valor a buscar.
    :param columnas_operacion: (str) {'contiene', 'igual', 'entre', 'menor', 'mayor', 'mayor igual', 'menor igual'} condición de comparación para filtrar la información.
    :return: dataframe *Asset Inventory* filtrado con los términos de búsqueda).
    """
    # base_filtro=tabla.copy()
    asset=asset_inventory_espanol(token)
    
    base_filtro=asset.copy()

    columnas=base_filtro.columns.tolist()
    
    lista_vocales=["a","e","i","o","u","a","e","i","o","u"]
    lista_tildes=["á","é","í","ó","ú","ä","ë","ï","ö","ü"]
    
    columnas_string=columnas_valor.copy()
    
    #### Revisar si término clave está en columnas de string
    for s in ["filas","columnas","fecha_creacion","fecha_actualizacion"]:
        if s in columnas_string:
            del columnas_string[s]
    
    for s_key in columnas_string:
        if s_key not in columnas:
            return(print("No existe una columna con el nombre '{0}'".format(s_key)))
        else:
            pass
        
        s_value=columnas_valor[s_key]
        
        # Pasar los nombres de los términos a buscar a minúscula y quitar tildes
        for i_s in range(len(s_value)):
            for i in range(len(lista_vocales)):
                s_value[i_s]=s_value[i_s].lower().replace(lista_tildes[i],lista_vocales[i])
               

        # Pasar todo el texto de la columna donde se busca a minúscula
        asset_columna=base_filtro.loc[:,s_key].astype(str).apply(lambda x:x.lower())
        # Cambiar todas las tildes en el texto
        for i in range(len(lista_vocales)):
            asset_columna=asset_columna.apply(lambda x:x.replace(lista_tildes[i],lista_vocales[i]))
        
        # Crear columna que diga si se encuentra o no el ´termino en esa observacion
        asset_columna=pd.DataFrame(asset_columna)
        # Iterar para cada término que se quiere buscar
        asset_columna["true"]=0
        asset_columna["true"]=asset_columna[s_key].apply(lambda x:1 if all(q in x for q in s_value) else 0)
        # Quedarse con las observaciones donde se encontró eltérmino
        asset_columna=asset_columna[asset_columna["true"]==1]
        # Filtrar la base original con el índice dela base con las observaciones encontradas
        base_filtro=base_filtro.loc[asset_columna.index]
    
    for s in ["filas","columnas"]:
        if s in columnas_valor:
            # Obtener los límiter inferior y superior deseados
            limite_inferior=columnas_valor[s][0]
            limite_superior=columnas_valor[s][1]
            # Si los limites son numéricos, por lo tanto en un rango, escoger rango
            if type(limite_inferior)==int and type(limite_superior)==int:
                base_filtro=base_filtro.loc[(base_filtro[s]<=limite_superior)&(base_filtro[s]>=limite_inferior),:]
            
            elif type(limite_inferior)==int and limite_superior=="+":
                base_filtro=base_filtro.loc[base_filtro[s]>=limite_inferior,:]
            
            elif type(limite_inferior)==int and limite_superior=="-":
                base_filtro=base_filtro.loc[base_filtro[s]<=limite_inferior,:]             
            
            else:
                return("Los parámetros de 'fila' y/o 'columna' tienen valores incorrectos")
            
                   
    for s in ["fecha_creacion","fecha_actualizacion"]:
        if s in columnas_valor:
            fecha_inicio=datetime.datetime.strptime(columnas_valor[s][0],"%Y-%m-%d")

            # Crear columna con fecha en formato fecha
            base_filtro.loc[:,"{0}_fecha".format(s)]=base_filtro.loc[:,s].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d") if x!="nan" else np.nan)

            if columnas_valor[s][1]=="+":
                base_filtro=base_filtro.loc[base_filtro.loc[:,"{0}_fecha".format(s)]>=fecha_inicio,:]
       
            elif columnas_valor[s][1]=="-":
                base_filtro=base_filtro.loc[base_filtro.loc[:,"{0}_fecha".format(s)]<=fecha_inicio,:]
            
            else:
                fecha_fin=datetime.datetime.strptime(columnas_valor[s][1],"%Y-%m-%d")
                base_filtro=base_filtro.loc[(base_filtro.loc[:,"{0}_fecha".format(s)]>=fecha_inicio) & (base_filtro.loc[:,"{0}_fecha".format(s)]<=fecha_fin),:]
            
            del base_filtro["{0}_fecha".format(s)]
                            
    return(base_filtro)


#def infos_cols_tabla(base):
#    tipo_columna=col_type(base)
#    valores_unicos=unique_col(base)
#    valores_unicos_missing=unique_col_missing(base)
#    porcentaje_missing=missing_perc(base)
#    
#    columnas=["Columna","Tipo de la columna","No. únicos","No. únicos con missing","% valores faltantes"]
#    
#    tabla_grande=pd.concat([tipo_columna,valores_unicos,valores_unicos_missing,porcentaje_missing],axis=1).reset_index()
#    tabla_grande.columns=columnas
#    return(tabla_grande)
    

























