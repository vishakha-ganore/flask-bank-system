# bank_project/app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Account, Transaction

app = Flask(__name__)

# --- CONFIGURATION ---
# Set a secret key for session management. CHANGE THIS in a real application.
app.config['SECRET_KEY'] = 'my-super-secret-key-that-no-one-should-know'
# Configure the database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# --- HELPER FUNCTION ---
def get_current_user():
    """Returns the Account object for the currently logged-in user."""
    if 'account_id' in session:
        return Account.query.get(session['account_id'])
    return None

# --- ROUTES ---
@app.route('/')
def index():
    """Homepage: shows login form or redirects to dashboard if already logged in."""
    if get_current_user():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password'] # IMPORTANT: In a real app, hash this password!
        initial_deposit = float(request.form.get('initial_deposit', 0))

        if initial_deposit < 0:
            flash('Initial deposit cannot be negative.', 'danger')
            return redirect(url_for('register'))

        # Create new account
        new_account = Account(name=name, password=password, balance=initial_deposit)
        db.session.add(new_account)
        db.session.commit()

        # Log initial deposit as a transaction if any
        if initial_deposit > 0:
            deposit_transaction = Transaction(account_id=new_account.id, type='deposit', amount=initial_deposit)
            db.session.add(deposit_transaction)
            db.session.commit()

        flash(f'Account created successfully! Your account number is {new_account.account_number}. Please log in.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    """Handles user login."""
    account_number = request.form['account_number']
    password = request.form['password']

    account = Account.query.filter_by(account_number=account_number).first()

    if account and account.password == password: # In a real app, use a password verification function
        session['account_id'] = account.id
        flash('Logged in successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid account number or password.', 'danger')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Displays the user's account dashboard."""
    user = get_current_user()
    if not user:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('index'))
    
    # Get all transactions for the user, ordered by most recent
    user_transactions = Transaction.query.filter_by(account_id=user.id).order_by(Transaction.timestamp.desc()).all()
    
    return render_template('dashboard.html', user=user, transactions=user_transactions)

@app.route('/transaction', methods=['POST'])
def handle_transaction():
    """Handles deposits and withdrawals."""
    user = get_current_user()
    if not user:
        return redirect(url_for('index'))

    amount = float(request.form['amount'])
    action = request.form['action']

    if amount <= 0:
        flash('Transaction amount must be positive.', 'danger')
        return redirect(url_for('dashboard'))

    if action == 'deposit':
        user.balance += amount
        transaction = Transaction(account_id=user.id, type='deposit', amount=amount)
        flash(f'Successfully deposited ${amount:.2f}.', 'success')
    elif action == 'withdraw':
        if amount > user.balance:
            flash('Insufficient funds for this withdrawal.', 'danger')
            return redirect(url_for('dashboard'))
        user.balance -= amount
        transaction = Transaction(account_id=user.id, type='withdrawal', amount=amount)
        flash(f'Successfully withdrew ${amount:.2f}.', 'success')
    else:
        flash('Invalid transaction type.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.add(transaction)
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('account_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create the database and tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)