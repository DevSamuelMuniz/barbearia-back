from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import jwt
import datetime
import re

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Para permitir requisições de diferentes domínios

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
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'message': 'Token válido!', 'data': decoded_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expirado!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token inválido!'}), 401

    
    
# Rota de comunicação do procedimento com o frontend
@app.route('/api/procedimentos', methods=['POST'])
def add_procedimento():
    data = request.get_json()
    procedimento = data.get('procedimento')

    if not procedimento:
        return jsonify({'message': 'Procedimento é obrigatório!'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO procedimentos (procedimentos) VALUES (?)', (procedimento,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Procedimento adicionado com sucesso!'}), 201


@app.route('api/procedimentos', methods=['GET'])
def get_procedimentos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM procedimentos')
    procedimentos = cursor.fetchall()
    conn.cursor
    
    procedimentos_list = [{'id': row['id'], 'procedimento': row['procedimentos']} for row in procedimentos]
    return jsonify(procedimentos_list), 200

#agendamento
@app.route('/api/agendamento', methods=['POST'])
def add_agendamento():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados de entrada inválidos'}), 400

        nomeCliente = data.get('nomeCliente')
        nomeBarbeiro = data.get('nomeBarbeiro')
        horarioMarcado = data.get('horarioMarcado')

        if not nomeCliente or not nomeBarbeiro or not horarioMarcado:
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO agendamento (nomeCliente, nomeBarbeiro, horarioMarcado) VALUES (?, ?, ?)',
                       (nomeCliente, nomeBarbeiro, horarioMarcado))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Agendamento criado com sucesso'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agendamentos', methods=['GET'])
def get_agendamentos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nomeCliente, nomeBarbeiro, horarioMarcado FROM agendamento ORDER BY horarioMarcado ASC')
    agendamentos = cursor.fetchall()
    conn.commit()
    conn.close()

    agendamentos_list = [
        {"id": row["id"], "nomeCliente": row["nomeCliente"], "nomeBarbeiro": row["nomeBarbeiro"], "horarioMarcado": row["horarioMarcado"]}
        for row in agendamentos
    ]

    return jsonify(agendamentos_list)

@app.route('/api/addBarbeiro', methods=['POST'])
def add_barbeiro():
    data = request.get_json()

    nomeBarbeiro = data.get('nomeBarbeiro')
    cpf = data.get('cpf')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO barbeiro (nomeBarbeiro, cpf) VALUES (?, ?)',
                   (nomeBarbeiro, cpf))
    conn.commit()
    conn.close()

    return jsonify({"message": "Barbeiro adicionado com sucesso!"}), 201

@app.route('/api/barbeiros', methods=['GET'])
def barbeiros():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nomeBarbeiro FROM barbeiro')
    
    barbeiros = cursor.fetchall()
    conn.close()
    
    barbeiros_list = []
    for barbeiro in barbeiros:
        barbeiros_list.append({
            'id': barbeiro['id'],
            'nomeBarbeiro': barbeiro['nomeBarbeiro']
        })

    return jsonify(barbeiros_list), 200





if __name__ == '__main__':
    app.run(debug=True)
