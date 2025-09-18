# bank_project/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

db = SQLAlchemy()

def generate_account_number():
    """Generates a unique 6-digit account number."""
    while True:
        acc_num = random.randint(100000, 999999)
        # Check if the account number already exists in the database
        if not Account.query.filter_by(account_number=acc_num).first():
            return acc_num

class Account(db.Model):
    """Represents a user's bank account."""
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.Integer, unique=True, nullable=False, default=generate_account_number)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False) # In a real app, ALWAYS hash this!
    balance = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to transactions
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account {self.account_number} - {self.name}>"

class Transaction(db.Model):
    """Represents a single transaction."""
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'withdrawal'
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.type} of {self.amount} for account {self.account_id}>"