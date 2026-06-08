from flask import Flask, jsonify, request, send_from_directory
from analyzer import *
import redis
import json
from datetime import datetime

redis_client = redis.StrictRedis(host="redis", port=6379, db=0)

MAX_HISTORY = 10
HISTORY_KEY = 'history'
HISTORY_TTL = 180

def store_in_history(operation_type, input_data, result):
    """Armazena operação no histórico com timestamp"""
    history_entry = {
        'type': operation_type,
        'timestamp': datetime.now().isoformat(),
        'input': input_data,
        'result': result
    }
    # Adiciona nova entrada ao final da lista no Redis
    redis_client.rpush(HISTORY_KEY, json.dumps(history_entry))
    # Manter apenas os últimos MAX_HISTORY registros
    redis_client.ltrim(HISTORY_KEY, -MAX_HISTORY, -1)
    # Define tempo de expiração para a lista de histórico
    redis_client.expire(HISTORY_KEY, HISTORY_TTL)

def get_history():
    """Recupera todo o histórico do Redis"""
    history_data = redis_client.lrange(HISTORY_KEY, 0, -1)
    return [json.loads(entry) for entry in history_data]

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'Status': 'Ok'}), 200

@app.route('/calculate', methods=['POST'])
def calculate():
    dados = request.get_json()
    
    if not dados or 'numeros' not in dados:
       return jsonify({'Erro' : 'Envie um JSON com a chave numeros'}), 400
   
    numeros = dados['numeros']
    
    if not isinstance(numeros, list) or len(numeros) == 0:
        return jsonify({'Erro' : 'Numeros deve ser uma lista não vazia'}), 400
    
    try:
        resultado = calculo_estatistica(numeros)
        store_in_history('calculate', {'numeros': numeros}, resultado)
        return jsonify({'Sucesso': True, 'Estatisticas' : resultado}), 200
    except Exception as e:
        return jsonify({'Erro': str(e)}), 500

@app.route('/histogram', methods=['POST'])
def histogram():
    dados = request.get_json()
    
    if not dados or 'numeros' not in dados or 'bins' not in dados:
        return jsonify({'Erro' : 'Envie um JSON com a chave numeros e bins'}), 400

    numeros = dados['numeros']
    bins = dados['bins']

    if not isinstance(bins, int) or bins <= 0:
        return jsonify({'Erro' : 'Bins deve ser um inteiro positivo'}), 400

    if not isinstance(numeros, list) or len(numeros) == 0:
        return jsonify({'Erro' : 'Numeros deve ser uma lista não vazia'}), 400
    
    try:
        resultado = calculo_histograma(numeros, bins)
        store_in_history('histogram', {'numeros': numeros, 'bins': bins}, resultado)
        return jsonify({"Sucesso" : True, "Histograma" : resultado}), 200
    except Exception as e:
        return jsonify({'Erro' : str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare():
    dados = request.get_json()
    
    if not dados or 'numeros1' not in dados or 'numeros2' not in dados:
        return jsonify({'Erro' : 'Envie um JSON com a chave numeros1 e numeros2'}), 400
    
    numeros1, numeros2 = dados['numeros1'], dados['numeros2']
    
    if not isinstance(numeros1, list) or len(numeros1) == 0:
        return jsonify({'Erro' : 'Numeros1 deve ser uma lista não vazia'}), 400

    if not isinstance(numeros2, list) or len(numeros2) == 0:
        return jsonify({'Erro' : 'Numeros2 deve ser uma lista não vazia'}), 400
    
    try:
        resultado = comparar_estatistica(numeros1, numeros2)
        store_in_history('compare', {'numeros1': numeros1, 'numeros2': numeros2}, resultado)
        return jsonify({"Sucesso" : True, "Comparacao" : resultado}), 200
    except Exception as e:
        return jsonify({'Erro' : str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        hist = get_history()
        return jsonify({'Sucesso': True, 'Historico': hist}), 200
    except Exception as e:
        return jsonify({'Erro': str(e)}), 500

@app.route('/history/clear', methods=['DELETE'])
def clear_history():
    try:
        redis_client.delete(HISTORY_KEY)
        return jsonify({'Sucesso': True, 'Mensagem': 'Histórico limpo com sucesso'}), 200
    except Exception as e:
        return jsonify({'Erro': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)