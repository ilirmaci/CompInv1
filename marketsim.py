'''
Code for HW3 of Computational Investment I course

MArket simulation that reads list of BUY/SELL orders from
file given in command line argument and prints total portfolio
value by day

@author: Ilir Maci
'''

from pylab import *
from qstkutil import DataAccess as da
from qstkutil import qsdateutil as du
from qstkutil import tsutil as tsu
import datetime as dt
import pandas as pd

initial_cash = float(sys.argv[1])
infile = sys.argv[2]
outfile = sys.argv[3]

#initial_cash = 50000
#infile = 'orders.csv'
#outfile = 'values.csv'



def readOrder(file):
    '''(str) -> pandas
    Return pandas data object with orders read and sorted from file
    (CSV format) that contains the following variables:
    Year, Month, Day, Symbol, BUY/SELL, Quantity, Empty (dropped)
    '''
    orders = pd.read_csv(file, header=None, 
        names=['year','month','day','sym','op','qty'])
    #orders = orders.drop(['empty'], axis=1)
    orders = orders.sort(columns=['year', 'month', 'day'])
    orders.index = range(len(orders))
    return orders

def getOrderDates(orders):
    '''(pandas) -> list of date object
    Return list of dates based on year, month, and date columns
    of order.
    '''
    dates = []
    for i in range(0,len(orders)):
    	dates.append(dt.datetime(orders['year'][i], orders['month'][i],
	            orders['day'][i], 16, 0))
    #dates.sort()
    return dates

def getTradingDays(orders):
    '''(pandas) -> list of timestamp
    Return list of timestamps for all trading dates between first and
    last day of order.
    '''
    last = len(orders) - 1
    startday = dt.datetime(orders['year'][0], orders['month'][0], orders['day'][0])
    endday = dt.datetime(orders['year'][last], orders['month'][last], orders['day'][last]+1)
    timeofday=dt.timedelta(hours=16)
    return du.getNYSEdays(startday,endday,timeofday)

def getOrderSymbols(orders):
    '''(pandas) -> list of str
    Return list of unique stock symbols in order.
    '''
    return list(set(orders['sym']))

def getPrices(dates, symbols, closefield):
    '''(list of datetime, list of str, str) -> pandas
    Return array of closing prices for stocks in symbol on dates.
    Possible closefield values: open, close, high, low, actual_close
    '''
    data = da.DataAccess('Yahoo')
    close = data.get_data(dates, symbols, closefield)
    close = (close.fillna(method='ffill')).fillna(method='backfill')
    return close

# update cash array based on orders
def computeCash(orders, orderdates, prices, initial):
    '''(pandas, list of datetime, pandas, number) -> ndarray of floats
    Computes cash remaining each day on prices array after completing
    buy/sell operations in order starting with initial cash.
    '''
    #start array at initial cash
    cash = initial * np.ones(len(prices))
    j = 0 
    #process orders, i is order index, j is cash portfolio index
    for i in range(len(orders)):
        j = prices.index.searchsorted(orderdates[i])
        
        if orders['op'][i].lower() == "buy":
            op = -1
        elif orders['op'][i].lower() == "sell":
            op = 1
        else:
            op = 0

        sym = orders['sym'][i]
        qty = orders['qty'][i]

        cash[j:] = cash[j] + op * prices[sym][j] * qty
        
        #print prices.index[j], sym, orders['op'][i], qty, prices[sym][j], cash[j], j
    return cash


# update stocks array based on orders
def computeStocks(orders, orderdates, dates):
    '''(pandas, list of datetime, pandas) -> pandas
    Return array of stock quantities in portfolio for dates
    in prices index.
    '''
    symbols = getOrderSymbols(orders)
    stocks = np.zeros((len(dates), len(symbols)))
    stocks = pd.DataFrame(data=stocks, index=dates, columns=symbols)

    for i in range(len(orderdates)):
        if orderdates[i] in dates:
            j = dates.index(orderdates[i])
        else:
            continue

        if orders['op'][i].lower() == "buy":
            op = 1
        elif orders['op'][i].lower() == "sell":
            op = -1
        else:
            op = 0

        sym = orders['sym'][i]
        qty = orders['qty'][i]

        stocks[sym][j:] = stocks[sym][j] + op*qty
        #print orders['op'][i], sym, qty
    return stocks

# compute value array
def computeValue(prices, stocks, cash):
    '''(pandas, ndarray of numbers, pandas) -> ndarray of floats
    Return array with value of portfolio (stocks and cash) using
    prices.
    '''
    return (stocks * prices).sum(axis=1) + cash

# write array to file
def writeValue(filename, values, dates):
    '''(str, ndarray of number, list of datetime) -> NullType
    Write values to filename (CSV) in following format:
    year,month,day,value\n
    '''
    file = open(filename, 'w')
    for i in range(len(values)):
        date = dates[i].strftime('%Y,%m,%d')
        line = date + ',' + str(values[i]) + "\n"
        file.write(line)
    file.close()

#############################
######### MAIN CODE #########
#############################

orders = readOrder(infile)
orderDates = getOrderDates(orders)
symbols = getOrderSymbols(orders)
timestamps = getTradingDays(orders)

prices = getPrices(timestamps, symbols, 'close')
cash = computeCash(orders, orderDates, prices, initial_cash)
stocks = computeStocks(orders, orderDates, timestamps)
values = computeValue(prices, stocks, cash)

writeValue(outfile, values, timestamps)



