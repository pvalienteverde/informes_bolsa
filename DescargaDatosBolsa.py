# -*- coding: utf-8 -*-

import pandas.io.data as web
import pandas as pd
import datetime
import numpy as np
import logging
import matplotlib
import threading


_HISTORICAL_YAHOO_URL = 'http://ichart.finance.yahoo.com/table.csv?'

# Colores: http://stackoverflow.com/questions/22408237/named-colors-in-matplotlib
#'http://chartapi.finance.yahoo.com/instrument/1.0/REE.MC/chartdata;type=quote;range=1d/csv/'

class DatoBolsa(object):
    def __init__(self, df_datos, ticker,**kwargs):
        self.datos=df_datos
        self.ticker=ticker
        
    def __cmp__(self, other):
        return self.ticker>other.ticker
        
    def __str__(self):
        return "{}, numero de datos: {}".format(self.ticker,len(self.datos))
        
    def __repr__(self):
        return "{}".format(self.ticker)
        

def HistoricoDiaActual(ticker):
 
    url="http://chartapi.finance.yahoo.com/instrument/1.0/"+ticker+"/chartdata;type=quote;range=1d/csv/"
    #print url
    logging.info('Historico del dia en curso: {}'.format(url))
    datos=pd.DataFrame()  
    intentos=0     
    while (intentos<5 and datos.empty):
        datos=pd.read_csv(url,header=None,names=['Timestamp','close','high','low','open','volume'])
        intentos=intentos+1
        
    if (datos.empty):
        logging.exception(RuntimeError("Datos del dia en curso vacio, no se ha podido recuperar"))
    
    
    datos=datos.iloc[17:,:]
    datos=datos.astype(float)    
    datos.Timestamp=datos.Timestamp.apply(lambda x: datetime.datetime.utcfromtimestamp(x))    
    return datos



def HistoricoYahoo(ticker, start, end):

    url = (_HISTORICAL_YAHOO_URL + 's=%s' % ticker +
           '&a=%s' % (start.month - 1) +
           '&b=%s' % start.day +
           '&c=%s' % start.year +
           '&d=%s' % (end.month - 1) +
           '&e=%s' % end.day +
           '&f=%s' % end.year +
           '&g=d' +
           '&ignore=.csv')
    logging.info('Historico yahoo: {}'.format(url))
           
    intentos=0
    historico=pd.DataFrame()       
    while (intentos<5 and historico.empty):
        historico=pd.read_csv(url,index_col=0,parse_dates=['Date'])
        intentos=intentos+1
        
    if (historico.empty):
        logging.exception(RuntimeError("Historico yahoo vacio, no se ha podido recuperar"))
    
    # Vamos a ajustar el historico
    ratio_de_ajuste = historico['Adj Close'] / historico['Close']
    historico=historico.mul(ratio_de_ajuste,axis=0)
    historico.sort_index(ascending=True,inplace=True)
    return historico

def HistoricoCompleto(ticker, start, end):
    
    historico=HistoricoYahoo(ticker, start, end)
    
    dia_actual=datetime.datetime.now()
    dia_de_semana=dia_actual.weekday()
    dias_descarga=np.array([0,1,2,3,4])
    if np.size(np.where(dias_descarga==dia_de_semana)[0]) == 1:
        valores_dia_actual=HistoricoDiaActual(ticker)
        close_=valores_dia_actual.close.iloc[-1]
        open_=valores_dia_actual.open.iloc[0]
        high=valores_dia_actual.high.max()
        low=valores_dia_actual.low.min()
        volume=valores_dia_actual.volume.sum()
        dia=dia_actual.date()
        
        aux=pd.DataFrame(index=[dia],data={'Close':close_,'Open':open_,'High':high,'Volume':volume,'Low':low,'Adj Close':close_})

        historico=historico.append(aux)

    return historico

    
    

def CalculoPandasTicker(ticker,array_de_datos,fecha_ini,fecha_fin):
    logging.info("Lanzado {}".format(threading.currentThread().getName()))
    df_valores=[]
    
    try:    
        df_valores=HistoricoCompleto(ticker, fecha_ini, fecha_fin)
            
        df_valores['FechaNum']=matplotlib.dates.date2num(pd.DatetimeIndex(df_valores.index).date)   
        df_valores['SMA6'] = pd.rolling_mean(df_valores['Close'], 6)
        df_valores['SMA70'] = pd.rolling_mean(df_valores['Close'], 70)
        df_valores['SMA200'] = pd.rolling_mean(df_valores['Close'], 200)
        df_valores['DiffCloseOpen']=df_valores.Close-df_valores.Open
        ma = pd.rolling_mean(df_valores['Close'], 20)
        mstd = pd.rolling_std(df_valores['Close'], 20)    
        df_valores['BollingHigh'] =  ma+2*mstd
        df_valores['BollingLow'] =  ma-2*mstd
        
        df_valores=df_valores.iloc[-20*6:]
    except:
        logging.exception(RuntimeError("Error desconocido "+ticker+", Pasamos a otro"))
        
    aux_bolsa=DatoBolsa(df_valores,ticker)
    array_de_datos.append(aux_bolsa)
    logging.info("Detenido {}".format(threading.currentThread().getName()))

def CalculoPandasTickerSinHilos(ticker,fecha_ini,fecha_fin):
   
        df_valores=HistoricoCompleto(ticker, fecha_ini, fecha_fin)
            
        df_valores['FechaNum']=matplotlib.dates.date2num(pd.DatetimeIndex(df_valores.index).date)   
        df_valores['SMA6'] = pd.rolling_mean(df_valores['Close'], 6)
        df_valores['SMA70'] = pd.rolling_mean(df_valores['Close'], 70)
        df_valores['SMA200'] = pd.rolling_mean(df_valores['Close'], 200)
        df_valores['DiffCloseOpen']=df_valores.Close-df_valores.Open
        ma = pd.rolling_mean(df_valores['Close'], 20)
        mstd = pd.rolling_std(df_valores['Close'], 20)    
        df_valores['BollingHigh'] =  ma+2*mstd
        df_valores['BollingLow'] =  ma-2*mstd
        
        df_valores=df_valores.iloc[-20*6:]

        return df_valores