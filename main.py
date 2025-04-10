import os,datetime,jwt,bcrypt

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

client = MongoClient(os.getenv('MONGO_URL'))
db = client["School"]
users = db["users"]

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol')

    if users.find_one({"username": username}):
        return jsonify({"error": "El usuario ya existe"}), 409

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed_pw,"rol":rol})
    return jsonify({"message": "Usuario registrado con éxito"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = users.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"message":"ok","token": token})

    return jsonify({"error": "Credenciales inválidas"}), 401


@app.route('/perfil', methods=['GET'])
def perfil():
    return jsonify({"message": "Ruta protegida (no autenticada aún, solo ejemplo)"})

if __name__ == '__main__':
    app.run(debug=True)
