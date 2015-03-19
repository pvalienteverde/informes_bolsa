# -*- coding: utf-8 -*-
"""
Ticker
======

Aporta:
    1. Tickers de los valores de diferentes bolsas mundiales a traves de yahoo

@author: pedro
"""

import numpy as np
import urllib
from BeautifulSoup import BeautifulSoup
#http://mundogeek.net/archivos/2008/03/05/python-orientacion-a-objetos/
#http://www.maestrosdelweb.com/editorial/guia-python-cadenas-de-texto/

class ticker(object):
    """
    ticker
    ======
    
    APorta los tickers de los valores de diferentes bolsas mundiales a traves de yahoo
    """
    def __init__(self,tipo_mercado):
        
        if tipo_mercado=='mc' :  
            self.__valores=self.getValoresMC()
        else:
            raise Exception("No está implementado para el mercado {}".format(tipo_mercado))
    def getValores(self):
        """
        Devuelve el ticker de los valores de la bolsa elegida
        """
        return(np.array(self.__valores.keys()))
        
    @staticmethod
    def getValoresMC():
        """
        Metodo estatico que devuelve los valores del mercado continuo español a traves de yahoo
        """
        web = urllib.urlopen('https://es.finance.yahoo.com/actives?e=mc')
        s = web.read()        
        soup = BeautifulSoup(s)
        
        indices_de_tickers={}
        tickers=soup('td', {'class': 'first'})
        descripcion=soup('td', {'class': 'second name'})
        for indice in np.arange(0,len(tickers)-1):
            ticker=str(tickers[indice]('a')[0].contents[0])
            ticker_descripcion=str(descripcion[indice].contents[0])
            indices_de_tickers[ticker]=ticker_descripcion
            
        return indices_de_tickers
    
    def __str__(self):
        texto="Valores para el mercado continuo español: \n"
        for llave in self.__valores.keys():
            texto=texto+"\n\tTicker: "+llave+".MC --> "+self.__valores[llave]
        return(texto)# -*- coding: utf-8 -*-
        
if __name__ == "__main__": 
    ticker_mc = ticker('mc')  

