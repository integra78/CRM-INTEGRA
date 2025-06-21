from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp

app = Flask(__name__)
app.secret_key = 'CHANGE_ME'

# In-memory stores
users = {}
tasks = []
clients = []
projects = []


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        otp_secret = pyotp.random_base32()
        users[username] = {
            'email': email,
            'password': password,
            'otp_secret': otp_secret,
            'tasks': [],
            'clients': [],
            'projects': []
        }
        flash(f"OTP Secret (store in authenticator app): {otp_secret}")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        otp = request.form['otp']
        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            totp = pyotp.TOTP(user['otp_secret'])
            if totp.verify(otp):
                session['user'] = username
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid OTP')
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = users[username]
    return render_template('dashboard.html', user=username, tasks=user['tasks'], clients=user['clients'], projects=user['projects'])


@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = users[username]
    return render_template('profile.html', user=username, email=user['email'])


@app.route('/tasks', methods=['GET', 'POST'])
def manage_tasks():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = users[username]
    if request.method == 'POST':
        task = request.form['task']
        user['tasks'].append({'task': task, 'status': 'pending'})
    return render_template('tasks.html', tasks=user['tasks'])


@app.route('/clients', methods=['GET', 'POST'])
def manage_clients():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = users[username]
    if request.method == 'POST':
        client = request.form['client']
        user['clients'].append({'name': client})
    return render_template('clients.html', clients=user['clients'])


@app.route('/projects', methods=['GET', 'POST'])
def manage_projects():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = users[username]
    if request.method == 'POST':
        project = request.form['project']
        user['projects'].append({'name': project})
    return render_template('projects.html', projects=user['projects'])


@app.route('/reports')
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = users[username]
    return render_template('reports.html', tasks=user['tasks'], projects=user['projects'], clients=user['clients'])


if __name__ == '__main__':
    app.run(debug=True)
