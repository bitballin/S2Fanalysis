#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 08:35:30 2020

"""

import pandas as pd
import matplotlib.pyplot as plt
import imageio
import math 
import numpy as np
import time
from bitcoin_data import bitcoinData
from sklearn.metrics import r2_score
from datetime import date, timedelta
from matplotlib.ticker import ScalarFormatter



def S2F_function(bH):
    stock = 50*(210000*(1-math.pow(0.5, math.floor(bH/210000)))/(1-0.5)+math.pow(0.5, math.floor(bH/210000))*math.fmod(bH,210000))
    flow = 50*0.5**(math.floor(bH/210000))
    S2F = stock/flow
    return S2F

def subsidy_epoch_function(bH):
    return math.floor(bH/210000)+1
    

def S2Fanalysis(dataset = bitcoinData, dates = bitcoinData['Date'], epoch=range(1,33), blockheight = range(1,210000*33)):
    dataset['S2F'] = dataset['Blockheight'].apply(S2F_function)
    dataset['Subsidy Epoch'] = dataset['Blockheight'].apply(subsidy_epoch_function)
    dataset['logS2F'] = dataset['S2F'].apply(math.log)
    dataset['logPrice'] = dataset['PriceUSD'].apply(math.log)
    
    outputdf = dataset.copy()
    outputdf = outputdf[outputdf['Subsidy Epoch'].isin(epoch)]
    outputdf = outputdf[outputdf['Date'].isin(dates)]
    outputdf = outputdf[outputdf['Blockheight'].isin(blockheight)]
    
    
    linearFitS2FPrice = np.polyfit(outputdf['logS2F'], outputdf['logPrice'], 1)
    linearFitS2FPriceObject = np.poly1d(linearFitS2FPrice);
    
    r2 = r2_score(outputdf['logPrice'], linearFitS2FPriceObject(outputdf['logS2F']))    
    
    price_model=linearFitS2FPrice[0]*dataset['logS2F']+linearFitS2FPrice[1]
    price_model=price_model.apply(math.exp)
    return price_model, outputdf, linearFitS2FPrice,  r2


start_date = date(2011, 1, 1)
end_date = date(2021, 10, 1)
test_date=start_date
delta = timedelta(days=30)
images = []
fig = plt.figure()
ax = fig.add_subplot(111)
blockheight_forcast = 4*210000 - 1
s2f_forcast = S2F_function(blockheight_forcast)
while test_date <= end_date:
    pricemodel, outputdf, fit, r = S2Fanalysis(dates = pd.date_range(start=bitcoinData['Date'].min(), end=test_date))
    price_forcast=fit[0]*math.log(s2f_forcast)+fit[1]
    price_forcast=math.exp(price_forcast)
    plt.plot(bitcoinData['Date'],bitcoinData['PriceUSD'],'b');
    plt.plot(outputdf['Date'],outputdf['PriceUSD'],'r');
    c = plt.plot(bitcoinData['Date'],pricemodel,'k');
    plt.axis([start_date,end_date,bitcoinData['PriceUSD'].min(),bitcoinData['PriceUSD'].max()])
    plt.yscale('log')
    ax.set_title('S2F model using data from ' + bitcoinData['Date'].min().strftime("%d-%b-%Y") +' to '+ test_date.strftime("%d-%b-%Y") + '\n 2024 predicted price: $' + str(round(price_forcast,2)), fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    for handle in c: handle.remove()
    
    time.sleep(0.03) # seconds
    test_date += delta
    images.append(image)
imageio.mimsave('file.gif',images,fps=3)    


