from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
from functions import *
from models import db, User, Portfolio, Stocks, TransactionHistory
from datetime import datetime,timedelta
from flask_login import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import concurrent.futures
from flask_cors import CORS
import matplotlib.pyplot as plt
import time
import requests
from bs4 import BeautifulSoup



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_investment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI_OPTIONS'] = {'timezone': '+03:00'}
app.config['SECRET_KEY'] = "testkey"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

CORS(app)
jwt = JWTManager(app)

db.init_app(app)

@app.route('/stockSymbols',methods=['GET'])
@jwt_required()
def stockSymbols():
    try:
        url = 'https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/default.aspx'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find('table',{"data-csvname": "tumhisse"}).find('tbody').find_all('a')

        names =[stock.text for stock in rows]

        cleaned_names = [name.strip().replace("\r\n","") for name in names]
        cleaned_names = [name for name in cleaned_names if name.isalpha()]
        cleaned_names_with_extension = [name + ".IS" for name in cleaned_names]
        return jsonify({"message": cleaned_names_with_extension,
                        "isSuccessful": True})
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False})

@app.route('/buyStock',methods=['POST'])
@jwt_required()
def buyStock():
    try:
        request_body = request.get_json()
        user_portfolio = getPortfolioById(request_body["portfolioId"])
        stock = getStockByPortfolioId(user_portfolio.id,str.upper(request_body["symbol"]))
        date_format = "%Y-%m-%dT21:00:00.000Z"
        date = datetime.strptime(request_body["date"],date_format).date() + timedelta(days=1)
        if(date > datetime.now().date()):
            raise ValueError("Gelecekteki bir tarihe işlem giremezsiniz.")
        if stock:
            if not isinstance(request_body["amount"], int) or request_body["amount"] <= 0:
                raise ValueError("Alınan hisse adedi pozitif tam sayı olmalıdır.")
            if request_body["cost"] <= 0:
                raise ValueError("Hisse fiyatı pozitif olmalıdır.")
            
            stock = getStockByPortfolioId(user_portfolio.id,str.upper(request_body["symbol"]))
            newAmount = stock.amount + request_body["amount"]
            newCost = (stock.amount*stock.average_cost + request_body["amount"]*request_body["cost"])/newAmount

            stock.amount = newAmount
            stock.average_cost = newCost
            stock.updateDate = date
            db.session.merge(stock)
            db.session.commit()

            transactionHistory = TransactionHistory(portfolio = user_portfolio, stocks = stock, amount = request_body["amount"], price = request_body["cost"], transactionType = 1, createDate = date)
            db.session.add(transactionHistory)

        else:
            new_stockResponse = yf.Ticker(request.get_json()["symbol"]).basic_info
            giveExceptionIfNotExist = new_stockResponse['lastPrice']

            new_stock = Stocks(portfolio = user_portfolio,symbol = request_body["symbol"],amount = request_body["amount"],average_cost = request_body["cost"],createDate = date)
            db.session.add(new_stock)

            transactionHistory = TransactionHistory(portfolio = user_portfolio, stocks = new_stock, amount = request_body["amount"], price = request_body["cost"], transactionType = 1, createDate = date)
            db.session.add(transactionHistory)


        db.session.commit()

        response = f"{request_body['cost']} fiyatından {request_body['amount']} adet {str.upper(request_body['symbol'])} kodlu hisse başarıyla portfolyeye eklendi."

        return jsonify({"message": response,
                        "isSuccessful": True})
    except Exception as e:
        db.session.rollback()

        if e.args[0] == "currentTradingPeriod":
            e = "Bu sembole sahip hisse bulunamadı."

        return jsonify({"message": str(e),
                       "isSuccessful": False})

