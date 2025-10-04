# pages/data_dict.py — Dicionário de Dados (markdown no Streamlit)
# ---------------------------------------------------------------
# Esta página documenta o dataset usado no dashboard:
# - Convenções de nomenclatura
# - Campos disponíveis (nome, tipo esperado, descrição)
# - Regras de pré-processamento e fórmulas

import streamlit as st

def main():
    st.title("📚 Dicionário de Dados")

    # ------------------------------------------------------------
    # Visão geral
    # ------------------------------------------------------------
    st.markdown(
        """
**Fonte**: arquivo processado gerado a partir de `data/raw/dataset_ruido.csv`  
**Pipeline**: executado pelo `main.py` → `utils/pre_process.py`

### Convenções
- **snake_case**: todos os nomes de colunas em minúsculas com `_` (ex.: `order_date`, `total_cost`).
- **Datas**: quando presentes, `order_date` e `ship_date` são convertidas para tipo data.
- **Período**: `month_year` no formato `YYYY-MM`.
- **Faltantes**: linhas com qualquer dado faltante são **removidas** no pré-processamento.

---
"""
    )

    # ------------------------------------------------------------
    # Campos principais (tabela em Markdown)
    # ------------------------------------------------------------
    st.markdown(
        """
### Campos principais

| Coluna           | Tipo esperado | Descrição                                                                 |
|------------------|---------------|----------------------------------------------------------------------------|
| `order_date`     | data          | Data do pedido.                                                            |
| `ship_date`      | data          | Data de envio.                                                             |
| `month_year`     | texto         | Mês/Ano derivado de `order_date` no formato `YYYY-MM`.                    |
| `sales`          | numérico      | Valor de venda **líquida** registrada na linha.                            |
| `profit`         | numérico      | Lucro da linha (pode ser negativo).                                       |
| `total_cost`     | numérico      | **Custo total** da linha: `total_cost = sales - profit`.                  |
| `quantity`       | numérico      | Quantidade vendida.                                                        |
| `discount`       | numérico      | Desconto aplicado (se existir no bruto; não é criado no pipeline).        |
| `segment`        | texto         | Segmento do cliente (ex.: Consumer, Corporate, Home Office).              |
| `country`        | texto         | País.                                                                      |
| `state`          | texto         | Estado/Província.                                                          |
| `city`           | texto         | Cidade.                                                                    |
| `postal_code`    | texto         | CEP/Código postal.                                                         |
| `region`         | texto         | Região (ex.: West, East etc., se existir).                                |
| `category`       | texto         | Categoria do produto.                                                      |
| `sub_category`   | texto         | Subcategoria do produto.                                                   |
| `product_name`   | texto         | Nome do produto.                                                           |
| `customer_id`    | texto         | Identificador do cliente (se existir).                                     |
| `order_id`       | texto         | Identificador do pedido (se existir).                                      |

> Observação: algumas colunas dependem do arquivo bruto original. Se um campo **não** existir no CSV de origem, ele pode não aparecer no processado.
"""
    )

    # ------------------------------------------------------------
    # Fórmulas e regras
    # ------------------------------------------------------------
    st.markdown(
        """
### Fórmulas e regras de pré-processamento

- **Custo total**:  
  `total_cost = sales - profit`  
  Se `profit` for negativo, `total_cost` fica **maior** que `sales` (venda com prejuízo).

- **Período (mês/ano)**:  
  `month_year = to_period(order_date, 'M') → 'YYYY-MM'`

- **Nomes de colunas**:  
  Todos os nomes são convertidos para **snake_case** (minúsculas, `_` como separador).  
  Exemplos: `"Order Date" → "order_date"`, `"Sub-Category" → "sub_category"`.

- **Tratamento de faltantes**:  
  Após as transformações, é aplicado `dropna()` → **remove linhas** que contenham qualquer `NaN`.  
  *Impacto*: conjuntos com muitos valores ausentes podem reduzir de tamanho.
"""
    )

    # ------------------------------------------------------------
    # Boas práticas para análise
    # ------------------------------------------------------------
    st.markdown(
        """
### Boas práticas ao usar o dataset

- **Agregações por tempo**: utilize `month_year` para gráficos mensais; para granularidade diária, use `order_date`.
- **Comparações de rentabilidade**: compare `profit` e `total_cost` por `category` / `sub_category` / `segment`.
- **Filtros**: use a barra lateral para restringir período, categorias e faixas numéricas (sales, profit, total_cost).
- **Outliers**: lucros negativos são esperados em alguns casos (descontos altos, devoluções, fretes); investigue o contexto.
"""
    )

    # ------------------------------------------------------------
    # Como atualizar este dicionário
    # ------------------------------------------------------------
    st.markdown(
        """
### Como atualizar este dicionário

Se você incluir novos campos no pré-processamento (`utils/pre_process.py`),  
**documente-os aqui** adicionando novas linhas na tabela de “Campos principais” e, se necessário, novas fórmulas na seção acima.
"""
    )

# Executa a página quando chamada via st.Page/st.navigation ou diretamente
main()
