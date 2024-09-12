# bd-create.py

import sqlite3
import pandas as pd

# Função para criar e popular o banco de dados
def create_database():
    conn = sqlite3.connect('impressoras.db')
    cursor = conn.cursor()

    # Criar tabela de impressoras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS impressoras (
            serie TEXT PRIMARY KEY,
            modelo TEXT,
            marca TEXT,
            setor TEXT,
            conexao TEXT
        )
    ''')

    # Criar tabela de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            hora TEXT,
            serie TEXT,
            contador TEXT,
            peca TEXT,
            FOREIGN KEY (serie) REFERENCES impressoras(serie)
        )
    ''')

    # Carregar dados do Excel e inserir na tabela de impressoras
    df = pd.read_excel('impressoras.xlsx')
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT OR IGNORE INTO impressoras (serie, modelo, marca, setor, conexao)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['Série'], row['Modelo'], row['Marca'], row['Setor'], row['Conexão']))

    conn.commit()
    conn.close()
    print("Banco de dados criado e populado com sucesso.")

if __name__ == '__main__':
    create_database()
