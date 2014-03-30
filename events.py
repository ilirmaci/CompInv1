'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Feb, 15, 2013

@author: Ilir Maci
'''


import pandas 
from qstkutil import DataAccess as da
import numpy as np
import math
import copy
import qstkutil.qsdateutil as du
import datetime as dt
import qstkutil.DataAccess as da
import qstkutil.tsutil as tsu
import qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

# Get the data from the data store
storename = "Yahoo" # get data from our daily prices source
# Available field names: open, close, high, low, close, actual_close, volume
closefield = "actual_close"
volumefield = "volume"
window = 10

def findEvents(symbols, startday,endday, marketSymbol,verbose=False):

        # Reading the Data for the list of Symbols.	
        timeofday=dt.timedelta(hours=16)
        timestamps = du.getNYSEdays(startday,endday,timeofday)
        dataobj = da.DataAccess('Yahoo')
        if verbose:
                print __name__ + " reading data"
        # Reading the Data
        close = dataobj.get_data(timestamps, symbols, closefield)
        
        # Completing the Data - Removing the NaN values from the Matrix
        close = (close.fillna(method='ffill')).fillna(method='backfill')
        
        # Calculating Daily Returns for the Market
        SPYValues=close[marketSymbol]

        # Calculating the Returns of the Stock Relative to the Market 
        # So if a Stock went up 5% and the Market rised 3%. The the return relative to market is 2% 
        np_eventmat = copy.deepcopy(close)
        for sym in symbols:
                for time in timestamps:
                        np_eventmat[sym][time]=np.NAN

        if verbose:
                print __name__ + " finding events"

        orders = open('orders.csv', 'w')
        
        # Generating the Event Matrix
        for symbol in symbols:
                for i in range(2,len(close[symbol])):
                        if close[symbol][i-1]>=7.0 and close[symbol][i]<7.0: #TRUE if price drops below 5.0
                                np_eventmat[symbol][i] = 1.0  #overwriting by the bit, marking the event
                                j = min([i+5, len(close) -1]) #order reversing day
                                writeOrder(close.index[i], symbol, 'Buy', 100, orders)
                                writeOrder(close.index[j], symbol, 'Sell', 100, orders)
        orders.close()
        return np_eventmat


def writeOrder(timestamp, symbol, operation, quantity, file):
        '''(datetime, str, str, int, file open for w) -> NullType
        Writes order into specified file in CSV format in
        the following order:
        year, month, day, symbol, operation, quantity

        Prerequisites: operation is one of ['Buy', 'Sell']
        '''
        date = timestamp.strftime('%Y,%m,%d')
        line = ','.join([date, symbol, operation, str(quantity)]) + '\n'
        file.write(line)

#################################################
################ MAIN CODE ######################
#################################################

dataobj = da.DataAccess('Yahoo')
symbols = dataobj.get_symbols_from_list("sp5002012")
symbols.append('SPY')
# You might get a message about some files being missing, don't worry about it.

startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
eventMatrix = findEvents(symbols,startday,endday,marketSymbol='SPY',verbose=True)

eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=20,lookforward_days=20,verbose=True)

eventProfiler.study(filename="sp5002012.pdf",plotErrorBars=True,plotMarketNeutral=True,plotEvents=False,marketSymbol='SPY')


