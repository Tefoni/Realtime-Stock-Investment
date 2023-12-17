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

def getStockByPortfolioId(_portfolioId,stockSymbol):
    with app.app_context():   
      return Stocks.query.filter(Stocks.portfolioId == _portfolioId,Stocks.symbol == stockSymbol).first()
    
def getPortfolioStock(stock):
    stock_response = yf.Ticker(stock.symbol).basic_info
    stock_market_value = stock_response['lastPrice'] * stock.amount
    net_stock_profit = (stock_response['lastPrice'] - stock.average_cost) * stock.amount
    daily_stock_profit = (stock_response['lastPrice'] - stock_response['regularMarketPreviousClose']) * stock.amount
    return {
        "symbol": stock.symbol,
        "amount": stock.amount,
        "average_cost": stock.average_cost,
        "lastPrice": round(stock_response['lastPrice'], 2),
        "marketValue": round(stock_market_value, 2),
        "dailyStockProfit": round(daily_stock_profit, 2),
        "dailyStockPercentageProfit": round((stock_response["lastPrice"] - stock_response["regularMarketPreviousClose"]) / stock_response["regularMarketPreviousClose"] * 100, 2),
        "netStockProfit": round(net_stock_profit, 2),
        "netStockProfitPercentage": round((stock_response["lastPrice"] - stock.average_cost) / stock.average_cost * 100, 2)
    }


def profitHistoryof_stocks(stocks):
    response = []

    for stock in stocks:
        data = yf.download(stock.symbol, start=stock.createDate, end=datetime.now())
        stock_profits = []
        for row in data.iloc:
            stockProfit = (row.Close - stock.average_cost) * stock.amount
            #stockProfit = (row.Close - getAverageCostFromDate(row.name.date(),Stock)) - getStockAmountFromDate(date,Stock)
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

      
    