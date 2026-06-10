# DataStat API

## Visão Geral do Projeto

A DataStat API é uma aplicação web desenvolvida com Flask que oferece funcionalidades para análise estatística de conjuntos de dados numéricos. A API permite calcular estatísticas descritivas, gerar histogramas e comparar estatísticas entre dois conjuntos de números. Além disso, a aplicação inclui uma interface web simples para interagir com os endpoints da API e visualizar os resultados, bem como um sistema de histórico de operações.

## Funcionalidades

- **Cálculo de Estatísticas Descritivas**: Calcula média, mediana, desvio padrão, variância, mínimo, máximo, percentis (25, 50, 75) e contagem para um dado conjunto de números.
- **Geração de Histograma**: Cria um histograma para um conjunto de números, retornando os intervalos e a frequência de cada bin.
- **Comparação de Estatísticas**: Compara as estatísticas descritivas de dois conjuntos de números.
- **Histórico de Operações**: Mantém um registro das últimas 10 operações de análise realizadas.
- **Interface Web Interativa**: Uma interface de usuário baseada em HTML/CSS/JavaScript para facilitar a interação com a API e a visualização dos resultados.

## Tecnologias Utilizadas

- **Backend**: Python 3.11 com Flask
- **Análise Numérica**: NumPy
- **Cache**: Redis (para o histórico de operações)
- **Containerização**: Docker
- **Frontend**: HTML, CSS, JavaScript

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
    }
  }
  ```

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
│   ├── analyzer.py
│   ├── main.py
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
│   │   └── data_service.py
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   └── templates/
│       └── index.html
├── docker-compose.yml
├── pytest.ini
└── tests/
    └── test_analyzer.py
```

## Autor

- João Pedro Orem de Moura