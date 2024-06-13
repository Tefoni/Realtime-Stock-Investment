from bs4 import BeautifulSoup
import requests
import yfinance as yf
from models import db, User, Portfolio, Stocks, TransactionHistory
from app import app
from datetime import datetime
from math import isnan
import re
import concurrent.futures




def getPortfolioById(portfolioId):
    with app.app_context():
      return Portfolio.query.filter_by(id = portfolioId).first()

def getStocksByPortfolioId(_portfolioId):
    with app.app_context():
        return Stocks.query.filter(Stocks.portfolioId == _portfolioId,Stocks.amount > 0).all()

def getStockByPortfolioId(_portfolioId,stockSymbol):
    with app.app_context():   
      return Stocks.query.filter(Stocks.portfolioId == _portfolioId,Stocks.symbol == stockSymbol).first()
    
def getPortfolioStock(stock):
    stock_response = yf.Ticker(stock.symbol).basic_info
    stock_market_value = stock_response['lastPrice'] * stock.amount
    net_stock_profit = (stock_response['lastPrice'] - stock.average_cost) * stock.amount
    daily_stock_profit = (stock_response['lastPrice'] - stock_response['regularMarketPreviousClose']) * stock.amount
    dailyStockPercentageProfit = (stock_response["lastPrice"] - stock_response["regularMarketPreviousClose"]) / stock_response["regularMarketPreviousClose"] * 100
    if str(stock_response['regularMarketPreviousClose']) == "nan":
        daily_stock_profit = 0
        dailyStockPercentageProfit = 0
    
    return {
        "symbol": stock.symbol,
        "amount": stock.amount,
        "average_cost": round(stock.average_cost,2),
        "lastPrice": round(stock_response['lastPrice'], 2),
        "marketValue": round(stock_market_value, 2),
        "dailyStockProfit": round(daily_stock_profit, 2),
        "dailyStockPercentageProfit": round(dailyStockPercentageProfit, 2),
        "netStockProfit": round(net_stock_profit, 2),
        "netStockProfitPercentage": round((stock_response["lastPrice"] - stock.average_cost) / stock.average_cost * 100, 2),
        "stockId": stock.id
    }

def getMarketValueDistribution(stock):
    stock_response = yf.Ticker(stock.symbol).basic_info
    stock_market_value = stock_response['lastPrice'] * stock.amount
    return {"symbol": stock.symbol,
            "marketValue": stock_market_value}

def getTransactionHistory(transactionHistory):
    with app.app_context(): 
        stock = Stocks.query.filter(Stocks.id == transactionHistory.stockId).first()
    stock_response = yf.Ticker(stock.symbol).basic_info
    transaction_market_value = stock_response['lastPrice'] * transactionHistory.amount
    net_transaction_profit = (stock_response['lastPrice'] - transactionHistory.price) * transactionHistory.amount
    daily_transaction_profit = (stock_response['lastPrice'] - stock_response['regularMarketPreviousClose']) * transactionHistory.amount
    dailyTransactionPercentageProfit = round((stock_response["lastPrice"] - stock_response["regularMarketPreviousClose"]) / stock_response["regularMarketPreviousClose"] * 100, 2)
    netTransactionProfitPercentage = round((stock_response["lastPrice"] - transactionHistory.price) / transactionHistory.price * 100, 2)
    return{
        "symbol": stock.symbol,
        "openDate": transactionHistory.createDate.date(),
        "type": "BUY" if transactionHistory.transactionType == 1 else "SELL",
        "amount": transactionHistory.amount,
        "openPrice": transactionHistory.price,
        "lastPrice": round(stock_response['lastPrice'], 2),
        "marketValue": round(transaction_market_value,2) if transactionHistory.transactionType == 1 else round(transaction_market_value*-1,2),
        "dailyTransactionProfit": "-"if isnan(daily_transaction_profit) else ( round(daily_transaction_profit, 2) if transactionHistory.transactionType == 1 else round(daily_transaction_profit*-1, 2) ),
        "dailyTransactionPercentageProfit": "-" if isnan(dailyTransactionPercentageProfit) else ( dailyTransactionPercentageProfit if transactionHistory.transactionType == 1 else dailyTransactionPercentageProfit*-1 ),
        "netTransactionProfit": round(net_transaction_profit, 2) if transactionHistory.transactionType == 1 else round(net_transaction_profit*-1, 2),
        "netTransactionProfitPercentage": netTransactionProfitPercentage if transactionHistory.transactionType == 1 else netTransactionProfitPercentage*-1,
        "transactionId": transactionHistory.id
    }

