from flask import Flask, jsonify, request, send_from_directory
import services.data_service as service

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
        resultado = service.calcular_estatistica(numeros)
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
        resultado = service.calcular_histograma(numeros, bins)
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
        resultado = service.comparar_estatistica(numeros1, numeros2)
        return jsonify({"Sucesso" : True, "Comparacao" : resultado}), 200
    except Exception as e:
        return jsonify({'Erro' : str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        hist = service.get_history()
        return jsonify({'Sucesso': True, 'Historico': hist}), 200
    except Exception as e:
        return jsonify({'Erro': str(e)}), 500

@app.route('/history/clear', methods=['DELETE'])
def clear_history():
    try:
        service.clear_history()
        return jsonify({'Sucesso': True, 'Mensagem': 'Histórico limpo com sucesso'}), 200
    except Exception as e:
        return jsonify({'Erro': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)