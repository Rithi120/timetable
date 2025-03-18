from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Sample user data (this should be replaced with a database in production)
users = [
    {'username': 'user1', 'password': bcrypt.hashpw('password1'.encode('utf-8'), bcrypt.gensalt())},
    {'username': 'user2', 'password': bcrypt.hashpw('password2'.encode('utf-8'), bcrypt.gensalt())}
]

# User class for flask-login
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username)

# Function to read the to-do list from the JSON file
def load_todos():
    if os.path.exists('data/todos.json'):
        with open('data/todos.json', 'r') as f:
            return json.load(f)
    return []

# Function to save the to-do list to the JSON file
def save_todos(todos):
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/todos.json', 'w') as f:
        json.dump(todos, f)

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username), None)

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            user_obj = User(username)
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username already exists
        if any(u['username'] == username for u in users):
            flash('Username already exists')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Add new user to the users list (replace with a database in production)
        users.append({'username': username, 'password': hashed_password})

        flash('Registration successful, you can now log in')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route to fetch tasks
@app.route('/get_tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = load_todos()
    return jsonify(tasks), 200

# Route to add a task
@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    task = request.json
    tasks = load_todos()
    tasks.append(task)
    save_todos(tasks)
    return jsonify({"status": "success"}), 200

@app.route('/delete_task', methods=['POST'])
@login_required
def delete_task():
    task_text = request.json.get('text')  # Get the task text from the request
    tasks = load_todos()  # Load existing tasks
    tasks = [task for task in tasks if task['text'] != task_text]  # Remove the task
    save_todos(tasks)  # Save updated tasks back to the file
    return jsonify({"status": "success"}), 200

@app.route('/todo')
@login_required
def todo():
    return render_template('todo.html')

if __name__ == '__main__':
    app.run(debug=True)