def profitHistoryof_stocks(stocks,startDate = 0,endDate = 0):
    response = []
    for stock in stocks:
        if startDate != 0 and endDate != 0:
            data = yf.download(stock.symbol, start=startDate, end=endDate)
        else:
            data = yf.download(stock.symbol, start=stock.createDate, end=datetime.now())
        stock_profits = []
        for row in data.iloc:
            average_cost,amount = getCurrentDateValuesForStock(row.name.date(),stock)
            if amount != 0:
                stockProfit = (row.Close - average_cost) * amount
                stock_profits.append({
                        "date": str(row.name.date()),
                        "profit": stockProfit
                    }
                )

        response.append({
                "symbol": stock.symbol,
                "profits": stock_profits
            }
        )
    

    return response

def getCurrentDateValuesForStock(date,stock):
    amount = 0
    average_cost = 0
    total_MarketValue = 0
    with app.app_context(): 
        transactions = TransactionHistory.query.filter(TransactionHistory.stockId == stock.id).all()

    for transaction in transactions:
        if transaction.transactionType == 1 and transaction.createDate.date() <= date:    #BUY
                amount+= transaction.amount
                total_MarketValue += transaction.amount * transaction.price

        elif transaction.transactionType == 0 and transaction.createDate.date() <= date:   #SELL
                amount -= transaction.amount
                total_MarketValue -= transaction.amount * transaction.stockCost

    if amount <= 0:
        return 0,0
    
    average_cost = total_MarketValue/amount  
    return average_cost,amount

def stockNames():
    url = 'https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/default.aspx'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find('table',{"data-csvname": "tumhisse"}).find('tbody').find_all('a')

    names =[stock.text for stock in rows]

    cleaned_names = [name.strip().replace("\r\n","") for name in names]
    cleaned_names = [name for name in cleaned_names if name.isalpha()]
    cleaned_names_with_extension = [name + ".IS" for name in cleaned_names]
    return cleaned_names_with_extension
      
def getStockValue(stock):
        info = yf.Ticker(stock).basic_info
        return {
            "ticker": stock.split(".IS")[0],
            "last": round(info["lastPrice"],2),
            "change": round( (info["lastPrice"] - info["regularMarketPreviousClose"]) / info["regularMarketPreviousClose"] * 100, 2),
            "volume": info["lastVolume"]
        }

def getWatchListStock(stock):
    info = yf.Ticker(stock).basic_info

    # Mevcut tarihi ve saati al
    now = datetime.now()
    # Saat, dakika ve saniye formatında al
    current_time = now.strftime("%H:%M:%S")
    return {
        "market": stock.split(".IS")[0],
        "last": round(info["lastPrice"],2),
        "high": round(info["dayHigh"],2),
        "low": round(info["dayLow"],2),
        "open": round(info["open"],2),
        "time": current_time,
        "change": round( (info["lastPrice"] - info["previousClose"]) / info["previousClose"] * 100, 2),
        "volume": info["lastVolume"]
    }
 
def getIndexItems():
    eur_try = yf.Ticker("EURTRY=X").basic_info
    usd_try = yf.Ticker("USDTRY=X").basic_info
    xau_usd = yf.Ticker("GC=F").basic_info
    xu30 = getIndice("XU30 hisse")
    xu30["title"] = "XU30"
    return [
        {
            "title": "EURTRY",
            "value": round(eur_try["lastPrice"],2),
            "change": round( (eur_try["lastPrice"] - eur_try["open"])/eur_try["open"] *100, 2),
        },
        {
            "title": "USDTRY",
            "value": round(usd_try["lastPrice"],2),
            "change": round( (usd_try["lastPrice"] - usd_try["open"])/usd_try["open"] *100, 2),
        },
        getIndice("XU100"),
        xu30,
        {
            "title": "XAUUSD",
            "value": round(xau_usd["lastPrice"],2),
            "change": round( (xau_usd["lastPrice"] - xau_usd["open"])/xau_usd["open"] *100, 2),
        }
    ]


def getIndice(indice_name):
    url = f'https://www.google.com/search?q={indice_name}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Google Finance için hisse değerini bulmak
    stock_info = soup.find('div', {"class": "BNeawe iBp4i AP7Wnd"}).text
    parts = stock_info.split()

    # İkinci kısım değişim değerini ve işaretini temsil eder
    change_sign = 1 if parts[1][0] == '+' else -1

    # Yüzde değişim değerini almak için
    percentage_sign = 1 if change_sign == 1 else -1
    percentage_value = percentage_sign * float(parts[2].strip("()%").replace(',', '.'))

    return {
        "title": indice_name,
        "value": parts[0],
        "change": percentage_value
    }
    

def getSectorIndices():
    tickers = ["XUTEK","XBANK","XBLSM","XELKT","XGIDA","XHOLD hisse","XHARZ","XAKUR","XSPOR","XSGRT","XULAS","XTRZM","XGMYO"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        sectorIndicesOutput = list(executor.map(getIndice, tickers))

    return sectorIndicesOutput