from flask import Flask, jsonify,request
import json
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
from functions import *
from models import db, User, Portfolio, Stocks, TransactionHistory, WatchListStocks
from datetime import datetime,timedelta
from flask_login import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import concurrent.futures
from flask_cors import CORS
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


@app.route('/performance',methods=['GET'])
@jwt_required()
def performance():
    try:
        types = ["EUR","USD","GOLD","INTEREST"]
        codes = ["EURTRY=X","USDTRY=X","GC=F","INTEREST"]
        one_month_ago = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        one_month_ago_plus1 = (datetime.strptime(one_month_ago, "%Y-%m-%d") + timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')

        portfolio = 1000

        result = []
        i = 0
        usd_currentPrice =0
        usd_monthAgoPrice = 0
        usd_yesterday_price = 0
        for code in codes:
            if code != "INTEREST":
                info = yf.Ticker(code)
                history = info.history(start=one_month_ago, end=one_month_ago_plus1)
                month_ago_price = history['Close'].iloc[-1]
                current_price = info.basic_info["lastPrice"]
                open_price = info.basic_info["open"]

            if code == "USDTRY=X":
                usd_currentPrice = current_price
                usd_monthAgoPrice = month_ago_price
                usd_yesterday_price = open_price

            if code == "GC=F":
                perfMonth = ( (current_price/month_ago_price)*(usd_currentPrice/usd_monthAgoPrice) )*100  -100
                result.append({
                    "ticker": types[i],
                    "price": round(portfolio + (portfolio* perfMonth/100), 2),
                    "perfDay": round(( (current_price/open_price)*(usd_currentPrice/usd_yesterday_price) )*100  -100, 3),
                    "perfMonth": round(perfMonth, 2),
                })
            elif code == "INTEREST":
                url = "https://www.google.com/search?q=Turkey+interest+rate"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Arama sonucundaki faiz oranını içeren HTML etiketini bul
                interest_rate = float(soup.find('div', class_='IZ6rdc').text.replace('%',''))
                perfMonth = round(interest_rate/12, 2)
                result.append({
                    "ticker": types[i],
                    "price": round(portfolio + (portfolio* perfMonth/100), 2),
                    "perfDay": round(interest_rate/365,2),
                    "perfMonth": perfMonth,
                })
            else:
                info = info.basic_info
                perfMonth = round( (current_price/month_ago_price) * 100, 2) - 100
                perfDay = round( (info["lastPrice"] - info["open"])/info["open"] *100, 2)
                result.append({
                    "ticker": types[i],
                    "price": round(portfolio + (portfolio* perfMonth/100), 2),
                    "perfDay": round(perfDay,3),
                    "perfMonth": round(perfMonth, 2),
                })
            i += 1


        return jsonify({"message": result,
                        "isSuccessful": True})
    except Exception as e:
        return jsonify({"message": str(e),
                        "isSuccessful": False})


@app.route('/getMarketStocks',methods=['POST'])
@jwt_required()
def getMarketStocks():
    try:
        stockNames = request.get_json()
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            watchListOutput = list(executor.map(getWatchListStock, stockNames))

        return jsonify({"message": watchListOutput,
                        "isSuccessful": True})
    except Exception as e:
        return jsonify({"message": str(e),
                        "isSuccessful": False})


@app.route('/getAllBIST',methods=['GET'])
@jwt_required()
def getAllBIST():
    try:
        indexItems = getIndexItems()
        sectorIndices = getSectorIndices()

        stocks = stockNames()
        stocks.remove("ALTIN.IS") # Hisse statüsünde output gelmiyor
        stocksOutput = []

        # İş parçacıklarıyla hisse senedi bilgilerini al
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            stocksOutput = list(executor.map(getStockValue, stocks))

        stocksOutput = [stock for stock in stocksOutput if -10 <= stock['change'] <= 10]
        # `change` değerine göre sıralama
        stocksOutput_sorted = sorted(stocksOutput, key=lambda x: x['change'])

        output = {
            "topGainers": stocksOutput_sorted[-20:][::-1],
            "topLosers": stocksOutput_sorted[:20],
            "indices": sectorIndices,
            "indexItems": indexItems
        }

        return jsonify({"message": output,
                        "isSuccessful": True})
    except Exception as e:
        return jsonify({"message": str(e),
                        "isSuccessful": False})

@app.route('/stockSymbols',methods=['GET'])
@jwt_required()
def stockSymbols():
    try:
        return jsonify({"message": stockNames(),
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

@app.route('/getWatchList',methods=['GET'])
@jwt_required()
def getWatchList():
    try:
        user_email = get_jwt_identity()
        user = User.query.filter(User.email == user_email).first()
        watchListStocks = WatchListStocks.query.filter(WatchListStocks.userId == user.id).all()
        stock_names = [stock.stockName for stock in watchListStocks]
        
        print(stock_names)
        return jsonify({
            "message": stock_names,
            "isSuccessful": True,
        })
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False}) 

@app.route('/addWatchListStock',methods=['POST'])
@jwt_required()
def addWatchListStock():
    try:
        stockName = request.get_json()["stockName"]
        user_email = get_jwt_identity()
        user = User.query.filter(User.email == user_email).first()
        watchListStock = WatchListStocks(user = user, stockName = stockName)
        db.session.add(watchListStock)
        db.session.commit()

        return jsonify({
            "isSuccessful": True,
        })
    except Exception as e: 
        return jsonify({"message": str(e),
                       "isSuccessful": False}) 
    
@app.route('/removeWatchListStock',methods=['POST'])
@jwt_required()
def removeWatchListStock():
    try:
        stockName = request.get_json()["stockName"]
        user_email = get_jwt_identity()
        user = User.query.filter(User.email == user_email).first()
        watchListStock = WatchListStocks.query.filter(WatchListStocks.userId == user.id,WatchListStocks.stockName == stockName).first()
        db.session.delete(watchListStock)
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
    
    app.run(debug=False, host='0.0.0.0')

