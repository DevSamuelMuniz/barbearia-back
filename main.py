import sqlite3

conn = sqlite3.connect('barbearia.db')

cursor = conn.cursor()


# login
cursor.execute('''CREATE TABLE IF NOT EXISTS usuario
             (id INTEGER PRIMARY KEY, nome VARCHAR(100), email VARCHAR(150), senha Varchar(36))
               ''')
conn.commit()

# barbeiro
cursor.execute('''CREATE TABLE IF NOT EXISTS barbeiro
             (id INTEGER PRIMARY KEY, nomeBarbeiro VARCHAR(100), cpf Varchar(11))
               ''')
conn.commit()

# agendamento
cursor.execute('''CREATE TABLE IF NOT EXISTS agendamento
             (id INTEGER PRIMARY KEY, nomeCliente VARCHAR(100), nomeBarbeiro VARCHAR(150), horarioMarcado DATETIME)
               ''')
conn.commit()

# procedimentos
cursor.execute('''CREATE TABLE IF NOT EXISTS procedimentos
             (id INTEGER PRIMARY KEY, procedimento VARCHAR(100), valor VARCHAR(10))
               ''')
conn.commit()

# atendimento
cursor.execute('''CREATE TABLE IF NOT EXISTS atendimento
               (id INTEGER PRIMARY KEY, 
               nomeCliente VARCHAR(100),
               nomeBarbeiro VARCHAR(100),
               horarioMarcado DATETIME,
               procedimentos TEXT,
               valorTotal DECIMAL(10, 2))
              ''')
conn.commit()

# horários disponiveis pelo barbeiro
cursor.execute('''
        CREATE TABLE IF NOT EXISTS horarios_disponiveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomeBarbeiro TEXT NOT NULL,
            horario TEXT NOT NULL,
            disponivel BOOLEAN NOT NULL
        )
    ''')
    
conn.commit()

# dados cliente direto sem login
cursor.execute('''
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT NOT NULL,
        nome_barbeiro TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        horario_id INTEGER NOT NULL,
        FOREIGN KEY (horario_id) REFERENCES horarios_disponiveis(id)
    )
''')

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()