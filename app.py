from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, History
import os
import webbrowser

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cipher.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Cipher Functions
def additive_encrypt(plain_text, key):
    encrypted_text = ""
    for char in plain_text:
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            encrypted_text += chr((ord(char) - offset + key) % 26 + offset)
        else:
            encrypted_text += char
    return encrypted_text

def additive_decrypt(encrypted_text, key):
    decrypted_text = ""
    for char in encrypted_text:
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            decrypted_text += chr((ord(char) - offset - key) % 26 + offset)
        else:
            decrypted_text += char
    return decrypted_text

def multiplicative_encrypt(plain_text, key):
    encrypted_text = ""
    for char in plain_text:
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            encrypted_text += chr(((ord(char) - offset) * key) % 26 + offset)
        else:
            encrypted_text += char
    return encrypted_text

def multiplicative_decrypt(encrypted_text, key):
    decrypted_text = ""
    mod_inverse = pow(key, -1, 26)
    for char in encrypted_text:
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            decrypted_text += chr(((ord(char) - offset) * mod_inverse) % 26 + offset)
        else:
            decrypted_text += char
    return decrypted_text

def affine_encrypt(plain_text, key1, key2):
    encrypted_text = ""
    for char in plain_text:
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            encrypted_text += chr(((ord(char) - offset) * key1 + key2) % 26 + offset)
        else:
            encrypted_text += char
    return encrypted_text

def affine_decrypt(encrypted_text, key1, key2):
    decrypted_text = ""
    mod_inverse = pow(key1, -1, 26)
    for char in encrypted_text:
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            decrypted_text += chr((mod_inverse * ((ord(char) - offset) - key2)) % 26 + offset)
        else:
            decrypted_text += char
    return decrypted_text

def monoalphabetic_encrypt(plain_text, key):
    encrypted_text = ""
    for char in plain_text:
        if char.isalpha():
            encrypted_text += key[ord(char.lower()) - 97] if char.islower() else key[ord(char.upper()) - 65].upper()
        else:
            encrypted_text += char
    return encrypted_text

def monoalphabetic_decrypt(encrypted_text, key):
    decrypted_text = ""
    reverse_key = {v: k for k, v in enumerate(key)}
    for char in encrypted_text:
        if char.isalpha():
            if char.islower():
                decrypted_text += chr(reverse_key[char] + 97)
            else:
                decrypted_text += chr(reverse_key[char.lower()] + 65).upper()
        else:
            decrypted_text += char
    return decrypted_text

def vigenere_encrypt(plain_text, key):
    encrypted_text = ""
    key_length = len(key)
    key_as_int = [ord(k.lower()) - 97 for k in key]
    for i, char in enumerate(plain_text):
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            key_char = key_as_int[i % key_length]
            encrypted_text += chr((ord(char) - offset + key_char) % 26 + offset)
        else:
            encrypted_text += char
    return encrypted_text

def vigenere_decrypt(encrypted_text, key):
    decrypted_text = ""
    key_length = len(key)
    key_as_int = [ord(k.lower()) - 97 for k in key]
    for i, char in enumerate(encrypted_text):
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            key_char = key_as_int[i % key_length]
            decrypted_text += chr((ord(char) - offset - key_char) % 26 + offset)
        else:
            decrypted_text += char
    return decrypted_text

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Use pbkdf2:sha256 hashing method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash("Invalid username or password!")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/cipher', methods=['POST'])
@login_required
def cipher():
    data = request.json
    cipher_type = data['cipher_type']
    operation = data['operation']
    text = data['text']
    key = data.get('key')
    key2 = data.get('key2')

    result = ""
    # Logic for selecting cipher function
    if cipher_type == "additive":
        if operation == "encrypt":
            result = additive_encrypt(text, int(key))
        else:
            result = additive_decrypt(text, int(key))
    elif cipher_type == "multiplicative":
        if operation == "encrypt":
            result = multiplicative_encrypt(text, int(key))
        else:
            result = multiplicative_decrypt(text, int(key))
    elif cipher_type == "affine":
        if operation == "encrypt":
            result = affine_encrypt(text, int(key), int(key2))
        else:
            result = affine_decrypt(text, int(key), int(key2))
    elif cipher_type == "monoalphabetic":
        if operation == "encrypt":
            result = monoalphabetic_encrypt(text, key)
        else:
            result = monoalphabetic_decrypt(text, key)
    elif cipher_type == "vigenere":
        if operation == "encrypt":
            result = vigenere_encrypt(text, key)
        else:
            result = vigenere_decrypt(text, key)

    # Save history to database
    new_history = History(user_id=current_user.id, cipher_type=cipher_type, operation=operation,
                          input_text=text, key=key, result=result)
    db.session.add(new_history)
    db.session.commit()

    return jsonify({"result": result})

@app.route('/history')
@login_required
def history():
    history_data = History.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', history=history_data)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    if not os.path.exists('cipher.db'):
        with app.app_context():
            db.create_all()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        open_browser()
    app.run(debug=True)
