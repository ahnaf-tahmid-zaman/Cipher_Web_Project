from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Cipher Functions (Reusing the same logic from before)
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
    # Add other ciphers here as needed

    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
