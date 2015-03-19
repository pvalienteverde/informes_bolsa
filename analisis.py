# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-


import pandas.io.data as web
import pandas as pd
import datetime
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.finance import  candlestick_ohlc
from matplotlib.dates import DateFormatter, WeekdayLocator,\
     DayLocator, MONDAY
import numpy as np
import ticker as ticker     
from matplotlib.ticker import FormatStrFormatter 
from matplotlib.backends.backend_pdf import PdfPages
import logger as lg
import EnviaEmail
import time
import DescargaDatosBolsa
import multiprocessing

import multiprocessing
import threading

import logging
from multiprocessing import Pool
import argparse


def AnadirPDF(objeto_bolsa,fig,pp):
    
        df_valores_ticker=objeto_bolsa.datos
        nombre_ticker=objeto_bolsa.ticker
        try:
            
            subplot_ax=fig.add_subplot(111)
            subplot_ax.grid(zorder=0)
                
            df_valores_ticker_ordenado=df_valores_ticker[['FechaNum','Open','High','Low','Close','Volume']]
            tuple_valores=[tuple(x) for x in df_valores_ticker_ordenado.to_records(index=False)]
        
            subplot_ax.fill_between(df_valores_ticker.index, df_valores_ticker['BollingLow'], df_valores_ticker['BollingHigh'], color='#5858FA', alpha=0.2)
            
            subplot_ax.plot(df_valores_ticker.index, df_valores_ticker['SMA6'], 'k',linewidth=0.3,label='SMA6')
            subplot_ax.plot(df_valores_ticker.index, df_valores_ticker['SMA70'], 'k',linewidth=1,label='SMA70')
            subplot_ax.plot(df_valores_ticker.index, df_valores_ticker['SMA200'], 'k',linewidth=2,label='SMA200')
        
            candlestick_ohlc(subplot_ax, tuple_valores, width=0.4,colorup='g')    
            
            #subplot_ax.xaxis_date()
            subplot_ax.autoscale_view()
            subplot_ax.legend(loc='upper left',fontsize='xx-small')
            
            subida_ultimpo_dia=df_valores_ticker.Close[-1]-df_valores_ticker.Close[-2]
            color_text_titulo='red' if subida_ultimpo_dia>0 else 'green'
            subplot_ax.set_title(nombre_ticker+", {0} ({1:.2f}%)".format( subida_ultimpo_dia,subida_ultimpo_dia/df_valores_ticker.Close[-2]*100),color=color_text_titulo)
            # se especifica donde colocar lo que queremos
            subplot_ax.set_xticks(df_valores_ticker.index.values)   
            valores_y=[df_valores_ticker.Low.min(),df_valores_ticker.Close[-1],df_valores_ticker.Open[-1],df_valores_ticker.High.max()]
            subplot_ax.set_yticks(valores_y)
        
            subplot_ax.tick_params(direction='out', length=6, width=2, colors='r',axis='both')
            xdays=np.array([])
            for fecha in df_valores_ticker.index.values:
                f=pd.to_datetime(fecha)
                if f.dayofweek==0:
                    xdays=np.append(xdays,f.date())
                else:
                    xdays=np.append(xdays,"")
                    
          
            subplot_ax.set_xticklabels(xdays, rotation=45, horizontalalignment='right',fontproperties=style_font)
            i=0
            for tic in subplot_ax.xaxis.get_major_ticks():
                if (i%5):
                    tic.set_visible(False)
                
                i+=1
               
        
        
            subplot_ax.set_yticklabels(valores_y,alpha=0.9,color='blueviolet',fontproperties=style_font)
            subplot_ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            [line.set_zorder(3) for line in subplot_ax.lines]
            
            if (df_valores_ticker['SMA6'].iloc[-1]>df_valores_ticker['SMA70'].iloc[-1]>df_valores_ticker['SMA200'].iloc[-1]):
                subplot_ax.set_axis_bgcolor("#d3eede")
            else:
                subplot_ax.set_axis_bgcolor("#ffdede")
            
            ax2 = subplot_ax.twinx()
            
            ax2.bar(subplot_ax.get_xticks(),df_valores_ticker.Volume.where(df_valores_ticker.DiffCloseOpen>0,0)
        ,alpha=0.5,color='green',align='center')
            ax2.bar(subplot_ax.get_xticks(),df_valores_ticker.Volume.where(df_valores_ticker.DiffCloseOpen<=0,0)
        ,alpha=0.5,color='red',align='center')
        
            # Valores para el Volumen
            eje_y_volumen=[df_valores_ticker.Volume[-1]]
            ax2.set_yticks(eje_y_volumen)
            ax2.set_yticklabels(eje_y_volumen,fontproperties=style_font)
        
            ax2.set_ylim((0, df_valores_ticker['Volume'].max()*4))
            ax2.yaxis.set_major_formatter(FormatStrFormatter('%d'))
            
        
            #plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')    
            
            pp.savefig(dpi=200,)
            
            fig.delaxes(subplot_ax)
            fig.delaxes(ax2)    
        except Exception as e:    
            raise RuntimeError("Error desconodio:"+e.message)

def SacaDatosWeb(fecha_inicio,fecha_fin,array_de_datos=None):
    if array_de_datos is None:
        array_de_datos=[]
        
    hilos=[]    
    for nombre_ticker in tickers_a_representar:
        hilo = threading.Thread(target=DescargaDatosBolsa.CalculoPandasTicker,
                                args=(nombre_ticker,array_de_datos,fecha_inicio,fecha_fin),
                                name=nombre_ticker)
        hilos.append(hilo)
        
    [hilo.start() for hilo in hilos]    
    [hilo.join() for hilo in hilos]

    return array_de_datos
    
def CreaGraficasTickers(array_de_datos,ruta_pdf='analisis_diario_hilos.pdf'):
    
    #http://matplotlib.org/users/customizing.html
    plt.rc('axes', grid=True)
    plt.rc('grid', linestyle='-', linewidth=0.5,color='#acafb2')  

    fig=plt.figure(figsize=(13,5))

    matplotlib.font_manager.FontProperties(size=5)

    pp = PdfPages(ruta_pdf)  
    plt.ioff()
    
    logging.info('Creando las hojas...')
    for objeto_bolsa in np.sort(array_de_datos):
        try:        
            AnadirPDF(objeto_bolsa,fig,pp)
        except Exception as e:
            print "Pasamos a otro, el error ha sido: "+e.message
        
    pp.close()

    
if __name__ == "__main__":
    
    logging.basicConfig(filename='analisis.log', filemode='a', level=logging.DEBUG,format='%(asctime)s %(threadName)-10s  %(levelname)-8s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    logging.info('Empieza proceso de analisis bursatil, fecha: {}'.format(datetime.datetime.now()))
    
    fecha_inicio = datetime.datetime(2012, 1, 10)
    fecha_fin = datetime.datetime.now()
    
    tickers=np.array(['REE.MC','GAM.MC','ITX.MC','IBE.MC'])#,'GAM.MC','ITX.MC','IBE.MC'
    tickers_mc_disponibles=ticker.ticker('mc').getValores()
    tickers_a_representar=np.sort(tickers_mc_disponibles)#np.intersect1d(tickers,tickers_mc_disponibles
    
    
    array_de_datos=SacaDatosWeb(fecha_inicio,fecha_fin)

    CreaGraficasTickers(array_de_datos)

    
    
    
    logging.info('Terminado')