@app.route('/sellStock',methods=['POST'])
@jwt_required()
def sellStock():
    try:
        request_body = request.get_json()
        user_portfolio = getPortfolioById(request_body["portfolioId"])
        stock = getStockByPortfolioId(user_portfolio.id,str.upper(request_body["symbol"]))
        old_cost = stock.average_cost
        date_format = "%Y-%m-%dT21:00:00.000Z"
        date = datetime.strptime(request_body["date"],date_format).date() + timedelta(days=1)
        if(date > datetime.now().date()):
            raise ValueError("Gelecekteki bir tarihe işlem giremezsiniz.")

        if stock:
            if not isinstance(request_body["amount"], int) or request_body["amount"] <= 0:
                raise ValueError("Satılan hisse adedi pozitif tam sayı olmalıdır.")
            if request_body["amount"] > stock.amount:
                raise ValueError("Portfolyede istenen adette hisse bulunmamaktadır.")
            if request_body["cost"] <= 0:
                raise ValueError("Hisse fiyatı pozitif olmalıdır.")
            
            newAmount = stock.amount - request_body["amount"]
            profitValue = (request_body["cost"] - stock.average_cost) * request_body["amount"]
            user_portfolio.closedPositionValue += profitValue
            db.session.merge(user_portfolio)
            db.session.commit()

            stock.amount = newAmount
            stock.updateDate = date
            if newAmount == 0:
                stock.average_cost = 0

            db.session.merge(stock)
            db.session.commit()

            transactionHistory = TransactionHistory(portfolio = user_portfolio, stocks = stock, amount = request_body["amount"], price = request_body["cost"], transactionType = 0, createDate = date, closeProfitValue = profitValue, stockCost = old_cost)
            db.session.add(transactionHistory)

        else:
            raise TypeError("Portfolyede bu hisse bulunmamaktadır.")


        db.session.commit()

        response = f"{request_body['cost']} fiyatından {request_body['amount']} adet {str.upper(request_body['symbol'])} kodlu hisse başarıyla satıldı."

        return jsonify({"message": response,
                        "isSuccessful": True})
    except Exception as e:
        db.session.rollback()

        if e.args[0] == "currentTradingPeriod":
            e = "Bu sembole sahip hisse bulunamadı."

        return jsonify({"message": str(e),
                       "isSuccessful": False})

@app.route('/profitHistory',methods=['POST'])
@jwt_required()
def profitHistory():
    try:
        user_portfolio = getPortfolioById(request.get_json()['portfolioId'])
        portfolio_stocks = getStocksByPortfolioId(request.get_json()['portfolioId'])
        start_dateofPortfolio = Stocks.query.filter(Stocks.portfolioId == user_portfolio.id).order_by(Stocks.createDate.asc()).first().createDate.date()
        end_dateofPortfolio = datetime.now().date()
        #with concurrent.futures.ThreadPoolExecutor() as executor:
        #    stock_infos = list(executor.map(profitHistoryof_stocks, portfolio_stocks))
        stock_infos = profitHistoryof_stocks(portfolio_stocks)
        
        return jsonify({"startDate": start_dateofPortfolio,
                        "endDate": end_dateofPortfolio,
                        "stocks": stock_infos,
                        "isSuccessful": True})
    except Exception as e:
        return jsonify({"message": str(e),
                       "isSuccessful": False})
    
@app.route('/marketValueHistory',methods=['POST'])
@jwt_required()
def marketValueHistory():
    try:
        return jsonify(1)
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False})
    
@app.route('/stockDistribution',methods=['POST'])
@jwt_required()
def stockDistribution():
    try:
        stocks = getStocksByPortfolioId(request.get_json()['portfolioId'])
        with concurrent.futures.ThreadPoolExecutor() as executor:
            distributions = list(executor.map(getMarketValueDistribution, stocks))

        totalMarket_Value = sum(distribution["marketValue"] for distribution in distributions)
        response = []  
        for distribution in distributions:
            response.append({
                "symbol": distribution["symbol"],
                "distribution":  round(distribution["marketValue"]/totalMarket_Value*100, 2)
            })

        return jsonify({
            "isSuccessful": True,
            "message": response
        })
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False})
          

@app.route('/transactionHistory',methods=['POST'])
@jwt_required()
def getTransactionHistories():
    try:
        portfolio_id = request.get_json()["portfolioId"]
        transactionhistories = TransactionHistory.query.filter(TransactionHistory.portfolioId == portfolio_id,TransactionHistory.amount > 0, TransactionHistory.price > 0).all()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            response = list(executor.map(getTransactionHistory, transactionhistories))
        response = sorted(response, key=lambda x: x['openDate'], reverse=True)
        return jsonify({
            "isSuccessful": True,
            "message": response
        })
    except Exception as e:
        return jsonify({"message": str(e),
                       "isSuccessful": False}) 


@app.route('/deleteTransaction',methods=['POST'])
@jwt_required()
def deleteTransaction():
    try:
        transaction_id = request.get_json()["transactionId"]
        transaction = TransactionHistory.query.filter(TransactionHistory.id == transaction_id).first()
        stock = Stocks.query.filter(Stocks.id == transaction.stockId).first()
        portfolio = getPortfolioById(stock.portfolioId)
        if transaction.transactionType == 1:    # BUY
            if transaction.amount > stock.amount:
                raise ValueError("Öncelikle satışı iptal etmelisiniz.")
            newStock_cost = ( (stock.amount*stock.average_cost)- transaction.amount*transaction.price )
            stock.amount -= transaction.amount
            if stock.amount == 0:
                newStock_cost = 0
            else:
                newStock_cost /= stock.amount
            stock.average_cost = newStock_cost
            stock.updateDate = datetime.now().date()
            #Update stock with new values
            db.session.merge(stock)
            db.session.commit()
            response = f"{transaction.price} fiyatından alınmış {transaction.amount} adet {stock.symbol} hisse alımı iptal edildi."
            #Delete Transaction history
            deletedTransaction = TransactionHistory.query.get(transaction_id)
            db.session.delete(deletedTransaction)
            db.session.commit()     

        else:                                   # SELL
            portfolio.closedPositionValue -= transaction.closeProfitValue
            newStock_cost = ( (stock.amount*stock.average_cost) + (transaction.amount*transaction.stockCost) )
            stock.amount += transaction.amount
            newStock_cost /= stock.amount
            stock.average_cost = newStock_cost
            stock.updateDate = datetime.now().date()
            #Update stock with new values
            db.session.merge(stock)
            db.session.commit()
            response = f"{transaction.price} fiyatından satılmış {transaction.amount} adet {stock.symbol} hisse satışı iptal edildi."
            #Delete Transaction history
            deletedTransaction = TransactionHistory.query.get(transaction_id)
            db.session.delete(deletedTransaction)
            db.session.commit()
            #Update portfolio with new close position value
            db.session.merge(portfolio)
            db.session.commit()                 

        return jsonify({
            "isSuccessful": True,
            "message": response
        })
    except Exception as e:
        return jsonify({"message": str(e),
                       "isSuccessful": False}) 

