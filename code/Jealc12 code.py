# -*- coding: utf-8 -*-
"""
Created on Thu Feb 19 19:58:59 2026

@author: sliu154
"""

import signal 
import requests 
from time import sleep 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

### Thsiv ersion changes spread and volume according to position
###### THIS ONE IS THE BEST VERSION YET
############### V3
SPREAD_sell = 0.02
SPREAD_buy = 0.02
SPREAD_trend_sell = 0.02
SPREAD_trend_buy = 0.02

BUY_VOLUME2 = 1500 
SELL_VOLUME2 = 1500
BUY_VOLUME = 1500 
SELL_VOLUME = 1500

tickers_since_last=5

level3=12000
level2=level3-1
level1=level3/2

################################
class ApiException(Exception): 
   pass 
def signal_handler(signum, frame): 
   global shutdown 
   signal.signal(signal.SIGINT, signal.SIG_DFL) 
   shutdown = True 
API_KEY = {'X-API-Key': 'PEDDP321'} 
shutdown = False 
##############################
def buy_down_trend_finishes(session, to_buy,BUY_VOLUME2, last): 
   buy_payload = {'ticker': to_buy, 'type': 'LIMIT', 'quantity': BUY_VOLUME2, 'action': 'BUY', 'price': last -SPREAD_buy } 
   session.post('http://localhost:9999/v1/orders', params=buy_payload) 
    

def sell_up_trend_finishes(session, to_sell,SELL_VOLUME2, last): 
   sell_payload = {'ticker': to_sell, 'type': 'LIMIT', 'quantity': SELL_VOLUME2, 'action': 'SELL', 'price': last +SPREAD_sell } 
   session.post('http://localhost:9999/v1/orders', params=sell_payload) 
    
def history():
     with requests.Session() as s:
        s.headers.update(API_KEY)
        payload = {'ticker': 'ALGO'}
        resp = s.get('http://localhost:9999/v1/securities/history', params = payload)
        if resp.ok:
            book = resp.json()
            return book
        raise ApiException("Authoriation error. Please check API key")
        
def ticker_bid_ask(ticker):
     with requests.Session() as s:
        s.headers.update(API_KEY)
        payload = {'ticker':ticker}
        resp = s.get('http://localhost:9999/v1/securities/book', params = payload)
        if resp.ok:
            book = resp.json()
           # return book['bids'][0]['price'],book['asks'][0]['price']
            return book['asks'][0]['price'],book['bids'][0]['price']
        raise ApiException("Authoriation error. Please check API key")
        
def get_orders(status): 
    with requests.Session() as s:
        s.headers.update(API_KEY)
        payload = {'status': status} 
        resp = s.get('http://localhost:9999/v1/orders', params=payload) 
        if resp.status_code == 401: 
            raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT REST API Documentation.pdf)') 
        orders = resp.json() 
        return orders 
def get_tick(session): 
   resp = session.get('http://localhost:9999/v1/case') 
   if resp.status_code == 401: 
       raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT REST API Documentation.pdf)') 
   case = resp.json() 
   return case['tick'] 
def get_position():
    with requests.Session() as s: # step 3
         s.headers.update(API_KEY) # step 4
         resp = s.get('http://localhost:9999/v1/securities')
         if resp.ok: 
             case = resp.json()
             tick = case[0]['position'] # accessing the 'tick' value that was returned
             #print('The case is on tick', tick) # step 8 
             return tick    
def calculate_ema(prices, days, smoothing=2):
    ema = [sum(prices[:days]) / days]
    for price in prices[days:]:
        ema.append((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))    
    ema_print=[]
    for i in range(0,10):
        ema_print.append(ema[i])
    return ema_print
            
def pos_id(oo):
    ID_pos = []
    ID_neg = []
    for item in oo:
         Act = item['action']
         ID = item['order_id']
         if Act == 'BUY':
            ID_pos.append(ID)
         else:
            ID_neg.append(ID)
    ID_pos.reverse()
    ID_neg.reverse()
    return ID_pos,ID_neg

def cancel_orders_specific(cancel_ids):
    with requests.Session() as s: # step 3
        s.headers.update(API_KEY) # step 4
        words = ['http://localhost:9999/v1/orders/',str(cancel_ids)]
        idd="".join(words)
        s.delete(idd)
        
def cancel_orders_specific_all(cancel_ids):
    with requests.Session() as s: # step 3
        s.headers.update(API_KEY) # step 4
        for i in range(0,len(cancel_ids)):
            cid=cancel_ids[i]
            words = ['http://localhost:9999/v1/orders/',str(cid)]
            idd="".join(words)
            s.delete(idd)
   
def open_pos(oo):
    Quantity_pos = 0
    Quantity_neg = 0
    for item in oo:
         Act = item['action']
         Quantity = item['quantity']
         if Act == 'BUY':
              Quantity_pos += Quantity
         else:
              Quantity_neg += Quantity
    return Quantity_pos, -Quantity_neg
