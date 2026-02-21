from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from datetime import timedelta
from flask import url_for
import os




app = Flask(__name__)
app.secret_key = "secret123"

app.permanent_session_lifetime = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)



# Home Page
@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html' , username=session['username'])
    return redirect('/login')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
          flash("Username already exists ⚠️")
          return redirect('/register')


        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')



    return render_template('register.html')
    


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session.pop('user_id', None)
        session.pop('username', None)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session.permanent = True
            session['user_id'] = user.id
            session['username'] = user.username   

            return redirect(url_for('notes')) 

        else:
                flash("Invalid Username or Password ❌")
                return redirect('/login')
        
    return render_template('login.html')
    
        
    

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)   

    return redirect('/login')

#notes open
@app.route('/notes')
def notes():
    if 'user_id' not in session:
        return redirect('/login')

    notes_folder = os.path.join('static', 'notes')
    files = os.listdir(notes_folder)

    return render_template('notes.html',
                           username=session['username'],
                           files=files)




# check
@app.route('/check')
def check():
    users = User.query.all()
    result = ""
    for user in users:
        result += user.username + "<br>"
    return result


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
