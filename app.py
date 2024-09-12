from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import inspect, text
import sqlite3
import smtplib
import logging
import os
from email.mime.text import MIMEText

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar 'flash' para mensagens

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///impressoras.db'  # Usando SQLite como exemplo
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definindo o modelo da tabela Impressoras
class Impressora(db.Model):
    __tablename__ = 'impressoras'
    serie = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)  # Define a série como chave primária
    modelo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    setor = db.Column(db.String(100), nullable=True)
    conexao = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'serie': self.serie,
            'modelo': self.modelo,
            'marca': self.marca,
            'setor': self.setor,
            'conexao': self.conexao
        }

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(8), nullable=False)
    serie = db.Column(db.String(50), db.ForeignKey('impressoras.serie'), nullable=False)  # Corrigido para 'impressoras'
    contador = db.Column(db.String(50), nullable=False)
    peca = db.Column(db.String(100), nullable=False)

# Configurações do Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'skyennonet@gmail.com'
EMAIL_PASSWORD = 'uhqq rkjt simc rker'
EMAIL_DESTINATARIO = 'fcezariomoura@gmail.com'

# Função para enviar e-mail
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        print("Email enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# Rotas
@app.route('/test_sqlalchemy')
def test_sqlalchemy():
    try:
        # Testando uma consulta simples usando SQLAlchemy
        impressoras = Impressora.query.limit(5).all()

        if impressoras:
            # Exibindo os dados
            data = [f"{imp.serie} - {imp.modelo} - {imp.marca} - {imp.setor} - {imp.conexao}" for imp in impressoras]
            return f"Dados retornados: {', '.join(data)}"
        else:
            return "Nenhum dado foi encontrado na tabela 'impressoras'."
    except Exception as e:
        return str(e)

@app.route('/test_db')
def test_db():
    try:
        # Verifica diretamente a tabela impressoras
        result = db.session.execute(text('SELECT * FROM impressoras'))
        rows = [dict(row) for row in result]

        if rows:
            return f"Dados encontrados: {rows}"
        else:
            return "Nenhum dado encontrado na tabela 'impressoras'."
    except Exception as e:
        return str(e)

@app.route('/test_select')
def test_select():
    try:
        conn = sqlite3.connect('impressoras.db')  # Ajuste o caminho se necessário
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM impressoras LIMIT 5")  # Pega as primeiras 5 linhas
        rows = cursor.fetchall()

        if rows:
            return f"Dados retornados: {rows}"
        else:
            return "Nenhum dado foi encontrado na tabela 'impressoras'."
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    try:
        # Carrega todas as impressoras do banco de dados
        impressoras = Impressora.query.all()
        
        if not impressoras:
            logging.warning("Nenhuma impressora encontrada no banco de dados.")

        # Verifica se há impressoras carregadas como None
        impressoras_validas = [i for i in impressoras if i is not None]
        
        # Log de impressoras carregadas
        logging.info(f"Total de impressoras carregadas: {len(impressoras_validas)}")

        for impressora in impressoras_validas:
            logging.info(f"Impressora série: {impressora.serie}, modelo: {impressora.modelo}")

        # Captura o valor da pesquisa, se houver
        search_query = request.args.get('search', '').strip()

        if search_query:
            # Filtra as impressoras com base na pesquisa
            impressoras_validas = Impressora.query.filter(
                (Impressora.serie.ilike(f'%{search_query}%')) |
                (Impressora.modelo.ilike(f'%{search_query}%')) |
                (Impressora.marca.ilike(f'%{search_query}%')) |
                (Impressora.setor.ilike(f'%{search_query}%')) |
                (Impressora.conexao.ilike(f'%{search_query}%'))
            ).all()
            logging.info(f"Impressoras filtradas pela pesquisa '{search_query}': {[i.serie for i in impressoras_validas]}")

        # Retorna a página index com os dados das impressoras válidas
        return render_template('index.html', data=impressoras_validas)

    except Exception as e:
        # Loga o erro e mostra uma mensagem amigável
        logging.error(f"Erro ao carregar impressoras na rota home: {e}")
        return f"Ocorreu um erro ao carregar a página inicial: {e}"

@app.route('/impressora/<serie>', methods=['GET', 'POST'])
def impressora_profile(serie):
    impressora = Impressora.query.filter_by(serie=serie).first()

    if impressora is None:
        flash(f"Impressora com série {serie} não encontrada.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'request_parts' in request.form:
            contador = request.form.get('contador')
            peca = request.form.get('peca')

            novo_pedido = Pedido(
                data=datetime.now().strftime('%Y-%m-%d'),
                hora=datetime.now().strftime('%H:%M:%S'),
                serie=impressora.serie,
                contador=contador,
                peca=peca
            )
            db.session.add(novo_pedido)
            db.session.commit()

            body = f"Solicito o seguinte material para o equipamento abaixo:\n\n" \
                f"Série: {impressora.serie}\n" \
                f"Modelo: {impressora.modelo}\n" \
                f"Marca: {impressora.marca}\n" \
                f"Setor: {impressora.setor}\n" \
                f"Conexão: {impressora.conexao}\n\n" \
                f"Peça solicitada: {peca}\n" \
                f"Contador: {contador}"

            send_email(EMAIL_DESTINATARIO, 'Pedido de Peças', body)
            flash("Pedido de peças enviado com sucesso!")

        return redirect(url_for('impressora_profile', serie=serie))

    pedidos = Pedido.query.filter_by(serie=impressora.serie).all()

    return render_template('impressora_profile.html', impressora=impressora.to_dict(), pedidos=pedidos)

@app.route('/check_db')
def check_db():
    return current_app.config['SQLALCHEMY_DATABASE_URI']

@app.route('/list_tables')
def list_tables():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()  # Obtém os nomes das tabelas
    tables_data = {}

    for table_name in table_names:
        print(f"Consultando a tabela: {table_name}")  # Debug: ver qual tabela está sendo consultada
        query = db.session.execute(text(f'SELECT * FROM {table_name}'))  # Consulta SQL
        columns = query.keys()  # Pega os nomes das colunas
        rows = [dict(row) for row in query]  # Converte as linhas para dicionários

        tables_data[table_name] = {'columns': columns, 'rows': rows}

    return render_template('list_tables.html', tables=tables_data)

@app.route('/add_impressora', methods=['POST'])
def add_impressora():
    if request.method == 'POST':
        try:
            serie = request.form.get('serie')
            modelo = request.form.get('modelo')
            marca = request.form.get('marca')
            setor = request.form.get('setor', '')  # Campo opcional
            conexao = request.form.get('conexao', '')  # Campo opcional

            # Verificar se os dados foram preenchidos corretamente
            if not serie or not modelo or not marca:
                flash('Série, modelo e marca são obrigatórios!')
                return redirect(url_for('home'))

            # Adiciona nova impressora
            nova_impressora = Impressora(serie=serie, modelo=modelo, marca=marca, setor=setor, conexao=conexao)
            db.session.add(nova_impressora)
            db.session.commit()

            flash('Impressora adicionada com sucesso!')
        except Exception as e:
            logging.error(f"Erro ao adicionar impressora: {e}")
            flash(f'Ocorreu um erro ao adicionar a impressora: {e}')

    return redirect(url_for('home'))

# Inicializa o banco de dados e cria as tabelas se não existirem
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()  # Inicializa o banco de dados e cria as tabelas
    app.run(debug=True)