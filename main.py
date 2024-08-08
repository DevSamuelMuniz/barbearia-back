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

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()