"""Geração de gráficos server-side (seaborn/matplotlib).

Este módulo é o único responsável por produzir imagens. O `analyzer.py`
permanece puro (só NumPy). As figuras são renderizadas em memória e
devolvidas como data URI (`data:image/png;base64,...`), nunca gravadas em
disco.

Regras importantes:
- O backend do matplotlib é configurado como "Agg" ANTES de importar pyplot,
  pois o servidor não é interativo.
- O estado global do pyplot não é thread-safe e o Flask roda com
  `threaded=True`. Cada plotagem é serializada por um `threading.Lock` de
  módulo e a figura é SEMPRE fechada no `finally` para evitar vazamento de
  memória.
- As imagens têm fundo transparente e textos/eixos em cinza médio para
  permanecerem legíveis tanto no tema claro quanto no escuro do cliente
  (`prefers-color-scheme`).
"""

import base64
import io
import threading

import matplotlib

matplotlib.use("Agg")  # backend não-interativo, antes de importar pyplot

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

# Serializa o acesso ao estado global do pyplot (não thread-safe).
_PLOT_LOCK = threading.Lock()

# Paleta pensada para legibilidade em tema claro E escuro.
_ACCENT = "#6366f1"        # cor de destaque (indigo)
_INK = "#888888"           # cinza médio: legível sobre fundo claro ou escuro
_GRID = "#8888884d"        # cinza médio translúcido para linhas de grade


def _style_axes(ax):
    """Aplica o estilo neutro comum a todos os gráficos."""
    ax.set_facecolor("none")
    ax.title.set_color(_INK)
    ax.xaxis.label.set_color(_INK)
    ax.yaxis.label.set_color(_INK)
    ax.tick_params(colors=_INK, which="both")
    for spine in ax.spines.values():
        spine.set_color(_INK)
    sns.despine(ax=ax)


def _fig_to_data_uri(fig) -> str:
    """Serializa a figura como PNG transparente em uma data URI base64."""
    buffer = io.BytesIO()
    fig.savefig(
        buffer,
        format="png",
        dpi=110,
        bbox_inches="tight",
        transparent=True,
    )
    buffer.seek(0)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def plot_histograma(numeros: list, bins: int) -> str:
    """Histograma de barras dos números, com `bins` intervalos."""
    arr = np.asarray(numeros, dtype=float)
    with _PLOT_LOCK:
        fig, ax = plt.subplots(figsize=(7, 4))
        try:
            sns.histplot(x=arr, bins=bins, color=_ACCENT, edgecolor="none", ax=ax)
            ax.set_xlabel("Valor")
            ax.set_ylabel("Frequência")
            ax.set_title("Distribuição de frequência")
            ax.grid(axis="y", color=_GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            _style_axes(ax)
            fig.tight_layout()
            return _fig_to_data_uri(fig)
        finally:
            plt.close(fig)
