from functools import wraps
from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
from models import db, User, Portfolio, Stocks, TransactionHistory
from app import app
from datetime import datetime
import json



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
    return{
        "symbol": stock.symbol,
        "openDate": transactionHistory.createDate.date(),
        "type": "BUY" if transactionHistory.transactionType == 1 else "SELL",
        "amount": transactionHistory.amount,
        "openPrice": transactionHistory.price,
        "lastPrice": round(stock_response['lastPrice'], 2),
        "marketValue": round(transaction_market_value,2),
        "dailyTransactionProfit": round(daily_transaction_profit, 2),
        "dailyTransactionPercentageProfit": round((stock_response["lastPrice"] - stock_response["regularMarketPreviousClose"]) / stock_response["regularMarketPreviousClose"] * 100, 2),
        "netTransactionProfit": round(net_transaction_profit, 2),
        "netTransactionProfitPercentage": round((stock_response["lastPrice"] - transactionHistory.price) / transactionHistory.price * 100, 2),
        "transactionId": transactionHistory.id
    }

def profitHistoryof_stocks(stocks):
    response = []

    for stock in stocks:
        data = yf.download(stock.symbol, start=stock.createDate, end=datetime.now())
        stock_profits = []
        for row in data.iloc:
            #stockProfit = (row.Close - stock.average_cost) * stock.amount
            average_cost,amount = getCurrentDateValuesForStock(row.name.date(),stock)
            stockProfit = (row.Close - average_cost) * amount
            # üstteki get fonksiyonun için transactionhistory createDate <= get... ise dahil et yaparsn, 2 fonksiyonu birleştirirsn
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

    average_cost = total_MarketValue/amount  
    return average_cost,amount
      
    