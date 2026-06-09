from models.connection.redis_connection import RedisConnection
from datetime import datetime
import json

redis_client = RedisConnection().connect()

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

def clear_history():
    """Deleta histórico"""
    redis_client.delete(HISTORY_KEY)