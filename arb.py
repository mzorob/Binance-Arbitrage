from binance.client import Client
import pandas as pd
import json
from pandas.io.json import json_normalize
import numpy as np
import time


def pdiff(ask,bid):
    return (bid-ask)/bid

def vol(ask,bid):
    if ask>bid:
        return bid
    else:
        return ask

    

api_key = 'probably should write something to import these from a file'
api_secret = 'but its manual for now'





 
client = Client(api_key, api_secret)

tickers = client.get_orderbook_tickers()

eth = [] #95
btc = [] #97
bnb = [] #35
usdt = [] #6
unknown = [] #1

for x in tickers:
    if x['symbol'][-1] == 'H':
        x['symbol'] = x['symbol'][:-3]
        x['ETHaskPrice'] = x.pop('askPrice')
        x['ETHaskQty'] = x.pop('askQty')
        x['ETHbidPrice'] = x.pop('bidPrice')
        x['ETHbidQty'] = x.pop('bidQty')
        eth.append(x)
    elif x['symbol'][-1:] == 'C':
        x['symbol'] = x['symbol'][:-3]
        x['BTCaskPrice'] = x.pop('askPrice')
        x['BTCaskQty'] = x.pop('askQty')
        x['BTCbidPrice'] = x.pop('bidPrice')
        x['BTCbidQty'] = x.pop('bidQty')        
        btc.append(x)      
    elif x['symbol'][-1] == 'B':
        x['symbol'] = x['symbol'][:-3]
        x['BNBaskPrice'] = x.pop('askPrice')
        x['BNBaskQty'] = x.pop('askQty')
        x['BNBbidPrice'] = x.pop('bidPrice')
        x['BNBbidQty'] = x.pop('bidQty')  
        bnb.append(x)
    elif x['symbol'][-1] == 'T':
        x['symbol'] = x['symbol'][:-4] 
        usdt.append(x)
    else:
        unknown.append(x)

bnb = [ticker for ticker in bnb if ticker['symbol'] != 'LEND']
#print(len(eth),len(btc),len(bnb),len(usdt),len(unknown),eth[1])
#print(usdt)

#normalize tickers to usd
for ticker in btc:
    ticker['BTCbidPrice'] = float(ticker['BTCbidPrice']) * float(usdt[0]['bidPrice'])
    ticker['BTCbidQty']   = float(ticker['BTCbidQty']) * float(usdt[0]['bidQty'])
    ticker['BTCaskPrice'] = float(ticker['BTCaskPrice']) * float(usdt[0]['askPrice'])
    ticker['BTCaskQty']   = float(ticker['BTCaskQty']) * float(usdt[0]['askQty'])
    
for ticker in eth:
    ticker['ETHbidPrice'] = float(ticker['ETHbidPrice']) * float(usdt[1]['bidPrice'])
    ticker['ETHbidQty']   = float(ticker['ETHbidQty']) * float(usdt[1]['bidQty'])
    ticker['ETHaskPrice'] = float(ticker['ETHaskPrice']) * float(usdt[1]['askPrice'])
    ticker['ETHaskQty']   = float(ticker['ETHaskQty']) * float(usdt[1]['askQty'])
    
for ticker in bnb:
    ticker['BNBbidPrice'] = float(ticker['BNBbidPrice']) * float(usdt[2]['bidPrice'])
    ticker['BNBbidQty']   = float(ticker['BNBbidQty']) * float(usdt[2]['bidQty'])
    ticker['BNBaskPrice'] = float(ticker['BNBaskPrice']) * float(usdt[2]['askPrice'])
    ticker['BNBaskQty']   = float(ticker['BNBaskQty']) * float(usdt[2]['askQty'])


                
btc_eth = [c for c in btc for e in eth if c['symbol'] == e['symbol']]
eth_btc = [e for e in eth for c in btc if c['symbol'] == e['symbol']]

df1 = pd.DataFrame(btc_eth)
df2 = pd.DataFrame(eth_btc)


df1.set_index('symbol',inplace=True)
df2.set_index('symbol',inplace=True)
df1.sort_index(inplace=True)
df2.sort_index(inplace=True)

df = pd.concat([df1,df2],axis=1)

df['btcTOeth'] = np.vectorize(pdiff)(df['BTCaskPrice'],df['ETHbidPrice'])
df['ethTObtc'] = np.vectorize(pdiff)(df['ETHaskPrice'],df['BTCbidPrice'])
df['btcTOethVol'] = np.vectorize(vol)(df['BTCaskQty'],df['ETHbidQty'])
df['ethTObtcVol'] = np.vectorize(vol)(df['ETHaskQty'],df['BTCbidQty'])
df['btcTOethDOLLARS'] = df['btcTOeth']*df['btcTOethVol']*df['BTCaskPrice']
df['ethTObtcDOLLARS'] = df['ethTObtc']*df['ethTObtcVol']*df['ETHaskPrice']
df['btcTOethCAPITAL'] = df['btcTOethVol']*df['BTCaskPrice']
df['ethTObtcCAPITAL'] = df['ethTObtcVol']*df['ETHaskPrice']

#print(df1.head())
#print(df2.head())

bestETH = []
bestBTC = []

df.sort_values('btcTOethDOLLARS',inplace=True,ascending=False)
print(df.head())
df.sort_values('ethTObtcDOLLARS',inplace=True,ascending=False)  
print(df.head())


#print(df.loc[df['btcTOeth'].idxmax()]['btcTOeth'])
#print([df['btcTOeth'].idxmax(),(df.loc[df['btcTOeth'].idxmax()]['btcTOeth'])*df.loc[df['ethTObtc'].idxmax()]['ethTObtc']])
#print(df.loc[df['btcTOeth'].idxmax()]['btcTOethVol'])
#print(df.head())
#print(df.loc[df['ethTObtc'].idxmax()]['ethTObtc'])
#print([df['ethTObtc'].idxmax(),(df.loc[df['ethTObtc'].idxmax()]['ethTObtc'])*df.loc[df['ethTObtc'].idxmax()]['ethTObtcVol']])
#print(df.loc[df['ethTObtc'].idxmax()]['ethTObtcVol'])

#bEIdx = df.loc[df['btcTOethDOLLARS'].idxmax()]
#eBIdx = df.loc[df['ethTObtcDOLLARS'].idxmax()]

#print([df['btcTOethDOLLARS'].idxmax(),bEIdx['btcTOeth'],bEIdx['btcTOethDOLLARS'],bEIdx['btcTOethVol'],bEIdx['btcTOethCAPITAL']])
#print([df['ethTObtcDOLLARS'].idxmax(),eBIdx['ethTObtc'],eBIdx['btcTOethDOLLARS'],eBIdx['ethTObtcVol'],bEIdx['ethTObtcCAPITAL']])

#print(max(list(map(max, diffs))))
#print(bestETH)
#print(bestBTC)

if __name__ == '__main__':
    app.run_server(debug=True)
