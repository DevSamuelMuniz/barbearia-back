from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import jwt
import datetime

app = Flask(__name__)
CORS(app)  # Para permitir requisições de diferentes domínios

# Configuração do segredo para JWT
SECRET_KEY = 'GZpRA5eac1&kjf%w09^tBPKE'

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('barbearia.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rota para registrar um novo usuário
@app.route('/api/register', methods=['POST'])
def register():
    new_user = request.get_json()

    nome = new_user['nome']
    email = new_user['email']
    senha = new_user['senha']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)',
        (nome, email, senha)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Usuário registrado com sucesso!'}), 201

# Rota para login do usuário
@app.route('/api/login', methods=['POST'])
def login():
    credentials = request.get_json()

    email = credentials['email']
    senha = credentials['senha']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM usuario WHERE email = ? AND senha = ?',
        (email, senha)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        # Gerar token JWT
        token = jwt.encode({
            'id': user['id'],
            'nome': user['nome'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'message': 'Login bem-sucedido!', 'token': token}), 200
    else:
        return jsonify({'message': 'Credenciais inválidas!'}), 401

# Rota para verificar o token (opcional)
@app.route('/api/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token é necessário!'}), 403

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'message': 'Token válido!', 'data': decoded_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expirado!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token inválido!'}), 401

if __name__ == '__main__':
    app.run(debug=True)
