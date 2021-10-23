#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Script to read bitcoin data from coinmetrics website

Created on Mon Jun  8 07:19:57 2020
"""


import pandas as pd
from datetime import datetime
import io
import requests
import numpy as np
import math


#grab old data
bitcoinDataOld = pd.read_csv("bitcoindataset.csv")
df = pd.read_csv("OldBitcoinBHData.csv") 
df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'].dt.date
bitcoinDataOldBH = df.drop_duplicates(subset='date', keep="first")
bitcoinDataOldBH['blockheight']= bitcoinDataOldBH['blockheight'].apply(lambda x: x.replace(',', '')).astype(int)

#get new Data
url = "https://coinmetrics.io/newdata/btc.csv"
s=requests.get(url).content
bitcoinDataNew=pd.read_csv(io.StringIO(s.decode('utf-8')))
bitcoinDataNew['Blockheight'] = bitcoinDataNew.BlkCnt.cumsum()
bitcoinDataNew.dropna(inplace = True)
bitcoinDataNew.reset_index(drop = True, inplace = True)

#create new dataframe with just Date, Price, and Blockheight



bitcoinData = pd.DataFrame()
bitcoinData['Date'] = pd.concat([bitcoinDataOld.timestamp, bitcoinDataNew.date])
bitcoinData['PriceUSD'] = pd.concat([bitcoinDataOld.close, bitcoinDataNew.PriceUSD])
bitcoinData['Blockheight'] = pd.concat([bitcoinDataOld.blockheight, bitcoinDataNew.Blockheight])
bitcoinData = bitcoinData.sort_values(by=['Date'])
bitcoinData = bitcoinData.drop_duplicates(subset='Date', keep="first")
bitcoinData.Date = pd.to_datetime(bitcoinData.Date)
bitcoinData.reset_index(drop = True, inplace = True)


bitcoin_data_just_date_bh = pd.DataFrame()
temp = bitcoinDataOldBH.copy()
tempd = temp['date'].append(bitcoinData['Date'].dt.date)
tempbh = temp['blockheight'].append(bitcoinData['Blockheight'])
bitcoin_data_just_date_bh['date'] = tempd
bitcoin_data_just_date_bh['blockheight'] = tempbh
bitcoin_data_just_date_bh= bitcoin_data_just_date_bh.drop_duplicates(subset='date', keep="first")