def cancel_orders():
    with requests.Session() as s: # step 3
         s.headers.update(API_KEY) # step 4
         s.post('http://localhost:9999/v1/commands/cancel?all=1')
        

def buy_sell(session, to_buy, to_sell, algo_close_bid,algo_close_ask,BUY_VOLUME77,SELL_VOLUME77): 
   buy_payload = {'ticker': to_buy, 'type': 'LIMIT', 'quantity': BUY_VOLUME77, 'action': 'BUY', 'price': algo_close_bid - SPREAD_buy} 
   sell_payload = {'ticker': to_sell, 'type': 'LIMIT', 'quantity': SELL_VOLUME77, 'action': 'SELL', 'price': algo_close_ask + SPREAD_sell} 
   session.post('http://localhost:9999/v1/orders', params=buy_payload) 
   session.post('http://localhost:9999/v1/orders', params=sell_payload) 
    
def buy_sell_upward_trend(session, to_buy, to_sell, last,BUY_VOLUME): 
    buy_payload = {'ticker': to_buy, 'type': 'LIMIT', 'quantity': BUY_VOLUME, 'action': 'BUY', 'price': last - SPREAD_trend_buy} 
    session.post('http://localhost:9999/v1/orders', params=buy_payload) 
    #print("placed")
    
def buy_sell_downward_trend(session, to_buy, to_sell, last,SELL_VOLUME): 
    sell_payload = {'ticker': to_sell, 'type': 'LIMIT', 'quantity': SELL_VOLUME, 'action': 'SELL', 'price': last + SPREAD_trend_sell} 
    session.post('http://localhost:9999/v1/orders', params=sell_payload)     
    #print('Placed')


    
