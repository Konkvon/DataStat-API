import pytest
import numpy as np
from app.analyzer import *

@pytest.mark.parametrize("numeros", [
    [1, 2, 3, 4, 5],
    [10, 20, 30, 40, 50],
    [5, 5, 5, 5, 5]
])
def test_calculo_estatistica(numeros : list) -> dict:
    
    arr = np.array(numeros, dtype=float)
    
    assert {
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
    
@pytest.mark.parametrize("numeros, bins", [
    ([1, 2, 3, 4, 5], 2),
    ([10, 20, 30], 3)
])
def test_calculo_histograma(numeros : list, bins : int) -> dict:
    
    arr = np.array(numeros, dtype=float)
    
    frequencia, intervalos = np.histogram(arr, bins=bins)
    
    assert {
        "Intervalos" : intervalos.tolist(),
        "Frequencia" : frequencia.tolist()
    }


@pytest.mark.parametrize("numeros1, numeros2", [
    ([1, 2, 3], [4, 5, 6]),
    ([10, 20, 30], [15, 25, 35]),
    ([5], [5])
])
def test_comparar_estatistica(numeros1 : list, numeros2 : list) -> dict:
    n1 = calculo_estatistica(numeros1)
    n2 = calculo_estatistica(numeros2)
    assert {
        chave : (n1[chave], n2[chave]) 
        for chave in n1.keys()
    }