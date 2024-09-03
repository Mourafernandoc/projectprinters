from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar 'flash' para mensagens

# Configurações do Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'fcezariomoura@gmail.com'  # substitua pelo seu e-mail do Gmail
EMAIL_PASSWORD = 'F3rn@nd01124'  # substitua pela sua senha do Gmail
EMAIL_DESTINATARIO = 'skyennonet@gmail.com'

# Função para carregar o Excel e retornar um DataFrame
def load_excel():
    try:
        df = pd.read_excel('impressoras.xlsx')
        print("Excel carregado com sucesso")
        return df
    except Exception as e:
        print(f"Erro ao carregar o Excel: {e}")
        return None

# Função para garantir que o arquivo pedidos.xlsx exista
def ensure_pedidos_file():
    if not os.path.exists('pedidos.xlsx'):
        df = pd.DataFrame(columns=['Data', 'Hora', 'Série', 'Modelo', 'Marca', 'Setor', 'Conexão', 'Contador', 'Peça'])
        df.to_excel('pedidos.xlsx', index=False)
        print("Arquivo pedidos.xlsx criado com sucesso")

@app.route('/')
def home():
    df = load_excel()
    if df is not None:
        search_query = request.args.get('search', '').strip()
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        data = df.to_dict(orient='records')
        return render_template('index.html', data=data)
    else:
        flash("Erro ao carregar os dados. Por favor, verifique o arquivo Excel.")
        return render_template('index.html', data=[])

@app.route('/impressora/<serie>', methods=['GET', 'POST'])
def impressora_profile(serie):
    df = load_excel()
    if df is not None:
        try:
            impressora = df[df['Série'] == serie].to_dict(orient='records')[0]
        except IndexError:
            flash(f"Impressora com série {serie} não encontrada.")
            return redirect(url_for('home'))

        if request.method == 'POST':
            if 'update_info' in request.form:
                setor = request.form.get('setor')
                conexao = request.form.get('conexao')
                df.loc[df['Série'] == serie, 'Setor'] = setor
                df.loc[df['Série'] == serie, 'Conexão'] = conexao
                try:
                    df.to_excel('impressoras.xlsx', index=False)
                    flash("Informações atualizadas com sucesso!")
                except Exception as e:
                    flash(f"Erro ao salvar as alterações: {e}")

            elif 'send_email' in request.form:
                contador = request.form.get('contador')
                peca = request.form.get('peca')
                mensagem = f"Solicito o seguinte material para o equipamento abaixo:\n\n"
                mensagem += f"Série: {impressora['Série']}\nModelo: {impressora['Modelo']}\nMarca: {impressora['Marca']}\nSetor: {impressora['Setor']}\nConexão: {impressora['Conexão']}\nContador: {contador}\nPeça: {peca}"

                try:
                    enviar_email(mensagem)
                    flash("Pedido enviado com sucesso!")
                    registrar_pedido(impressora, contador, peca)
                except Exception as e:
                    flash(f"Erro ao enviar o pedido: {e}")

            return redirect(url_for('impressora_profile', serie=serie))

        return render_template('impressora_profile.html', impressora=impressora)
    else:
        flash("Erro ao carregar os dados. Por favor, verifique o arquivo Excel.")
        return redirect(url_for('home'))

# Função para enviar e-mail
def enviar_email(mensagem):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            msg = MIMEText(mensagem)
            msg['Subject'] = 'Pedido de Peça'
            msg['From'] = EMAIL_USER
            msg['To'] = EMAIL_DESTINATARIO
            server.sendmail(EMAIL_USER, EMAIL_DESTINATARIO, msg.as_string())
    except Exception as e:
        raise Exception(f"Erro ao enviar e-mail: {e}")

# Função para registrar o pedido
def registrar_pedido(impressora, contador, peca):
    try:
        df = pd.read_excel('pedidos.xlsx')
        novo_pedido = {
            'Data': datetime.now().strftime('%Y-%m-%d'),
            'Hora': datetime.now().strftime('%H:%M:%S'),
            'Série': impressora['Série'],
            'Modelo': impressora['Modelo'],
            'Marca': impressora['Marca'],
            'Setor': impressora['Setor'],
            'Conexão': impressora['Conexão'],
            'Contador': contador,
            'Peça': peca
        }
        df = df.append(novo_pedido, ignore_index=True)
        df.to_excel('pedidos.xlsx', index=False)
    except Exception as e:
        print(f"Erro ao registrar pedido: {e}")

if __name__ == '__main__':
    ensure_pedidos_file()
    app.run(debug=True)
