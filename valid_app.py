from flask import Flask, render_template, request, flash, redirect, url_for, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required, UserMixin, LoginManager
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
import os
import json
 


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150), nullable=False)
    correct = db.Column(db.Integer())
    incorrect_times = db.Column(db.Integer())
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(150), nullable=False)

@app.route('/home')
@login_required
def home():
    return render_template('index.html', user=current_user)

@app.route('/about')
@login_required
def about():
    return render_template('about.html', user=current_user)

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html', user=current_user)

@app.route('/problems')
@login_required
def problems():
    return render_template('problems.html', user=current_user)


# LOGIN AND SIGN UP
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template('login.html', user=current_user)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password')
        password2 = request.form.get('confirm_password')
        country = request.form.get('country')
        username = request.form.get('username')
        user = User.query.filter_by(email=email).first()
        usernamee = User.query.filter_by(username=username).first()
        if user:
            flash('Email is already in use', category='error')
        if usernamee:
            flash('Username is already in use', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(firstName) < 2:
            flash('First Name must be greater than 2 characters', category='error')
        elif len(lastName) < 2:
            flash('Last Name must be greater than 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 6:
            flash('Password must be more than 6 characters', category='error')
        else:
            flash('Works! Logged in!', category='success')
            new_user = User(username=username, password=generate_password_hash(password1, method = "sha256"), email=email, country=country, first_name=firstName, last_name=lastName, correct=0, incorrect_times=0)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('home'))
            

    return render_template('signup.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user/<string:Usernamee>', methods = ['POST','GET'])
@login_required
def username(Usernamee):
    usernamee = current_user.query.filter_by(username=Usernamee).first()
    event = User.query.filter().all()
    if usernamee:
        return render_template("user_hub.html", user=current_user, username=Usernamee, User=event)
    else:
        return render_template('user_not_exists.html')

# POINT SYSTEM
@app.route('/point', methods=['POST'])
def point():
    user = current_user
    req = request.get_json() # dictionary
    print(req) # print json response
    if req['point'] == '5':
        print(req['point'] + ' correct')
        user.correct = user.correct + 1
        db.session.commit()
    else:
        user.incorrect_times = user.incorrect_times + 1
        db.session.commit()
        print('Incorrect')

    res = make_response(jsonify({"messsage":"JSON"}), 200)
    return res



# INVALID URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_not_found.html'), 404
# INVALID SERVER ERROR
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
if __name__ == '__main__':
    db.create_all()
    app.run()
