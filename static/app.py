from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['user_auth_db']
users_collection = db['users']

@app.route('/')
def home():
    """Redirect authenticated users to the profile page, else show the login page."""
    if 'username' in session:
        return redirect(url_for('index'))  # Change to redirect to index
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))  # Change to redirect to index
        
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        if users_collection.find_one({'username': username}):
            return render_template('register.html', error='Username already exists')
        
        # Hash password and store user
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            'username': username,
            'password': hashed_password
        })
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/index')
def index():
    """Display user profile."""
    if 'username' not in session:
        return redirect(url_for('home'))
    
    user = users_collection.find_one({'username': session['username']})
    
    # Profile data
    profile_data = {
        'name': user['username'],
        'title': 'Software Developer',
        'about': 'Hello! I\'m a passionate software developer with interest in web development and technology.',
        'skills': ['Python', 'Flask', 'HTML', 'CSS', 'JavaScript']
    }
    
    return render_template('index.html', profile=profile_data)  # Render index.html

@app.route('/logout')
def logout():
    """Log the user out."""
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
