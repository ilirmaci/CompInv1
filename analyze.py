from qstkutil import DataAccess as da
from qstkutil import qsdateutil as du
from qstkutil import tsutil as tsu

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import copy
import sys

# read input (filename and index symbol)
infile = sys.argv[1]
benchmark = sys.argv[2]

##infile = 'testdata.csv'
##benchmark = 'SPX'
	
# function to read contents of file into pandas object
def getValues(filename):
    '''(str) -> pandas DataFrame
    Return values read from filename (CSV, 4 columns) 
    into pandas object.
    '''
    return pd.read_csv(filename, names=['year', 'month', 'day', 'portfolio'], header=None)

# function to extract dates and create timestamps
def getDates(values):
    '''(pandas) -> list of datetime
    Return array of datetime objects based on dates in values.
    '''
    timestamps=[]
    for i in range(len(values)):
        year = values['year'][i]
        month = values['month'][i]
        day = values['day'][i]
        time = 16 #time of day in hours
        timestamps.append(dt.datetime(year, month, day, time, 0))
    timestamps.sort()
    return timestamps

###############################
########## MAIN BODY ##########
###############################


values = getValues(infile)
timestamps = getDates(values)
values.index = timestamps

data = da.DataAccess('Yahoo')
marketdata = data.get_data(timestamps, [benchmark], 'close')

##marketdata = np.ones(5) + np.random.normal(loc=0, scale=0.01, size=5)
marketdata = pd.DataFrame(marketdata, index=timestamps, columns=[benchmark])

# adding portfolio column
marketdata['portfolio'] = values['portfolio']
names = [benchmark, 'portfolio']

pricedata = marketdata.values #extract values

#normalizing benchmark value to fund initial value
pricedata[:, 0] = pricedata[:, 0]/pricedata[0,0] * pricedata[0,1]

plt.clf() #erase open graph
plt.plot(timestamps, pricedata)
plt.legend(names, loc=3)
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.savefig('analysis.pdf', format='pdf')

# daily returns
prices = marketdata['portfolio'].values
returns = copy.deepcopy(prices)

tsu.returnize0(returns)

#returns = prices[1:]/prices[:-1] - 1

print "Sharpe Ratio: " + str(np.sqrt(250)*returns.mean()/returns.std())
print "Total return(%): " + str(100*prices[-1]/prices[0] - 100)
print "Std. deviation of daily returns(%): " + str(100*returns.std())

