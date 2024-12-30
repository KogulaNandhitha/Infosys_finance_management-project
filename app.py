import smtplib
import ssl
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
from flask import Flask, render_template

# Flask app setup
app = Flask(__name__)
app.secret_key = 'kogula'  # Replace with a strong secret key

# MySQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:kogula@localhost/transaction_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_USERNAME'] = 'nandhithakogula@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'cbbmqbsvtgttpunu'  # Replace with your email password
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True

# Initialize SQLAlchemy
# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Add this field

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(150), nullable=False)  # Column name must match
    initial_amount = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_balance = db.Column(db.Float, nullable=False)  # Add this to store the current balance
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    def __repr__(self):
        return f'<Goal {self.description}, Target: {self.target_amount}, Balance: {self.current_balance}>'
@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('Please login first.', 'danger')
        return redirect('/login')

    # Retrieve user details
    user_id = session['user_id']
    user = User.query.get(user_id)  # Assuming you have a `User` model and `user_id` matches its primary key
    account = Account.query.filter_by(user_id=user_id).first()

    # Retrieve goals for the user
    goals = Goal.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        description = request.form['description']
        target_amount = float(request.form['target_amount'])

       
        if  target_amount <= account.balance:
            # Send email notification to user
            user_email = user.email
            subject = "Goal is achived"
            body = f"Hello,\n\nYou have set a goal with a target amount of ${target_amount:.2f}, which is leser than or equal to your current account balance of ${account.balance:.2f}.\nCongrats for achivement.\n\nRegards,\nYour App Team"
            send_email(user_email, subject, body)
          
            # Flash a message indicating the user was notified
            flash(f"Goal is achived", 'warning')

        # Create and save a new goal
        new_goal = Goal(description=description, target_amount=target_amount, current_balance=account.balance, user_id=user_id)
        db.session.add(new_goal)
        db.session.commit()

        flash('Goal added successfully!', 'success')
       
        return redirect('/add_goal')
    
    # Pass user details and goals to the template
    return render_template('add_goal.html', user=user, goals=goals)



