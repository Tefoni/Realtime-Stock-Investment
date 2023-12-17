from datetime import datetime
from time import timezone
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify,request

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),unique = True,nullable = False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(40))
    createDate = db.Column(db.DateTime(timezone = True), default= datetime.now())
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    def __repr__(self):
        return f'<User: Id({self.id}) Email({self.email}) Password({self.password}) Name({self.name}) CreateDate({self.createDate})>\n'    

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    closedPositionValue = db.Column(db.Float)
    createDate = db.Column(db.DateTime(timezone = True), default= datetime.now())
    stocks = db.relationship('Stocks', backref='portfolio', lazy=True)
    transactionHistories = db.relationship('TransactionHistory', backref='portfolio', lazy= True)
    def __repr__(self):
        return f'<Portfolio: Id({self.id}) UserId({self.userId}) ClosedPositionValue({self.closedPositionValue}) CreateDate({self.createDate})>\n'    

class Stocks(db.Model):
    def __init__(self, amount,average_cost,symbol, *args, **kwargs):
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Alınan hisse adedi pozitif tam sayı olmalıdır.")
        if average_cost <= 0:
            raise ValueError("Hisse fiyatı pozitif olmalıdır.")
        super().__init__(amount=amount,average_cost = average_cost,symbol= str.upper(symbol),*args, **kwargs)

    id = db.Column(db.Integer, primary_key=True)
    portfolioId = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    name = db.Column(db.String(100))
    symbol = db.Column(db.String(30))
    amount = db.Column(db.Integer)
    average_cost = db.Column(db.Float)
    createDate = db.Column(db.DateTime(timezone = True), default= datetime.now() )
    updateDate = db.Column(db.DateTime(timezone = True))
    transactionHistories = db.relationship('TransactionHistory', backref='stocks', lazy=True)


    def __repr__(self):
        return f'<Stock: Id({self.id}) PortfolioId({self.portfolioId}) Name({self.name}) Symbol({self.symbol}) Amount({self.amount}) Cost({self.average_cost}) CreateDate({self.createDate}) UpdateDate({self.updateDate})>\n'
    
class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stockId = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    amount = db.Column(db.Integer)
    price = db.Column(db.Float)
    portfolioId = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    createDate = db.Column(db.DateTime(timezone = True), default= datetime.now())
    transactionType = db.Column(db.Integer, nullable= False)
    def __repr__(self):
        self.type = "BUY" if self.transactionType == 1 else "SELL"
        return f'<Transaction: Id({self.id}) StockId({self.stockId}) Amount({self.amount}) Price({self.price}) PortfolioId({self.portfolioId}) CreateDate({self.createDate}) TransactionType({self.transactionType})>\n'
    
