from app import app, db
from app import Impressora  # Ajuste conforme sua estrutura de projeto

with app.app_context():
    impressoras = Impressora.query.all()
    for impressora in impressoras:
        print(impressora.serie, impressora.modelo, impressora.marca, impressora.setor, impressora.conexao)