# Function to send email
def send_email(user_email, subject, body):
    """
    Sends an email to the specified user email address.

    Parameters:
        user_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.
    """
    # Define email sender credentials
    email_sender = app.config['MAIL_USERNAME']
    email_password = app.config['MAIL_PASSWORD']

    # Create the email
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = user_email
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    try:
        with smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'], context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, user_email, em.as_string())
        print(f"Email sent successfully to {user_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
import matplotlib.pyplot as plt



# Example: Call this function when a user adds a bill
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created

    # Example usage
   
    subject = "You have Been logged in"
    body = """
    Hello,

     If you have any questions, please reach out to support.

    Thank you for using our service!

    Regards,
    Your App Team
    """

    
@app.route('/transaction-data')
def transaction_data():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 403

    user_id = session['user_id']

    # Calculate total added and debited amounts
    account = Account.query.filter_by(user_id=user_id).first()
    total_added = account.initial_amount + sum(b.amount for b in Bill.query.filter_by(user_id=user_id))
    total_debited = sum(b.amount for b in Bill.query.filter_by(user_id=user_id))

    return jsonify({
        'status': 'success',
        'data': {
            'added': total_added,
            'debited': total_debited
        }
    })



# Route to add account
# @app.route('/add-amount', methods=['POST'])
# def add_account():
#     try:
#         account_name = request.form['account_name']  # Check this matches your form field name
#         balance = float(request.form['balance'])     # Ensure the form includes 'balance'
        
#         # Add account logic here (e.g., saving to the database)
#         new_account = Account(account_name=account_name, balance=balance)
#         db.session.add(new_account)
#         db.session.commit()

#         return redirect(url_for('add-amount'))

#     except KeyError as e:
#         return f"Missing field: {str(e)}", 400

# Routes
# @app.route('/profile')
# def view_accounts():
#     if 'user_id' not in session:
#         flash('Please login first.', 'danger')
#         return redirect('/login')

#     user_id = session['user_id']
#     accounts = Account.query.filter_by(user_id=user_id).all()
#     return render_template('profile.html', accounts=accounts)
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect('/register')

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['notifications'] = []  # Initialize notifications
            user_email = user.email
            subject = "You have Been logged in"
            body = "You are logged in"
                # to_email = user.email  # Ensure the 'email' field exists in your User model
                # subject = f'New Bill Added: {description}'
                # body = f'Hello {user.username},\n\nA new bill has been added.\n\nDescription: {description}\nAmount: {amount}\n\nRegards,\nTransaction System'
            send_email(user_email, subject, body)
            flash('Login successful!', 'success')
           
            return redirect('/dashboard')
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect('/login')
    # user_email = "kogulanandhitha9924@gmail.com"
    # subject = "You have Been logged in"
    # body = "hi"
    #             # to_email = user.email  # Ensure the 'email' field exists in your User model
    #             # subject = f'New Bill Added: {description}'
    #             # body = f'Hello {user.username},\n\nA new bill has been added.\n\nDescription: {description}\nAmount: {amount}\n\nRegards,\nTransaction System'
    # send_email(user_email, subject, body)
    return render_template('login.html')

@app.route('/add-amount', methods=['GET', 'POST'])
def add_amount():
    if 'user_id' not in session:
        flash('Please login first.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    user = User.query.get(user_id)
    bills = Bill.query.filter_by(user_id=user_id).all()
    notifications = session.get('notifications', [])
    account = Account.query.filter_by(user_id=user_id).first()  # Fetch user's account
    goals = Goal.query.filter_by(user_id=user_id).all()  # Fetch user's goals

    if request.method == 'POST':
        try:
            # Retrieve and validate the amount from the form
            added_amount = float(request.form['amount'])
            
            if not account:
                flash('No account found. Please create an account first.', 'danger')
                return redirect('/dashboard')

            # Update account balance
            account.balance += added_amount
            db.session.commit()

            # Update goals
            for goal in goals:
                if goal.status == 'Progress':  # Update only in-progress goals
                    goal.current_balance = account.balance

                    # Check if the goal is achieved
                    if goal.current_balance >= goal.target_amount:
                        goal.status = 'Achieved'
                        
            # Send email notification to user
                        user_email = user.email
                        subject = "Goal is achived"
                        body = f"Hello,\n\nYou have achived  your goal.\nCongrats for achivement.\n\nRegards,\nYour App Team"
                        send_email(user_email, subject, body)
          
            # Flash a message indicating the user was notified
         

                        flash(f'Congratulations! Goal "{goal.description}" has been achieved!', 'success')
             
            db.session.commit()
            flash(f'Amount ${added_amount:.2f} added successfully!', 'success')

        except ValueError:
            flash('Invalid amount entered. Please try again.', 'danger')

    return render_template('add-amount.html', user=user, bills=bills, notifications=notifications)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first.', 'danger')
        return redirect('/login')
    
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    bills = Bill.query.filter_by(user_id=user_id).all()
    notifications = session.get('notifications', [])
    goals = Goal.query.filter_by(user_id=user_id).all()
    account = Account.query.filter_by(user_id=user_id).first()  # Fetch the user's account

    balance = account.balance if account else 0.0  # Default to 0.0 if no account exists
    
    return render_template(
        'dashboard.html',
        user=user,
        bills=bills,
        notifications=notifications,
        goals=goals,
        balance=balance
    )

@app.route('/add-bill', methods=['POST'])
def add_bill():
    if 'user_id' not in session:
        flash('Please login first.', 'danger')
        return redirect('/login')

    try:
        # Fetch form data
        description = request.form['description']
        amount = float(request.form['amount'])
        user_id = session['user_id']
       
        user = User.query.get(user_id)
        user_email = user.email
        subject = "Bills"
            # body = "Your bill added"
            # to_email = user.email  # Ensure the 'email' field exists in your User model
            # subject = f'New Bill Added: {description}'
        body = f'Hello {user.username},\n\nA new bill has been added.\n\nDescription: {description}\nAmount: {amount}\n\nRegards,\nTransaction System'
        send_email(user_email, subject, body)
        flash('Bill added successfully!', 'success')
        # Identify the default account for the user
        account = Account.query.filter_by(user_id=user_id).first()
        if not account:
            flash('No account exists for this user. Please add an account first.', 'danger')
            return redirect('/dashboard')

        # Check for sufficient balance
        if account.balance < amount:
            flash('Insufficient balance in the account.', 'danger')
            return redirect('/dashboard')

        # Deduct from account balance
        account.balance -= amount

        # Add the bill
        new_bill = Bill(description=description, amount=amount, user_id=user_id)
        db.session.add(new_bill)
        db.session.commit()
        send_email(user_email, subject, body)
        flash('Bill added and account balance updated successfully!', 'success')
        goals = Goal.query.filter_by(user_id=user_id).all()
        for goal in goals:
            goal.current_balance = account.balance

        # Add the bill
        new_bill = Bill(description=description, amount=amount, user_id=user_id)
        db.session.add(new_bill)
        db.session.commit()

        send_email(user_email, subject, body)
        flash('Bill added and account balance updated successfully!', 'success')

        return redirect('/dashboard')

    except (KeyError, ValueError) as e:
        flash('Invalid form data. Please try again.', 'danger')
        return redirect('/dashboard')
       

    except (KeyError, ValueError) as e:
        flash('Invalid form data. Please try again.', 'danger')
        return redirect('/dashboard')



@app.route('/delete-bill/<int:bill_id>')
def delete_bill(bill_id):
    if 'user_id' not in session:
        flash('Please login first.', 'danger')
        return redirect('/login')

    bill = Bill.query.get(bill_id)
    if bill and bill.user_id == session['user_id']:
        db.session.delete(bill)
        db.session.commit()

        # Add notification
        notification = f"Bill '{bill.description}' of amount {bill.amount} deleted."
        session.setdefault('notifications', []).append(notification)

        # Send email after transaction
        user = User.query.get(bill.user_id)
        user_email = user.email
        subject = "Bills deleted"
        # body = "Your bill added"
        # to_email = user.email  # Ensure the 'email' field exists in your User model
        # subject = f'New Bill Added: {description}'
        body ="Your Bill has been deleted"
        send_email(user_email, subject, body)

        flash('Bill deleted successfully!', 'success')
    else:
        flash('You are not authorized to delete this bill.', 'danger')
    return redirect('/dashboard')

@app.route('/notifications', methods=['GET'])
def notifications():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 403

    notifications = session.get('notifications', [])
    return jsonify({'status': 'success', 'notifications': notifications})

@app.route('/clear-notifications', methods=['POST'])
def clear_notifications():
    if 'user_id' in session:
        session['notifications'] = []
        return jsonify({'status': 'success', 'message': 'Notifications cleared'})
    return jsonify({'status': 'error', 'message': 'Not logged in'}), 403

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("Please login to continue.", "danger")
        return redirect('/login')

    user_id = session['user_id']
    user = User.query.get(user_id)
    accounts = Account.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()  
    if request.method == 'POST':
        if 'account_name' in request.form and 'initial_amount' in request.form:
            # Add New Account
            if accounts:  # Prevent adding multiple accounts
                flash("You already have an account!", "info")
                return redirect('/profile')

            account_name = request.form['account_name']
            initial_amount = float(request.form['initial_amount'])

            # Create and save new account
            new_account = Account(
                user_id=user_id,
                account_name=account_name,
                initial_amount=initial_amount,
                balance=initial_amount
            )
            db.session.add(new_account)
           
            db.session.commit()
            flash("Account added successfully!", "success")
        
        elif 'amount' in request.form:
            # Add Amount to Existing Account
            if not accounts:
                flash("No account found. Please add an account first.", "warning")
                return redirect('/profile')
            try:
                amount_to_add = float(request.form['amount'])
                if amount_to_add <= 0:
                    flash("Amount must be greater than zero.", "danger")
                else:
                    # Add amount to the first user's account
                    account = accounts[0]
                    account.balance += amount_to_add
                    goals = Goal.query.filter_by(user_id=user_id).all()
                    for goal in goals:
                         goal.current_balance = account.balance
                         if goal.current_balance >= goal.target_amount:
                                
                        
            # Send email notification to user
                                user_email = user.email
                                subject = "Goal is achived"
                                body = f"Hello,\n\nYou have achived  your goal.\nCongrats for achivement.\n\nRegards,\nYour App Team"
                                send_email(user_email, subject, body)
                    db.session.commit()
                    flash(f"${amount_to_add:.2f} has been added to your account!", "success")
            except ValueError:
                flash("Invalid amount entered.", "danger")
        
        return redirect('/profile')

    return render_template('profile.html', accounts=accounts)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('notifications', None)  # Clear notifications on logout
    flash('Logged out successfully!', 'success')
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
