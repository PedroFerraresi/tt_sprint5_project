# Superstore Dashboard – Sprint 5

## Introdução

Este projeto é um **dashboard interativo** (Streamlit) para análise de um conjunto de vendas no estilo *Superstore*.  

O objetivo é oferecer uma visão clara e navegável dos principais indicadores do negócio — **vendas, lucro, custos, clientes e produtos** — com filtros laterais, gráficos dinâmicos (Plotly Express) e páginas temáticas (KPIs gerais, vendas, clientes, produtos e dicionário de dados).  

O código foi pensado como material didático: simples, comentado e facilmente extensível.

---

## Dados

O projeto utiliza um arquivo CSV de vendas com granularidade de **linha de pedido**.

**Arquivos:**

- `data/raw/dataset_ruido.csv`: dados brutos (com ruído).
- `data/processed/processed.csv`: dados processados e prontos para visualização.

**Colunas esperadas** (podem variar conforme o bruto):

- **Datas**: `order_date`, `ship_date`
- **Tempo derivado**: `month_year` (YYYY-MM)
- **Métricas**: `sales`, `profit`, `total_cost` (derivada)
- **Dimensões**: `category`, `sub_category`, `segment`, `country`, `state`, `city`, `postal_code`
- **Itens**: `product_name` (ou `product`)
- **Cliente**: `customer_name` / `customer_id` (se existir)

> Observação: se um campo não existir no CSV de origem, ele pode não aparecer no processado.

---

## Pré-processamento

O pipeline está em `utils/pre_process.py` e é executado pelo `main.py`.

**Etapas principais:**

1. **Leitura robusta** do CSV (`utf-8`, `latin1`, `cp1252`).
2. **Padronização** dos nomes de colunas para **snake_case**.
3. **Parse de datas** (`order_date`, `ship_date`, quando existirem).
4. **Colunas derivadas**:
    - `total_cost = sales - profit`
    - `month_year` no formato `YYYY-MM` a partir de `order_date`.
5. **Remoção de linhas com faltantes** (`dropna()`).
6. **Gravação** do processado em `data/processed/processed.csv`.

> Dica: se o bruto tiver muitos ausentes, o `dropna()` pode reduzir bastante o dataset (intencional neste momento didático).

---

## Perguntas de negócio

- **Visão geral**
  - Como estão **vendas**, **lucro** e **custos** no período?
  - Qual a **tendência mensal** de vendas brutas e de **profit**?

- **Vendas**
  - Quais **categorias** e **subcategorias** mais vendem?
  - Como se comportam **vendas, custos e lucro** ao longo do tempo?
  - Onde estão os **maiores prejuízos** (profit negativo)?

- **Clientes & Geografia**
  - Quantos **clientes únicos** e quais **segmentos** mais compram?
  - Quais **países/estados/cidades** representam maior volume de vendas?
  - **Mapa por estados dos EUA**: quais estados vendem mais?

- **Produtos**
  - Quais **produtos** concentram a maior parte das vendas? (**Curva ABC / Pareto** com slider total e filtro por A/B/C)
  - **Top ganhos** e **maiores prejuízos** por produto.
  - **Cohort de clientes** (contagem): retenção por mês da primeira compra.

- **Dicionário de Dados**
  - Quais campos existem e como foram calculados/transformados?

---

## Como utilizar

### Versão publicada (recomendada)

O app está disponível em: **<https://ttsprint5project-hyptkiri9xe3afxgzsz3an.streamlit.app/>**

> Use os **filtros na barra lateral** para restringir período, segmentos, categorias etc. As páginas estão no menu superior (API de navegação do Streamlit 1.50).

### Executar localmente

**Pré-requisitos:**

- Python 3.10+
- `streamlit==1.50.0`, `pandas`, `numpy`, `plotly`

**Passo a passo:**  

1. Coloque o CSV bruto em `data/raw/dataset_ruido.csv`.  
2. Instale dependências:  

    ```bash
    pip install -r requirements.txt
    # ou
    pip install streamlit==1.50.0 pandas numpy plotly
    ```

3. Rode o app:

    ```bash
    streamlit run main.py
    ```

4. O app irá abrir e irá:
    - Ler data/raw/dataset_ruido.csv
    - Pré-processar e salvar data/processed/processed.csv
    - Abrir a página principal Visão Geral

### Estrutura do Projeto

```text
.  
├── data/  
│   ├── raw/  
│   │   └── dataset_ruido.csv  
│   └── processed/  
│       └── processed.csv  
├── img/  
├── notebooks/  
│   └── prototype.ipynb  
├── pages/  
│   ├── 1_main_kpis.py  
│   ├── 2_sales_kpis.py  
│   ├── 3_clients_kpis.py  
│   ├── 4_products_kpis.py  
│   └── data_dict.py  
├── utils/  
│   ├── aux_functions.py  
│   ├── bootstrap.py  
│   ├── lateral_filters.py  
│   ├── app_paths.py  
│   └── pre_process.py  
└── main.py  
```

## Próximos Passos

### 1. Tratamento de faltantes mais sofisticado

- Imputações condicionais, dropna(subset=[...]), validações e data quality checks.

### 2. Performance

- Reduzir uso de memória (dtypes), caching de agregações, pré-agregados por mês.

### 3. Novas análises

- Forecast de vendas; RFM de clientes; market basket analysis; KPIs logísticos.

### 4. Interação e UX

- Exportar CSV dos dados filtrados; bookmarks de filtros; tooltips/contexto nas páginas.

### 5. Segurança e compartilhamento

- Autenticação, controle de acesso por página/métrica, logs de uso.

### 6. Infra & DevEx

- Testes, pre-commit, lint, CI/CD, Dockerfile, variáveis de ambiente.

### 7. Catálogo de dados

- Ampliar o Dicionário de Dados (exemplos, ranges, data lineage).

### 8. Internacionalização

- Suporte a múltiplos idiomas (pt/en/es) via arquivo de tradução simples.
