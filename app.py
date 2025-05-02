from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
import secrets
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Configure database (using SQLite for testing in Codespace)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///flaskapp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)

# Database models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # In production, use password hashing
    messages = db.relationship('Message', backref='user', lazy=True)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# Ensure database tables are created
with app.app_context():
    db.create_all()

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
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # In production, use password verification
            session['username'] = username
            session['user_id'] = user.id
            return redirect(url_for('chat'))
        elif not user:
            # Auto-register new users
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            session['user_id'] = new_user.id
            return redirect(url_for('chat'))
        else:
            error = "Invalid credentials. Please try again."
    
    return render_template('login.html', error=error)

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    # Get recent messages from database
    messages = Message.query.order_by(Message.timestamp).all()
    message_list = [{'user': msg.user.username, 'content': msg.content} for msg in messages]
    
    return render_template('chat.html', messages=message_list, current_user=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
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
    if 'username' in session and 'user_id' in session:
        # Save message to the database
        new_message = Message(
            content=data['content'],
            user_id=session['user_id']
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Broadcast the message
        message = {
            'user': session['username'],
            'content': data['content']
        }
        emit('receive_message', message, to='chat_room')

if __name__ == '__main__':
    socketio.run(app, debug=True)
