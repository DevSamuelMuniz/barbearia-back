from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import jwt
import json
import datetime
import re
from datetime import datetime, timedelta, timezone

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
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)

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
    valor = data.get('valor')

    if not procedimento:
        return jsonify({'message': 'Procedimento é obrigatório!'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO procedimentos (procedimento, valor) VALUES (?,?)', (procedimento, valor,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Procedimento adicionado com sucesso!'}), 201


@app.route('/api/procedimentos-get', methods=['GET'])
def get_procedimentos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, procedimento, valor FROM procedimentos')  # Ajuste o nome da coluna para corresponder ao seu banco de dados
    procedimentos = cursor.fetchall()
    conn.close()
    
    procedimentos_list = []
    for procedimento in procedimentos:
        procedimentos_list.append(
            {
                'id': procedimento['id'], 
                'procedimento': procedimento['procedimento'],
                'valor': procedimento['valor']
            }
        )
    return jsonify(procedimentos_list), 200

# configuração para armazenar os dados do modal
@app.route('/api/store-procedimentos', methods=['POST'])
def store_procedimentos():
    data = request.get_json()
    
    nomeCliente = data.get('nomeCliente')
    nomeBarbeiro = data.get('nomeBarbeiro')
    horarioMarcado = data.get('horarioMarcado')
    procedimentos_selecionados = data.get('procedimentos')
    valor_total = data.get('total')

    procedimentos_json = json.dumps(procedimentos_selecionados)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO atendimento (nomeCliente, nomeBarbeiro, horarioMarcado, procedimentos, valorTotal)
        VALUES (?, ?, ?, ?, ?)
    ''', (nomeCliente, nomeBarbeiro, horarioMarcado, procedimentos_json, valor_total))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Atendimento armazenado com sucesso!"}), 201


#Configuração para excluir os dados ao finalizar o modal
@app.route('/api/delete-agendamento/<int:agendamento_id>', methods=['DELETE'])
def delete_agendamento(agendamento_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM agendamento WHERE id = ?', (agendamento_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Agendamento excluído com sucesso!"}), 200


#Financeiro
@app.route('/api/financeiros', methods=['GET'])
def get_financeiro():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nomeCliente, nomeBarbeiro, horarioMarcado, valorTotal FROM atendimento')
    financeiros = cursor.fetchall()
    conn.close()

    financeiro_list = []
    for financeiro in financeiros:
        try:
            # Tenta converter o horário para o formato desejado
            horario_formatado = datetime.strptime(financeiro['horarioMarcado'], '%Y-%m-%dT%H:%M:%S').strftime('%d/%m/%Y %H:%M')
        except ValueError:
            # Se já estiver no formato correto, mantém como está
            horario_formatado = financeiro['horarioMarcado']
        
        financeiro_list.append(
            {
                'id': financeiro['id'],
                'nomeCliente': financeiro['nomeCliente'],
                'nomeBarbeiro': financeiro['nomeBarbeiro'],
                'horarioMarcado': horario_formatado,
                'valorTotal': financeiro['valorTotal']
            }
        )
    return jsonify(financeiro_list), 200



from datetime import datetime

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

        # Converter o horário marcado para o formato DD/MM/YYYY HH:MM
        horarioMarcado = datetime.strptime(horarioMarcado, '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M')

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




#retono dos filtros
@app.route('/api/get-date-financeiro', methods=['GET'])
def filtro_data_financeiro():
    date = request.args.get('date')
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ajuste a consulta conforme necessário
    cursor.execute('SELECT * FROM atendimento WHERE horarioMarcado LIKE ?', (f'{date}%',))
    rows = cursor.fetchall()
    conn.close()
    
    data = [dict(row) for row in rows]
    return jsonify(data)


@app.route('/api/get-date-agendamento', methods=['GET'])
def filtro_data_agendamento():
    date = request.args.get('date')
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ajuste a consulta conforme necessário
    cursor.execute('SELECT * FROM agendamento WHERE horarioMarcado LIKE ?', (f'{date}%',))
    rows = cursor.fetchall()
    conn.close()
    
    data = [dict(row) for row in rows]
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
