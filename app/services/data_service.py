import repositories.data_repository as repository
import analyzer

def get_history():
    hist = repository.get_history()
    return hist

def clear_history():
    repository.clear_history()

def calcular_estatistica(numeros):
    resultado = analyzer.calculo_estatistica(numeros)
    repository.store_in_history('calculate', {'numeros': numeros}, resultado)
    return resultado

def calcular_histograma(numeros,bins):
    resultado = analyzer.calculo_histograma(numeros, bins)
    repository.store_in_history('histogram', {'numeros': numeros, 'bins': bins}, resultado)
    return resultado

def comparar_estatistica(numeros1, numeros2):
    resultado = analyzer.comparar_estatistica(numeros1, numeros2)
    repository.store_in_history('compare', {'numeros1': numeros1, 'numeros2': numeros2}, resultado)
    return resultado