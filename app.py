from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
socketio = SocketIO(app)

# Storing messages in memory for demo purposes
# In a real app, you would use a database
messages = []
users = {}  # Store usernames and passwords for demo

@app.route('/')
def home():
    return render_template('index.html', title='Flask Chat App')

@app.route('/about')
def about():
    return "<h1>About Flask</h1><p>Flask is a micro web framework written in Python. It is designed to be simple and easy to use, making it ideal for small applications and quick prototypes.</p>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple authentication for demo purposes
        # In a real app, you would check against a database and hash passwords
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('chat'))
        elif username not in users:
            # Auto-register new users for the demo
            users[username] = password
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            error = "Invalid credentials. Please try again."
    
    return render_template('login.html', error=error)

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', messages=messages, current_user=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        join_room('chat_room')
        emit('user_joined', {'user': session['username']}, to='chat_room')

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session:
        leave_room('chat_room')

@socketio.on('send_message')
def handle_message(data):
    if 'username' in session:
        message = {
            'user': session['username'],
            'content': data['content']
        }
        messages.append(message)
        emit('receive_message', message, to='chat_room')

if __name__ == '__main__':
    socketio.run(app, debug=True)
