from flask import Flask, render_template, request, jsonify
import webbrowser
import os

app = Flask(__name__)

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
def index():
    return render_template('index.html')

@app.route('/cipher', methods=['POST'])
def cipher():
    data = request.json
    cipher_type = data['cipher_type']
    operation = data['operation']
    text = data['text']
    key = data.get('key')
    key2 = data.get('key2')
    result = ""

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

    return jsonify({"result": result})

def open_browser():
    """Open the default web browser to the application URL."""
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        open_browser()
    app.run(debug=True)
