import os
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
from keras.models import load_model
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user data (replace with database)
users = {
    'admin': generate_password_hash('password'),
    'user1': generate_password_hash('password'),
    'user2': generate_password_hash('password')
}

def authenticate_user(username, password):
    if username in users and check_password_hash(users[username], password):
        return True
    return False

model = load_model('KIDNEY-Diseases (2).h5')
print('Model loaded. Check http://127.0.0.1:5000/')

def get_className(classNo):
    class_labels = ['Cyst', 'Normal', 'Stone', 'Tumor']
    return class_labels[classNo]

def getResult(img):
    image = cv2.imread(img)
    image = Image.fromarray(image, 'RGB')
    image = image.resize((244, 244))
    image = np.array(image)
    input_img = np.expand_dims(image, axis=0)
    result = model.predict(input_img)
    return np.argmax(result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            if check_password_hash(users[username], password):
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Invalid password')
        else:
            return render_template('login.html', error='Username does not exist. Please register.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = generate_password_hash(password)
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Username already exists')
    return render_template('register.html')

@app.route('/', methods=['GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/kidney_disease_description', methods=['GET'])
def kidney_disease_description():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('kidney_disease_description.html')

@app.route('/predict', methods=['GET'])
def predict_form():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    f = request.files['file']
    if f:
        basepath = os.path.dirname(__file__)
        uploads_dir = os.path.join(basepath, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, secure_filename(f.filename))
        f.save(file_path)
        value = getResult(file_path)
        result = get_className(value)
        return result

    return "Error"

if __name__ == '__main__':
    app.run(debug=True)
