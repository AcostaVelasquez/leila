# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:33:57 2019

@author: pabmontenegro
"""
import pandas as pd
import numpy as np
# from sodapy import Socrata


#def sodapy_data(api_id,token=None):
#
#    client = Socrata("www.datos.gov.co",
#                     app_token=token)
#
#    results = client.get(api_id,limit=1000000000)
#    base_original = pd.DataFrame.from_records(results)
#    return(base_original)


## Tipos de las columnas
def col_type(base,detail="low"):
    lista=[[],[]]
    
    if detail=="low":
        
        for s in base.columns:
            tip=str(type(base[s].value_counts(dropna=True).index[0]))
            lista[0].append(s)
        
            if "int" in tip or "float" in tip:
                lista[1].append("Numérico")
            elif "str" in tip:
                lista[1].append("Texto")
            elif "bool" in tip:
                lista[1].append("Boolean")
            # elif ""
            else:
                lista[1].append("Otro")
             
    elif detail=="high":
        
        for s in base.columns:
            tip=str(type(base[s].value_counts(dropna=True).index[0])).replace("<class ","").replace(">","").replace("'","'")
            lista[0].append(s)
            lista[1].append(tip)

    else:
        return("Se ha ingresado en la opción 'detail' un valor distinto a 'low' o 'high'")
    
    tips=pd.DataFrame(lista).T.set_index(keys=0,drop=True).iloc[:,0]
            
    return(tips)

########## valores únicos en cada columna
# sin missing values
def unique_col(base,missing=False):
    if missing==False:
        unicos_columnas=base.apply(lambda x:len(x.value_counts()),axis=0)
    elif missing==True:
        unicos_columnas=base.apply(lambda x:len(x.value_counts(dropna=False)),axis=0)
    else:
        return("La opción 'missing' tiene un valor distinto a False o True")
    return(unicos_columnas)
    
########## COMPLETITUD. Missing 
def missing(base,perc=True):
    if perc==True:
        missing_columnas=pd.isnull(base).sum()/len(base)
    elif perc==False:
        missing_columnas=pd.isnull(base).sum()
    else:
        return("La opción 'perc' tiene un valor distinto a True o False")
    return(missing_columnas)

        
########## Unicidad. Porcentaje y número de filas y columnas no únicas
def nounique(base,col=True,perc=True):
    if col==True and perc==True:
        no_unic_columnas=base.T.duplicated(keep=False)
        cols=no_unic_columnas[no_unic_columnas==True].shape[0]/base.shape[1]
        
    elif col==True and perc==False:
        no_unic_columnas=base.T.duplicated(keep=False)
        cols=no_unic_columnas[no_unic_columnas==True].shape[0]
        
    elif col==False and perc==True:
        no_unic_filas=base.duplicated(keep=False)
        cols=no_unic_filas[no_unic_filas==True].shape[0]/base.shape[0]   
        
    elif col==False and perc==False:
        no_unic_filas=base.duplicated(keep=False)
        cols=no_unic_filas[no_unic_filas==True].shape[0]
    else:
        return("Las opciones 'col' y 'perc' tienen valores distintos a True y False")
    
    return(cols)
    
########## MATCHING DE COLUMNAS Y FILAS NO ÚNICAS
def duplic(base,col=True):
        
    # if col!=True or col!=False:
    #     return("El parámetro 'col' tiene valores distintos a True o False")
    # else:
    #     pass
    
    if col==True:
        dupli=base.T.duplicated(keep=False)
    elif col==False:
        dupli=base.duplicated(keep=False)
    else:
        print("El parámetro 'col' tiene valores distintos a True o False")
    
    dupli=dupli[dupli==True]
    if dupli.sum()==0:
        return("No hay columnas duplicadas")
    lista_duplicados=[]
    for s in dupli.index:
        for ss in dupli.index:
            if col==True:
                if base[s].equals(base[ss]) and s!=ss:
                    lista_duplicados.append([s,ss])
            elif col==False:
                if base.iloc[s].equals(base.iloc[ss]) and s!=ss:
                    lista_duplicados.append([s,ss])
            else:
                pass

    if col==False:
        lista_duplicados=sorted(lista_duplicados)
    else:
        pass
                
    dic={}
    for s in dupli.index:
        dic[s]=[]
    for s in dupli.index:
        for i in range(len(lista_duplicados)):
            if s in lista_duplicados[i]:
                dic[s].append(lista_duplicados[i])
    for s in dic:
        lista=[q for l in dic[s] for q in l]
        dic[s]=list(set(lista))
    
    if col==True:            
        lista_listas=[q for q in dic.values()]
    else:
        lista_listas=[sorted(q) for q in dic.values()]

    for i in range(len(lista_listas)): 
        for ii in range(len(lista_listas[i])):
            lista_listas[i][ii]=str(lista_listas[i][ii])
    

    df=pd.DataFrame(lista_listas).drop_duplicates().reset_index(drop=True)
    return(df)

########## CONSISTENCIA. Porcentaje de outliers
def outliers(base,outliers="both",perc=True):
    col_tipos=col_type(base,detail="low")
    col_num=col_tipos[col_tipos=="Numérico"].index
    base_num=base[col_num]
    
    if base_num.shape[1]==0:
        print("La base de datos no contiene columnas numéricas")
    else:
        pass
    
    percentiles_25=base_num.apply(lambda x:np.nanpercentile(x,25),axis=0)
    percentiles_75=base_num.apply(lambda x:np.nanpercentile(x,75),axis=0)
    
    iqr=percentiles_75-percentiles_25
    iqr_upper=percentiles_75+iqr*1.5
    iqr_lower=percentiles_25-iqr*1.5

    dic_outliers={}
    
    if outliers=="both":
        for i in range(0,len(iqr)):
            dic_outliers[base_num.columns[i]]=(base_num.iloc[:,i]>iqr_upper[i])|(base_num.iloc[:,i]<iqr_lower[i])
    elif outliers=="upper":
        for i in range(0,len(iqr)):
            dic_outliers[base_num.columns[i]]=(base_num.iloc[:,i]>iqr_upper[i])
    elif outliers=="lower":
        for i in range(0,len(iqr)):
            dic_outliers[base_num.columns[i]]=(base_num.iloc[:,i]<iqr_lower[i])
    else:
        return("La opción outliers tiene valores distintos a 'both', 'upper' o 'lower")
    
    base_outliers=pd.DataFrame(dic_outliers)
    
    if perc==True:
        base_outliers_porc=base_outliers.sum()/base_outliers.shape[0]
    elif perc==False:
        base_outliers_porc=base_outliers.sum()
    else:
        return("La opción 'perc' tiene valores distintos a True o False")

    return(base_outliers_porc)        
    
############## describe de columnas
def descriptive_stats(base,float_transform=False):
    
    if float_transform==True:
        base=base.apply(lambda x:x.astype(float,errors="ignore"),axis=0)
    elif float_transform==False:
        pass
    else:
        return("La opción 'float_transform' tiene valores distintos a True o False")

    col_tipos=col_type(base,detail="low")
    col_num=col_tipos[(col_tipos=="Numérico")|(col_tipos=="Float")].index
    base_num=base[col_num] 
    
    if len(col_num)==0:
        return("La base de datos no tiene columnas numéricas")
    else:
        pass
    
    base_descripcion=base.describe().T
    base_descripcion["missing"]=pd.isnull(base_num).sum()/len(base_num)
    base_descripcion["outliers"]=outliers(base)
    
    return(base_descripcion)

###############
def var_high_low(base,percent_low=5,percent_high=95):
    cols_tipos=base.dtypes
    lista_nums=[]
    for i in range(len(cols_tipos)):
        if "int" in str(cols_tipos[i]) or "float" in str(cols_tipos[i]):
            lista_nums.append(cols_tipos.index[i])
    base_num=base[lista_nums]
    for c in base_num.columns:
        if base_num[c].isnull().sum()==base_num.shape[0]:
            del base_num[c]
        else:
            pass
        
    percentil_bajo=base_num.apply(lambda x:np.percentile(x.dropna(),5),axis=0)
    percentil_alto=base_num.apply(lambda x:np.percentile(x.dropna(),95),axis=0)
    
    percentiles=pd.concat([percentil_bajo,percentil_alto],axis=1)
    percentiles_true=(percentiles.iloc[:,0]==percentiles.iloc[:,1])
    percentiles_true=percentiles_true[percentiles_true==True]
    
    if len(percentiles_true)==0:
        return("No hay ninguna columna numérica que tenga el percentil {0} y el percentil {1} igual".format(percent_low,percent_high))
    else:
        return percentiles_true.index
    
############### tabla de valores únicos para cada variable de texto
# Falta definir qué es una variable categórica
def unique_text(base,limit=0.5,nums=False,variables=None):
    # Filtrar la base por las variables escogidas en la opción 'variables'
    if variables is not None:
        base=base[variables]
    else:
        pass
    
    # Calcular qué variables tipo object tienen valores únicos menores al 50% (o valor de 'limit') del total de filas de la base original
    limit=0.5
    col_object=base.dtypes
    col_object=col_object[col_object=="object"]
    lista_object_unicos=[]
    for s in col_object.index:
        unico=len(pd.unique(base[s]))
        if unico<base.shape[0]*limit:
            lista_object_unicos.append(s)
            
    # Si la opción 'nums' es True, incluir las variables numéricas con repeticiones menores al 50% (o el límite) del total de filas   
    if nums==True:
        cols_types=base.dtypes
        col_nums=[]
        for i in range(len(cols_types)):
            if "int" in str(cols_types[i]) or "float" in str(cols_types[i]):
                col_nums.append(cols_types.index[i])
        for s in col_nums:
            unico=len(pd.unique(base[s]))
            if unico<base.shape[0]*limit:
                lista_object_unicos.append(s)
    elif nums==False:
        pass
    else:
        return("La opción 'nums' tiene un valor distinto a True o False")
    
    # Crear el dataframe con la información
    lista_counts=[]
    for s in lista_object_unicos:
        counts=base[s].value_counts()
        if type(counts.index[0])==dict:
            continue
        lista=counts[0:10]
        resto=counts[10:len(counts)].sum()
        miss=pd.isnull(base[s]).sum()

        lista["Demás categorías"]=resto
        lista["Datos faltantes"]=miss
        # lista["Total de categorías (con NA)"]=len(pd.unique(base[s]))

        lista=lista.to_frame()
        lista["Columna"]=s
        lista["Porcentaje del total de filas"]=lista[s]/len(base)
            
        resto=lista.iloc[:,0].loc["Demás categorías"]
        
        if resto==0:
            lista=lista.drop("Demás categorías",axis=0)


        lista=lista.reset_index()
        
        
        s=lista.columns.tolist()[1]
        colis=["Columna","index",s,"Porcentaje del total de filas"]
        lista=lista[colis]
        lista_cols=lista.columns.tolist()
        lista=lista.rename(columns={"index":"Valor",lista_cols[2]:"Frecuencia"})
        lista_counts.append(lista)
    df_counts=pd.concat(lista_counts,axis=0)
    return(df_counts)
    
########## Tamaño de la base de datos en la memoria
def memoria(base,col=False):
    if col==False:
        memoria=base.memory_usage(index=True).sum()
    elif col==True:   
        memoria=base.memory_usage(index=True)
    else:
        return("La opción 'col' tiene un valor distinto a True o False")
    return memoria/1024/1024
    
########## tabla de resumen pequeña
def data_summary(base):
    datos=["" for q in range(11)]
    # nombres=["Número de filas","Número de columnas","Columnas numéricas","Columnas de texto","Columnas boolean","Columnas de fecha","Otro tipo de columnas","Número de filas no únicas","Número de columnas no únicas","Columnas con más de la mitad de datos faltantes","Columnas con más del 10% de datos como extremos","Tamaño de la base en megabytes (redondeado)"]
    nombres=["Número de filas","Número de columnas","Columnas numéricas","Columnas de texto","Columnas boolean","Columnas de fecha","Otro tipo de columnas","Número de filas no únicas","Columnas con más de la mitad de datos faltantes","Columnas con más del 10% de datos como extremos","Tamaño de la base en megabytes (redondeado)"]
   
    col_tipos=col_type(base,detail="low")
    col_texto=col_tipos[col_tipos=="Texto"]
    col_num=col_tipos[col_tipos=="Numérico"]
    col_bool=col_tipos[col_tipos=="Boolean"]
    col_date=col_tipos[col_tipos=="Fecha"]
    col_other=col_tipos[col_tipos=="Otro"]
   
    col_missing=missing(base,perc=True)
    col_missing_50=col_missing[col_missing>0.5]

    col_porc=outliers(base,outliers="both",perc=True)
    col_porc_10=col_porc[col_porc>0.1]
    
    memoria_tot=memoria(base)

    datos[0]=base.shape[0]
    datos[1]=base.shape[1]
    datos[2]=len(col_num)
    datos[3]=len(col_texto)
    datos[4]=len(col_bool)
    datos[5]=len(col_date)
    datos[6]=len(col_other)
    datos[7]=nounique(base,col=False,perc=False)
    # datos[8]=nounique(base,col=True,perc=False)
    datos[8]=len(col_missing_50)
    datos[9]=len(col_porc_10)
    datos[10]=memoria_tot

    tabla_resumen=pd.Series(data=datos,index=nombres).astype(int)
    return(tabla_resumen)
 


#from distutils.sysconfig import get_python_lib
#print(get_python_lib())
#



np.nan==np.nan





