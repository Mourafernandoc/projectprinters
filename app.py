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
EMAIL_USER = 'skyennonet@gmail.com'  # substitua pelo seu e-mail do Gmail
EMAIL_PASSWORD = ''  # substitua pela sua senha do Gmail
EMAIL_DESTINATARIO = 'fcezariomoura@gmail.com'

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
            if 'request_parts' in request.form:
                contador = request.form.get('contador')
                peca = request.form.get('peca')

                # Atualizando a planilha de pedidos
                pedido_df = pd.DataFrame({
                    'Data': [datetime.now().strftime('%Y-%m-%d')],
                    'Hora': [datetime.now().strftime('%H:%M:%S')],
                    'Série': [impressora['Série']],
                    'Modelo': [impressora['Modelo']],
                    'Marca': [impressora['Marca']],
                    'Setor': [impressora['Setor']],
                    'Conexão': [impressora['Conexão']],
                    'Contador': [contador],
                    'Peça': [peca]
                })

                if os.path.exists('pedidos.xlsx'):
                    pedidos = pd.read_excel('pedidos.xlsx')
                    pedidos = pd.concat([pedidos, pedido_df], ignore_index=True)
                else:
                    pedidos = pedido_df

                pedidos.to_excel('pedidos.xlsx', index=False)

                # Enviando e-mail
                body = f"Solicito o seguinte material para o equipamento abaixo:\n\n" \
                    f"Série: {impressora['Série']}\n" \
                    f"Modelo: {impressora['Modelo']}\n" \
                    f"Marca: {impressora['Marca']}\n" \
                    f"Setor: {impressora['Setor']}\n" \
                    f"Conexão: {impressora['Conexão']}\n\n" \
                    f"Peça solicitada: {peca}\n" \
                    f"Contador: {contador}"

                send_email(EMAIL_DESTINATARIO, 'Pedido de Peças', body)
                flash("Pedido de peças enviado com sucesso!")

            return redirect(url_for('impressora_profile', serie=serie))

        return render_template('impressora_profile.html', impressora=impressora)
    else:
        flash("Erro ao carregar os dados. Por favor, verifique o arquivo Excel.")
        return redirect(url_for('home'))




# Função para enviar e-mail
def send_email(to_email, subject, body):
    from_email = 'fcezariomoura@gmail.com'
    from_password ='Nadjeschd@1808'
    to_email = 'skyennonet@gmail.com'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            print("Email enviado com sucesso!")
    except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")


# Função para registrar o pedido
def registrar_pedido(impressora, contador, peca):
    try:
        # Verifica se o arquivo 'pedidos.xlsx' existe e carrega o conteúdo
        if os.path.exists('pedidos.xlsx'):
            df = pd.read_excel('pedidos.xlsx')
        else:
            # Se o arquivo não existir, cria um DataFrame vazio com as colunas necessárias
            df = pd.DataFrame(columns=['Data', 'Hora', 'Série', 'Modelo', 'Marca', 'Setor', 'Conexão', 'Contador', 'Peça'])

        # Cria um novo pedido como um DataFrame de uma linha
        novo_pedido = pd.DataFrame([{
            'Data': datetime.now().strftime('%Y-%m-%d'),
            'Hora': datetime.now().strftime('%H:%M:%S'),
            'Série': impressora['Série'],
            'Modelo': impressora['Modelo'],
            'Marca': impressora['Marca'],
            'Setor': impressora['Setor'],
            'Conexão': impressora['Conexão'],
            'Contador': contador,
            'Peça': peca
        }])

        # Concatena o novo pedido com o DataFrame existente
        df = pd.concat([df, novo_pedido], ignore_index=True)

        # Salva o DataFrame atualizado de volta no arquivo Excel
        df.to_excel('pedidos.xlsx', index=False)
        print("Pedido registrado com sucesso")

    except Exception as e:
        print(f"Erro ao registrar pedido: {e}")


if __name__ == '__main__':
    ensure_pedidos_file()
    app.run(host='0.0.0.0',port=5000,debug=True)
