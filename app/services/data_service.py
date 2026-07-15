import repositories.data_repository as repository
import analyzer
import plots

def get_history():
    hist = repository.get_history()
    return hist

def clear_history():
    repository.clear_history()

def calcular_estatistica(numeros):
    resultado = analyzer.calculo_estatistica(numeros)
    repository.store_in_history('calculate', {'numeros': numeros}, resultado)
    return resultado

def calcular_histograma(numeros, bins):
    resultado = analyzer.calculo_histograma(numeros, bins)
    # O histórico guarda apenas o resultado numérico (imagem não é persistida).
    repository.store_in_history('histogram', {'numeros': numeros, 'bins': bins}, resultado)
    grafico = _plot_seguro(plots.plot_histograma, numeros, bins)
    return {'Histograma': resultado, 'Grafico': grafico}

def comparar_estatistica(numeros1, numeros2):
    resultado = analyzer.comparar_estatistica(numeros1, numeros2)
    repository.store_in_history('compare', {'numeros1': numeros1, 'numeros2': numeros2}, resultado)
    return resultado

def _plot_seguro(func, *args):
    """Gera o gráfico com degradação graciosa.

    Se a plotagem falhar por qualquer motivo, o cálculo numérico não deve ser
    afetado: retornamos ``None`` e a UI exibe apenas a tabela.
    """
    try:
        return func(*args)
    except Exception:
        return None
