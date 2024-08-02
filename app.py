from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import jwt
import datetime
import re

app = Flask(__name__)
CORS(app)  # Para permitir requisições de diferentes domínios

# Configuração do segredo para JWT
app.config['SECRET_KEY'] = 'GZpRA5eac1&kjf%w09^tBPKE'

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('barbearia.db')
    conn.row_factory = sqlite3.Row
    return conn

# Função para validar o formato do e-mail
def is_valid_email(email):
    email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email)

# Rota para registrar um novo usuário
@app.route('/api/register', methods=['POST'])
def register():
    new_user = request.get_json()

    nome = new_user.get('nome')
    email = new_user.get('email')
    senha = new_user.get('senha')

    # Verifica se algum campo está vazio
    if not nome or not email or not senha:
        return jsonify({'message': 'Todos os campos são obrigatórios!'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica se o e-mail já está registrado
    cursor.execute('SELECT * FROM usuario WHERE email = ?', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return jsonify({'message': 'O e-mail já está registrado!'}), 400

    # Se o e-mail não existe, insere o novo usuário
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
    auth = request.get_json()
    email = auth.get('email')
    senha = auth.get('senha')

    if not email or not senha:
        return jsonify({'message': 'Email e senha são obrigatórios!'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuario WHERE email = ? AND senha = ?', (email, senha))
    user = cursor.fetchone()
    conn.close()

    if user:
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token}), 200
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
