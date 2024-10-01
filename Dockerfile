#imagem base
FROM python:3.10-slim

#diretorio de trabalho no conteiner
WORKDIR /app

#copiar os arquivos de dependencias para o conteiner
COPY requirements.txt requirements.txt

#instala as depedencias para o conteiner
RUN pip install --no-cache-dir -r requirements.txt

#copia o restante do codigo da aplicação para o conteiner
COPY . .

#exponha a porta 5000(a porta usada pelo Flask)
EXPOSE 5000

#comando para iniciar a aplicação
CMD ["python", "app.py"]