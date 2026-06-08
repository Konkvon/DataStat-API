# 1. Imagem base: Python 3.11 leve (baseada em Debian slim)
FROM python:3.11-slim
# 2. Define o diretório de trabalho dentro do container
WORKDIR /app
# 3. Copia o arquivo de dependências ANTES do código
# (Docker cacheia esta camada — rebuild fica mais rápido)
COPY requirements.txt .
# 4. Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt
# 5. Copia o restante do código para dentro do container
COPY . .
# 6. Expõe a porta 5000 para comunicação externa
EXPOSE 5000
# 7. Comando executado quando o container inicia
CMD ["python", "main.py"]