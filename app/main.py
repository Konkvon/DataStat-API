from flask import Flask, jsonify, request
from analyzer import *

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'Status': 'Ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)