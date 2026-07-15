# Plano de Redesign do Frontend — DataStat API

> Documento de implementação para o agente responsável. Todas as decisões abaixo foram
> confirmadas com o dono do projeto em entrevista. Não reabrir decisões já tomadas.

## Decisões confirmadas (não alterar)

| Tema | Decisão |
|------|---------|
| **Stack do frontend** | Vanilla HTML/CSS/JS. **Remover o Bootstrap.** Criar design system próprio com CSS moderno (custom properties, grid, flex). **Zero build step** — servido estaticamente pelo Flask como hoje. |
| **Gráficos — conteúdo** | Gráfico visual **+ manter a tabela** de dados (os dois juntos). |
| **Gráficos — renderização** | **Server-side com seaborn + pandas (matplotlib).** NÃO renderizar no cliente. O backend gera a imagem e o frontend só exibe. |
| **Estética** | Dashboard moderno e limpo (estilo SaaS/analytics): cards com sombra suave, muito respiro, tipografia clara, paleta neutra + 1 cor de destaque. |
| **Tema claro/escuro** | Respeitar `prefers-color-scheme` do sistema automaticamente. **Sem** botão de toggle. |
| **Layout** | **Abas (tabs)** no topo alternando Calcular / Histograma / Comparar. Histórico sempre acessível. |

## Contexto do código atual (leia antes de começar)

- Frontend: `app/templates/index.html`, `app/static/styles.css`, `app/static/app.js`. Hoje usa Bootstrap 5 via CDN, 4 seções empilhadas, resultados como tabelas HTML montadas em `app.js`. O histograma hoje é uma **tabela**, não gráfico.
- Backend em camadas (ver `CLAUDE.md`): `main.py` (rotas + validação) → `services/data_service.py` (orquestração + grava histórico) → `analyzer.py` (NumPy puro, sem efeitos colaterais) → `repositories/data_repository.py` (histórico no Redis).
- Endpoints atuais: `GET /`, `GET /health`, `POST /calculate`, `POST /histogram`, `POST /compare`, `GET /history`, `DELETE /history/clear`. Chaves JSON em português (`numeros`, `bins`, `Sucesso`, `Estatisticas`, `Histograma`, `Comparacao`, `Erro`).
- **Restrição de imports:** os módulos usam import "flat" (`import analyzer`, `import services.data_service as service`) que só resolve com `app/` no `sys.path`. Todo módulo novo deve respeitar esse esquema (ficar dentro de `app/` e ser importado da mesma forma).
- `app/requirements.txt` está salvo em **UTF-16** (acidente). Ao editá-lo, **reescrever como UTF-8**.

---

## Trabalho — Backend (plotagem seaborn)

### 1. Dependências
Reescrever `app/requirements.txt` como **UTF-8** adicionando:
```
Flask==3.1.3
numpy==2.4.6
pytest==9.0.3
redis==8.0.0
pandas
seaborn
matplotlib
```
(Manter as versões já fixadas; para as novas, fixar versões compatíveis com Python 3.11 — ex.: `pandas==2.2.*`, `seaborn==0.13.*`, `matplotlib==3.9.*`. Verificar no build do Docker.)

O `Dockerfile` não precisa mudar (o `pip install -r requirements.txt` já cobre). Apenas ciente de que o build ficará mais lento/pesado.

### 2. Novo módulo `app/plots.py`
Manter `analyzer.py` puro (só NumPy). Criar `app/plots.py` responsável por gerar as imagens. Regras obrigatórias:

- **Backend não-interativo do matplotlib** — configurar ANTES de importar pyplot:
  ```python
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  import seaborn as sns
  import pandas as pd
  ```
- **Thread-safety + vazamento de memória:** o servidor Flask roda com `threaded=True`. O estado global do pyplot não é thread-safe. Proteger cada plotagem com um `threading.Lock` de módulo e **sempre** fechar a figura (`plt.close(fig)`) no `finally`.
- **Saída:** renderizar em memória (`io.BytesIO`), PNG, e retornar uma **data URI** (`data:image/png;base64,...`) como `str`. Não gravar arquivos em disco.
- **Compatibilidade com tema claro/escuro:** como a imagem é gerada no servidor e o tema é do cliente (`prefers-color-scheme`), a imagem precisa ser legível nos dois temas. Estratégia: **fundo transparente** (`savefig(..., transparent=True)`), textos/eixos/ticks em cinza médio (~`#888`) legível em ambos os fundos, barras na cor de destaque. Remover molduras (`sns.despine`) para visual clean.