@app.route('/portfolio',methods=['POST'])
@jwt_required()
def portfolio():
    try:
        portfolio_id = request.get_json()["portfolioId"]
        portfolio_stocks = getStocksByPortfolioId(portfolio_id)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            stock_infos = list(executor.map(getPortfolioStock, portfolio_stocks))

        market_value = sum(info["marketValue"] for info in stock_infos)
        open_profit = sum(info["netStockProfit"] for info in stock_infos)
        daily_profit = sum(info["dailyStockProfit"] for info in stock_infos)
        closed_profit = getPortfolioById(request.get_json()["portfolioId"]).closedPositionValue
        return jsonify({
            "isSuccessful": True,
            "marketValue": round(market_value, 2),
            "openProfit": round(open_profit, 2),
            "closedProfit": round(closed_profit,2),
            "dailyProfit": round(daily_profit, 2),
            "stocks": stock_infos
        })

    except Exception as e:
        return jsonify({"message": str(e),
                       "isSuccessful": False}) 

@app.route('/addPortfolio',methods=['GET'])
@jwt_required()
def addPortfolio():
    try:
        user_email = get_jwt_identity()
        user = User.query.filter(User.email == user_email).first()
        userPortfolio = Portfolio(user = user,closedPositionValue = 0)
        db.session.add(userPortfolio)
        db.session.commit()

        return jsonify({
            "isSuccessful": True,
        })
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False})  
    
@app.route('/signUp',methods=['POST'])
def signUp():
    try:
        request_body = request.get_json()

        # Check if the email is already taken
        existing_user = User.query.filter_by(email=request_body["email"]).first()
        if existing_user:
            raise Exception("Email zaten kullanılmakta.")
        
        new_user = User(email=request_body["email"],password = generate_password_hash(request_body["password"], method='pbkdf2:sha256'),name = request_body["name"])
        db.session.add(new_user)
        db.session.commit()

        userPortfolio = Portfolio(user = new_user,closedPositionValue = 0)
        db.session.add(userPortfolio)
        db.session.commit()

        return jsonify({"message": "Kullanıcı başarıyla oluşturuldu.",
                        "isSuccessful": True})
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False})


@app.route('/login',methods=['POST'])
def login():
    try:
        request_body = request.get_json()
        user = User.query.filter_by(email=request_body["email"]).first()
        if user and check_password_hash(user.password,request_body["password"]):
            access_token = create_access_token(identity= user.email)
            return jsonify({"token": access_token,
                            "isSuccessful": True})
        else:
            raise Exception("Email veya şifre yanlış.Tekrar deneyiniz.")

    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False})


@app.route('/userPortfolioIds',methods=['GET'])
@jwt_required()
def getUserPortfolioIds():
    try:
        user_email = get_jwt_identity()
        user = User.query.filter(User.email == user_email).first()
        portfolios = Portfolio.query.filter(Portfolio.userId == user.id).all()
        portfolioIds = []
        for i in range(len(portfolios)):
            portfolioIds.append(portfolios[i].id)

        return jsonify({
            "isSuccessful": True,
            "message": portfolioIds
        })
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False})  


@app.route('/user',methods=['GET'])
@jwt_required()
def getCurrentUser():
    user_email = get_jwt_identity()
    user = User.query.filter(User.email == user_email).first()
    return jsonify(user.name) 
 
# Customize response for invalid token
@jwt.invalid_token_loader
@jwt.unauthorized_loader
def invalid_token(error):
    return jsonify({"message": "Geçersiz token.",
                    "isSuccessful": False}), 401

@jwt.expired_token_loader
def expired_token(error,error2):
    return jsonify({"message": "Süresi geçmiş token.",
                    "isSuccessful": False}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)

