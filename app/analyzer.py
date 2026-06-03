import numpy as np

def calculo_estatistica(numeros : list) -> dict:
    
    arr = np.array(numeros, dtype=float)
    
    return {
        "Count" : int(arr.size),
        "Mean" : round(float(np.mean(arr)), 4),
        "Median" : round(float(np.median(arr)), 4),
        "STD" : round(float(np.std(arr)), 4),
        "Variance" : round(float(np.var(arr)), 4),
        "Min" : round(float(np.min(arr)), 4),
        "Max" : round(float(np.max(arr)), 4),
        "p25" : round(float(np.percentile(arr, 25)), 4),
        "p50" : round(float(np.percentile(arr, 50)), 4),
        "p75" : round(float(np.percentile(arr, 75)), 4)   
    }

def calculo_histograma(numeros : list, bins : int) -> dict:
    
    arr = np.array(numeros, dtype=float)
    
    frequencia, intervalos = np.histogram(arr, bins=bins)
    
    return {
        "Intervalos" : intervalos.tolist(),
        "Frequencia" : frequencia.tolist()
    }

def comparar_estatistica(numeros1 : list, numeros2 : list) -> dict:
    
    