from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pigeons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class PigeonPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pair_name = db.Column(db.String(100))
    egg_count = db.Column(db.Integer)
    hatch_date = db.Column(db.Date)
    treatment = db.Column(db.String(200))
    withdrawal_days = db.Column(db.Integer)
    successful_breeds = db.Column(db.Integer)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='اسم المستخدم موجود بالفعل')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='خطأ في اسم المستخدم أو كلمة المرور')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pairs = PigeonPair.query.all()
    today = datetime.today().date()
    return render_template('index.html', pairs=pairs, today=today)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        pair_name = request.form['pair_name']
        egg_count = int(request.form['egg_count'])
        hatch_days = int(request.form['hatch_days'])
        treatment = request.form['treatment']
        withdrawal_days = int(request.form['withdrawal_days'])
        successful_breeds = int(request.form['successful_breeds'])

        hatch_date = datetime.today().date() + timedelta(days=hatch_days)

        new_pair = PigeonPair(
            pair_name=pair_name,
            egg_count=egg_count,
            hatch_date=hatch_date,
            treatment=treatment,
            withdrawal_days=withdrawal_days,
            successful_breeds=successful_breeds
        )
        db.session.add(new_pair)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pair = PigeonPair.query.get(id)
    if request.method == 'POST':
        pair.pair_name = request.form['pair_name']
        pair.egg_count = int(request.form['egg_count'])
        hatch_days = int(request.form['hatch_days'])
        pair.hatch_date = datetime.today().date() + timedelta(days=hatch_days)
        pair.treatment = request.form['treatment']
        pair.withdrawal_days = int(request.form['withdrawal_days'])
        pair.successful_breeds = int(request.form['successful_breeds'])

        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', pair=pair)

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pair = PigeonPair.query.get(id)
    db.session.delete(pair)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
