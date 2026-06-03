from flask import Flask, jsonify, request
from analyzer import *

app = Flask(__name__)

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
        return jsonify({'Sucesso': True, 'Estatisticas' : resultado}), 200
    except Exception as e:
        return jsonify({'Erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)