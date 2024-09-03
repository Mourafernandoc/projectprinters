from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar 'flash' para mensagens

# Função para carregar o Excel e retornar um DataFrame
def load_excel():
    try:
        df = pd.read_excel('impressoras.xlsx')
        print("Excel carregado com sucesso")
        return df
    except Exception as e:
        print(f"Erro ao carregar o Excel: {e}")
        return None

# Função para carregar o Excel dos pedidos e retornar um DataFrame
def load_pedidos():
    try:
        return pd.read_excel('pedidos.xlsx')
    except Exception as e:
        print(f"Erro ao carregar os pedidos: {e}")
        return pd.DataFrame(columns=['Data', 'Impressora', 'Contador', 'Peça'])

@app.route('/')
def home():
    df = load_excel()
    if df is not None:
        # Captura o termo de pesquisa da query string
        search_query = request.args.get('search', '').strip()
        
        # Aplica o filtro de pesquisa, se houver um termo de pesquisa
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
            if 'edit' in request.form:
                # Atualiza as informações da impressora
                setor = request.form.get('setor')
                conexao = request.form.get('conexao')
                df.loc[df['Série'] == serie, 'Setor'] = setor  # "Setor" com S maiúsculo
                df.loc[df['Série'] == serie, 'Conexão'] = conexao  # "Conexão" com C maiúsculo
                try:
                    df.to_excel('impressoras.xlsx', index=False)
                    flash("Informações atualizadas com sucesso!")
                except Exception as e:
                    flash(f"Erro ao salvar as alterações: {e}")
                return redirect(url_for('impressora_profile', serie=serie))
            
            elif 'request_parts' in request.form:
                # Processa o pedido de peças
                contador = request.form.get('contador')
                peca = request.form.get('peca')
                pedido_texto = f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nImpressora: {serie}\nContador: {contador}\nPeça: {peca}"
                
                # Envio de e-mail
                try:
                    msg = MIMEText(pedido_texto)
                    msg['Subject'] = f'Pedido de Peça para Impressora {serie}'
                    msg['From'] = 'your_email@example.com'
                    msg['To'] = 'destination_email@example.com'
                    
                    with smtplib.SMTP('smtp.example.com', 587) as server:
                        server.starttls()
                        server.login('your_email@example.com', 'your_password')
                        server.send_message(msg)
                    
                    # Registro do pedido
                    pedidos_df = load_pedidos()
                    pedidos_df = pedidos_df.append({'Data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Impressora': serie, 'Contador': contador, 'Peça': peca}, ignore_index=True)
                    pedidos_df.to_excel('pedidos.xlsx', index=False)
                    
                    flash("Pedido de peça enviado com sucesso!")
                except Exception as e:
                    flash(f"Erro ao enviar o pedido: {e}")
                
                return redirect(url_for('impressora_profile', serie=serie))
        
        # Carregar e exibir os pedidos para a impressora
        pedidos_df = load_pedidos()
        pedidos = pedidos_df[pedidos_df['Impressora'] == serie].to_dict(orient='records')
        return render_template('impressora_profile.html', impressora=impressora, pedidos=pedidos)
    else:
        flash("Erro ao carregar os dados. Por favor, verifique o arquivo Excel.")
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