# this is the main method containing the actual market making strategy logic 
def main(): 
   # creates a session to manage connections and requests to the RIT Client 
   with requests.Session() as s: 
       # add the API key to the session to authenticate during requests 
        s.headers.update(API_KEY) 
        # get the current time of the case 
        ###############################################FROM HERE
        tick = get_tick(s) 
        last_tick= get_tick(s)
       # while the time is between 5 and 295, do the following 
        while tick > 1 and tick < 300:
            ctick=get_tick(s)
            oo=get_orders('OPEN')
            position=get_position()
            if position >= level3:
                SELL_VOLUME=SELL_VOLUME2*3
                BUY_VOLUME=BUY_VOLUME2
                SPREAD_sell = 0.01
                SPREAD_buy = 0.03
                SPREAD_trend_sell = 0.01
                SPREAD_trend_buy = 0.03
            elif position >= level1 and position<=level2:
                SELL_VOLUME=SELL_VOLUME2*2
                BUY_VOLUME=BUY_VOLUME2
                SPREAD_sell = 0.01
                SPREAD_buy = 0.02
                SPREAD_trend_sell = 0.01
                SPREAD_trend_buy = 0.02
            elif position <= -level1 and position >= -level2:
                SELL_VOLUME=SELL_VOLUME2
                BUY_VOLUME=BUY_VOLUME2*2
                SPREAD_sell = 0.02
                SPREAD_buy = 0.01
                SPREAD_trend_sell = 0.02
                SPREAD_trend_buy = 0.01
            elif position <= -level3:
                SELL_VOLUME=SELL_VOLUME2
                BUY_VOLUME=BUY_VOLUME2*3
                SPREAD_sell = 0.03
                SPREAD_buy = 0.01
                SPREAD_trend_sell = 0.03
                SPREAD_trend_buy = 0.01
            elif len(get_orders('TRANSACTED'))!=0:
                if get_orders('TRANSACTED')[0]['tick']-ctick >=tickers_since_last:
                    SELL_VOLUME=SELL_VOLUME2*3
                    BUY_VOLUME=BUY_VOLUME2*3
                    SPREAD_sell = 0.01
                    SPREAD_buy = 0.01
                    SPREAD_trend_sell = 0.01
                    SPREAD_trend_buy = 0.01
            elif position>-level1 and position<level1:
                SELL_VOLUME=SELL_VOLUME2*2
                BUY_VOLUME=BUY_VOLUME2*2
                SPREAD_sell = 0.02
                SPREAD_buy = 0.02
                SPREAD_trend_sell = 0.02
                SPREAD_trend_buy = 0.02
            ### detect when the last sale was, and if we havent made a sale in 3 ticks, reduce spread
            position=get_position()
            ob=open_pos(oo)[0]
            os=open_pos(oo)[1]
            if 20000 <= position + ob:
                bye_id=pos_id(oo)[0]
                cancel_orders_specific_all(bye_id)
            if -20000 >= position -os:
                bye_id=pos_id(oo)[1]
                cancel_orders_specific_all(bye_id)
                   
            else:
                orders = get_orders('OPEN') 
                algo_close=ticker_bid_ask('ALGO')
                algo_close_bid=algo_close[0]
                algo_close_ask=algo_close[1]
                buy_sell(s, 'ALGO', 'ALGO', algo_close_bid,algo_close_ask,BUY_VOLUME,SELL_VOLUME) 
                orders = get_orders('OPEN') 
                sleep(.5) 
            position=get_position()     
            if 20000 <= position:
                cancel_orders()
                kill_everything=0
                posi=get_position()
                SELL_VOLUME=SELL_VOLUME2
                BUY_VOLUME=BUY_VOLUME2
                SPREAD_sell = 0.01
                SPREAD_buy = 0.01
                SPREAD_trend_sell = 0.01
                SPREAD_trend_buy = 0.01
                while posi > 13000:
                    algo_close=ticker_bid_ask('ALGO')
                    algo_close_ask=algo_close[1] 
                    sell_up_trend_finishes(s, 'ALGO', SELL_VOLUME, algo_close_ask) 
                    sleep(0.5)
                    kill_everything=len(get_orders('OPEN'))
                    if kill_everything >=3:
                        oo=get_orders('OPEN')
                        try:
                            cancel_ids=pos_id(oo)[1][0]
                            cancel_orders_specific(cancel_ids)
                            posi=get_position()
                        except:
                            posi=get_position()
  
                else: 
                    cancel_orders()

            if -20000 >= position:
                cancel_orders()
                kill_everything=0
                posi=get_position()
                SELL_VOLUME=SELL_VOLUME2
                BUY_VOLUME=BUY_VOLUME2
                SPREAD_sell = 0.01
                SPREAD_buy = 0.01
                SPREAD_trend_sell = 0.01
                SPREAD_trend_buy = 0.01
                while posi < -13000:
                    algo_close=ticker_bid_ask('ALGO')
                    algo_close_bid=algo_close[0]
                    buy_down_trend_finishes(s, 'ALGO', BUY_VOLUME, algo_close_bid) 
                    sleep(0.5)
                    kill_everything=len(get_orders('OPEN'))
                    if kill_everything >=3:
                        oo=get_orders('OPEN')
                        try:
                            cancel_ids=pos_id(oo)[0][0]
                            cancel_orders_specific(cancel_ids)
                            posi=get_position()
                        except:
                            posi=get_position()
                else: 
                    cancel_orders()

            if len(get_orders('OPEN')) >= 15: 
                oo=get_orders('OPEN')
                if len(pos_id(oo)[0]) !=0:
                    cancel_ids=pos_id(oo)[0][0]
                    cancel_orders_specific(cancel_ids)
                if len(pos_id(oo)[1]) !=0:
                    cancel_ids=pos_id(oo)[1][0]
                    cancel_orders_specific(cancel_ids)
                
                
            tick = get_tick(s) 
            ############################################# TO HERE IS BASE CODE 
            ### TRENDS
            
            if tick != last_tick: #this is to only run the EMA strategy ONCE per tick
                if tick >=20:
                    last_tick=get_tick(s)  
                    history_prices=history() #from line 148 to 155 is calculating the EMA
                    last_X_prices=[]
                    for i in range(0,19):
                        last_X_prices.append(history_prices[i]["close"])
                    last_X_prices2=[]
                    for i in range(0,len(last_X_prices)+1):
                        last_X_prices2.append(last_X_prices[(len(last_X_prices)-1)-i])
                    ema = calculate_ema(last_X_prices2, 9)
                    #### this is to detect the upward trend
                    if ema[4]/ema[2] < ema[9]/ema[4]:
                        algo_close=ticker_bid_ask('ALGO')
                        algo_close_bid=algo_close[0]
                    ### if the trend is up, then we place a buying order for 1000
                        buy_sell_upward_trend(s, 'ALGO', BUY_VOLUME2, algo_close_bid-.01,BUY_VOLUME) 
                        buy_sell_upward_trend(s, 'ALGO', BUY_VOLUME2, algo_close_bid,BUY_VOLUME) 


                    ## downward trend
                    elif ema[4]/ema[2] > ema[9]/ema[4]:
                        algo_close=ticker_bid_ask('ALGO')
                        algo_close_ask=algo_close[1]
                        ### if the trend is down, then we place a selling order for 1000
                        buy_sell_downward_trend(s, 'ALGO', SELL_VOLUME2, algo_close_ask+0.01,SELL_VOLUME) 
                        buy_sell_downward_trend(s, 'ALGO', SELL_VOLUME2, algo_close_ask,SELL_VOLUME) 
        

        
        #### after this iteration, the placed orders following the EMA parameters will get cancelled if they do not
        ### get executed
        

# this calls the main() method when you type 'python algo2.py' into the command prompt 
if __name__ == '__main__': 
   signal.signal(signal.SIGINT, signal_handler) 
   main() 