Funções sugeridas:
- `plot_histograma(numeros, bins) -> str` — histograma de barras (seaborn `histplot` ou `barplot` sobre `np.histogram`).
- `plot_comparacao(numeros1, numeros2) -> str` — comparação dos dois conjuntos (boxplot lado a lado **ou** barras agrupadas das métricas). Usar `pandas.DataFrame` no formato long para o seaborn.
- (Opcional, nice-to-have) `plot_distribuicao(numeros) -> str` para a aba Calcular (ex.: boxplot/KDE). Marcar como opcional; só fazer se o resto estiver pronto.

### 3. Camada de serviço (`services/data_service.py`)
- `calcular_histograma` e `comparar_estatistica` passam a chamar também `plots.plot_*` e retornar o gráfico junto do resultado numérico.
- **Não gravar a imagem base64 no histórico do Redis** (pesado e com TTL). O histórico continua guardando só `input` + `result` numérico como hoje. O gráfico é recomputado on-demand quando necessário, ou o histórico simplesmente exibe a tabela (ver frontend).

### 4. Rotas (`main.py`)
- Manter a validação atual intacta.
- `POST /histogram` → resposta passa a incluir o gráfico, ex.: `{"Sucesso": true, "Histograma": {...}, "Grafico": "data:image/png;base64,..."}`.
- `POST /compare` → idem com `"Grafico"`.
- Manter o tratamento de exceções 400/500 existente. Erros de plotagem não devem derrubar o cálculo — se a plotagem falhar, retornar os dados numéricos e omitir/anular `Grafico` (degradação graciosa).

---

## Trabalho — Frontend (redesign)

### 5. `index.html`
- Remover o `<link>` do Bootstrap CDN. Manter apenas `/static/styles.css`.
- Estrutura: cabeçalho com título/subtítulo do produto → **barra de abas** (Calcular · Histograma · Comparar) → painel da aba ativa → seção de Histórico sempre visível abaixo (ou painel lateral no desktop).
- Semântica/acessibilidade: usar `role="tab"`/`aria-selected` nas abas, `aria-live` na área de resultado para feedback de loading.
- Manter todos os `id`s que o `app.js` já usa (`nums`, `calcBtn`, `calcResult`, `histNums`, `bins`, `histBtn`, `histResult`, `nums1`, `nums2`, `cmpBtn`, `cmpResult`, `loadHistBtn`, `clearHistBtn`, `historyResult`) — ou atualizar `app.js` de forma consistente se renomear.

### 6. `styles.css` — design system próprio
- Definir **custom properties** (tokens) para cor, espaçamento, raio, sombra, tipografia. Uma paleta neutra + 1 cor de destaque.
- Dark mode via `@media (prefers-color-scheme: dark)` sobrescrevendo os tokens de cor. Sem toggle.
- Componentes: card, botões (primário/secundário/perigo), inputs/textarea, tabs, tabela de dados, badge de tipo de operação no histórico, estado de erro, estado de loading (skeleton/spinner simples).
- Página não pode ter scroll horizontal; tabelas e imagens de gráfico com `max-width: 100%` e container com `overflow-x: auto` quando necessário.

### 7. `app.js`
- Implementar a lógica das **abas** (mostrar/ocultar painel, estado ativo).
- `formatHistograma` e `formatComparacao`: exibir a **imagem do gráfico** (`<img src="${data.Grafico}" alt="...">`) **acima** da tabela existente. Manter as tabelas.
- Tratar `Grafico` ausente/nulo (backend degradou) — mostrar só a tabela.
- Manter `parseNumbers`, `postJson`, `getJson` e a lógica de histórico. O histórico exibe as tabelas como hoje (sem re-renderizar gráficos, já que não são persistidos).
- Manter o carregamento automático do histórico no `load`.

---

## Verificação (fazer antes de considerar pronto)

1. `docker-compose up --build` sobe sem erro (conferir que seaborn/matplotlib instalaram no build).
2. `POST /histogram` e `POST /compare` retornam `Grafico` como data URI válida (base64 PNG).
3. Na UI: abas alternam corretamente; histograma e comparação mostram **gráfico + tabela**; histórico carrega e limpa.
4. Alternar o tema do SO (claro/escuro) — layout e gráficos permanecem legíveis nos dois.
5. Sem scroll horizontal em telas estreitas (mobile).
6. `pytest` continua passando (os testes atuais não cobrem plotagem; não quebrar `analyzer.py`).
7. Sem vazamento: confirmar que `plt.close(fig)` é chamado em todos os caminhos.

## Fora de escopo (não fazer sem pedir)
- Introduzir Node/build step, framework SPA, ou trocar Flask por outro servidor.
- Persistir imagens de gráfico no Redis.
- Adicionar botão de toggle de tema.
- Mudar contratos de API existentes além de **adicionar** o campo `Grafico`.
