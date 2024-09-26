# Gerenciamento de Impressoras

Este projeto é uma aplicação web desenvolvida em **Python** com **Flask** que permite gerenciar impressoras e realizar pedidos de peças. A aplicação exibe uma listagem de impressoras na página principal, organizadas em cards, com a opção de acessar o perfil detalhado de cada impressora. No perfil, o usuário pode editar informações e solicitar peças, com a funcionalidade de envio de e-mails automatizados.

## Funcionalidades

- **Listagem de Impressoras**: Impressoras são exibidas na página inicial como cards, cada uma com um espaço para imagem correspondente ao modelo.
- **Perfil de Impressoras**: Página dedicada para cada impressora, exibindo detalhes como série, modelo, setor e conexão.
- **Edição de Informações**: Permite a edição de campos como setor e conexão diretamente no perfil.
- **Solicitação de Peças**: Possibilidade de registrar pedidos de peças, que são enviados via e-mail e armazenados no banco de dados.
- **Envio de E-mails**: O sistema envia e-mails automaticamente ao registrar uma solicitação de peças.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Flask**: Framework web para o backend.
- **SQLAlchemy**: ORM para gerenciamento do banco de dados.
- **SQLite**: Banco de dados utilizado.
- **Jinja2**: Template engine para renderizar as páginas HTML.
- **HTML5/CSS3**: Estrutura e estilo das páginas.
- **JavaScript (jQuery)**: Utilizado para interações na interface, como exibição de pop-ups.

## Pré-requisitos

- **Python 3.x** instalado
- **Pip** instalado para gerenciar dependências
- Dependências listadas no `requirements.txt`

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/Mourafernandoc/projectprinters
   

2. Navegue até o diretório do projeto:

   ```bash
   cd seu-repositorio


3. Crie um ambiente virtual (opcional, mas recomendado):

	```bash
	python -m venv venv


4. Ative o ambiente virtual:

	No Windows:
	
	```bash
	venv\Scripts\activate
  
  No Linux/macOS	 
	
 ```bash
  source venv/bin/activate 
  ```

5.Instale as dependências:

	```bash
	pip install -r requirements.txt


6. Inicie o banco de dados:

	```bash
	python
	>>> from app import init_db
	>>> init_db()
	

7. Inicie a aplicação:

	```bash
	python app.py
  

8. Acesse a aplicação no navegador no endereço: http://localhost:5000


##Configuração de Rede Local
	Se você deseja que a aplicação seja acessível na sua rede local, altere a linha de execução no arquivo app.py:
	
	```bash
	if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

Isso permitirá o acesso via rede local através do IP da máquina onde a aplicação está rodando.

##Estrutura de Arquivos

```bash
	.
├── app.py                  # Arquivo principal da aplicação Flask
├── bd-create.py            # Script para criação e migração do banco de dados
├── templates/
│   ├── index.html          # Página inicial com a listagem de impressoras
│   ├── impressora_profile.html  # Página de perfil da impressora
├── static/
│   ├── css/
│   │   └── style.css       # Arquivo de estilo (CSS)
│   ├── images/             # Diretório para imagens das impressoras
├── requirements.txt        # Arquivo de dependências da aplicação
└── impressoras.db          # Banco de dados SQLite (após a inicialização)
```

##Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para obter mais detalhes.

##Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou abrir issues no repositório.
