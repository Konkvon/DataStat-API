# DataStat API

## Visão Geral do Projeto

A DataStat API é uma aplicação web desenvolvida com Flask que oferece funcionalidades para análise estatística de conjuntos de dados numéricos. A API permite calcular estatísticas descritivas, gerar histogramas e comparar estatísticas entre dois conjuntos de números. Além disso, a aplicação inclui uma interface web simples para interagir com os endpoints da API e visualizar os resultados, bem como um sistema de histórico de operações.

## Funcionalidades

- **Cálculo de Estatísticas Descritivas**: Calcula média, mediana, desvio padrão, variância, mínimo, máximo, percentis (25, 50, 75) e contagem para um dado conjunto de números.
- **Geração de Histograma**: Cria um histograma para um conjunto de números, retornando os intervalos e a frequência de cada bin, além de um **gráfico renderizado no servidor** (imagem PNG via seaborn/matplotlib) devolvido como data URI.
- **Comparação de Estatísticas**: Compara as estatísticas descritivas de dois conjuntos de números (exibida como tabela).
- **Histórico de Operações**: Mantém um registro das últimas 10 operações de análise realizadas, recarregado automaticamente na interface após cada operação.
- **Interface Web Interativa**: Interface em HTML/CSS/JavaScript puro (sem framework), com layout em **abas**, tema claro/escuro automático (`prefers-color-scheme`) e visualização dos resultados em tabelas e gráficos.

## Tecnologias Utilizadas

- **Backend**: Python 3.11 com Flask
- **Análise Numérica**: NumPy
- **Plotagem**: seaborn, matplotlib e pandas (gráficos gerados no servidor)
- **Cache**: Redis (para o histórico de operações)
- **Containerização**: Docker
- **Frontend**: HTML, CSS e JavaScript vanilla (sem build step)

## Configuração e Instalação

Para configurar e executar a DataStat API localmente, siga os passos abaixo:

### Pré-requisitos

Certifique-se de ter o Docker instalado em sua máquina.

### Execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/Konkvon/DataStat-API.git
   cd DataStat-API
   ```

2. Inicie os serviços com Docker Compose:
   ```bash
   docker-compose up --build
   ```

   Isso irá construir a imagem Docker da aplicação Flask e iniciar o contêiner da API, juntamente com um contêiner Redis. A aplicação estará disponível em `http://localhost:5000`.

## Endpoints da API

A API expõe os seguintes endpoints:

### `GET /`

Retorna a interface web da aplicação.

### `GET /health`

Verifica a saúde da API.

- **Resposta de Sucesso**: `HTTP 200 OK`
  ```json
  {
    "Status": "Ok"
  }
  ```

### `POST /calculate`

Calcula estatísticas descritivas para um conjunto de números.

- **Corpo da Requisição**:
  ```json
  {
    "numeros": [1, 2, 3, 4, 5]
  }
  ```

- **Resposta de Sucesso**: `HTTP 200 OK`
  ```json
  {
    "Sucesso": true,
    "Estatisticas": {
      "Count": 5,
      "Mean": 3.0,
      "Median": 3.0,
      "STD": 1.4142,
      "Variance": 2.0,
      "Min": 1.0,
      "Max": 5.0,
      "p25": 2.0,
      "p50": 3.0,
      "p75": 4.0
    }
  }
  ```

### `POST /histogram`

Gera um histograma para um conjunto de números com um número especificado de bins.

- **Corpo da Requisição**:
  ```json
  {
    "numeros": [1, 2, 2, 3, 3, 3, 4, 4, 5],
    "bins": 3
  }
  ```

- **Resposta de Sucesso**: `HTTP 200 OK`
  ```json
  {
    "Sucesso": true,
    "Histograma": {
      "Intervalos": [1.0, 2.3333333333333335, 3.666666666666667, 5.0],
      "Frequencia": [2, 3, 4]
    },
    "Grafico": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
  }
  ```

  O campo `Grafico` é a imagem do histograma (PNG em base64) renderizada no servidor. Se a geração do gráfico falhar por algum motivo, `Grafico` vem como `null` e o cálculo numérico não é afetado (degradação graciosa). A imagem **não** é persistida no histórico.

### `POST /compare`

Compara estatísticas descritivas entre dois conjuntos de números.

- **Corpo da Requisição**:
  ```json
  {
    "numeros1": [1, 2, 3],
    "numeros2": [4, 5, 6]
  }
  ```

- **Resposta de Sucesso**: `HTTP 200 OK`
  ```json
  {
    "Sucesso": true,
    "Comparacao": {
      "Count": [3, 3],
      "Mean": [2.0, 5.0],
      "Median": [2.0, 5.0],
      "STD": [0.8165, 0.8165],
      "Variance": [0.6667, 0.6667],
      "Min": [1.0, 4.0],
      "Max": [3.0, 6.0],
      "p25": [1.5, 4.5],
      "p50": [2.0, 5.0],
      "p75": [2.5, 5.5]
    }
  }
  ```

### `GET /history`

Retorna o histórico das últimas operações de análise.

- **Resposta de Sucesso**: `HTTP 200 OK`
  ```json
  {
    "Sucesso": true,
    "Historico": [
      {
        "type": "calculate",
        "timestamp": "2023-10-27T10:00:00.000000",
        "input": {"numeros": [1, 2, 3]},
        "result": { ... }
      }
    ]
  }
  ```

### `DELETE /history/clear`

Limpa o histórico de operações.

- **Resposta de Sucesso**: `HTTP 200 OK`
  ```json
  {
    "Sucesso": true,
    "Mensagem": "Histórico limpo com sucesso"
  }
  ```

## Estrutura do Projeto

```
DataStat-API/
├── app/
│   ├── Dockerfile
│   ├── analyzer.py            # computação NumPy pura (sem efeitos colaterais)
│   ├── plots.py              # geração dos gráficos server-side (seaborn/matplotlib)
│   ├── main.py               # rotas Flask + validação
│   ├── models/
│   │   └── connection/
│   │       ├── __init__.py
│   │       ├── connection_options.py
│   │       └── redis_connection.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── data_repository.py
│   ├── requirements.txt
│   ├── services/
│   │   ├── __init__.py
│   │   └── data_service.py   # orquestração (cálculo + plotagem + histórico)
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   └── templates/
│       └── index.html
├── plans/                    # documentos de planejamento
│   └── FRONTEND_REDESIGN_PLAN.md
├── docker-compose.yml
├── pytest.ini
├── CLAUDE.md
├── .gitignore
└── tests/
    └── test_analyzer.py
```

## Autor

- João Pedro Orem de Moura