# 📦 bpandas

**bpandas** é uma coleção de helpers para deixar o uso do **pandas** mais simples e rápido.  
Comece em segundos com **tabela de frequências** e **gráfico barras + linha com dois eixos Y** — bonito e profissional.

<p align="left">
  <a href="https://pypi.org/project/bpandas/"><img alt="PyPI" src="https://img.shields.io/pypi/v/bpandas.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.13-3776AB">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green.svg"></a>
</p>

---

## ✨ O que vem pronto

- `bfrequencies(df, column, ...)` → distribuição de **frequências** (absoluta, relativa e acumuladas).
- `blinebar(df, x, y_bar, y_line, ...)` → **barras + linha** com **dois eixos Y**, layout clean (matplotlib puro).

> Ideal para relatórios rápidos, EDA e material didático.

---

## 📦 Instalação

PyPI (após publicar):
```bash
pip install bpandas

Dev local (raiz do projeto):

pip install -e .


Requisitos: Python 3.13. Para versões exatas de libs, veja pyproject.toml.

🚀 Comece em 30 segundos
import pandas as pd
import bpandas as bp

# Exemplo simples
df = pd.DataFrame({"sexo": ["M","F","M","M","F", None]})

# 1) Frequências
freq = bp.bfrequencies(
    df, "sexo",
    include_na=True,       # inclui ausentes
    sort_by="index",       # "index" ou "count"
    ascending=True,
    percent=True,          # True = 0–100%; False = 0–1
    decimals=2
)
print(freq.head())
# -> colunas: value, frequency, relative_frequency, cumulative_frequency, cumulative_relative_frequency

# 2) Gráfico bonito: barras (freq absoluta) + linha (freq relativa acumulada)
bp.blinebar(
    freq,
    x="value",
    y_bar="frequency",
    y_line="cumulative_relative_frequency",
    title="Distribuição por Sexo",
    xlabel="Categorias",
    ylabel_left="Frequência Absoluta",
    ylabel_right="Frequência Acumulada (%)",
    y2_is_percent=True,    # formata eixo direito como %
    rotate_xticks=0,       # 0, 30, 45, 90...
    # savepath="saida.png" # opcional: salva a figura
)

🧠 API (resumo)
bfrequencies(df, column_name, *, include_na=True, sort_by="index", ascending=True, percent=True, decimals=2) -> pd.DataFrame

Entrada: df (DataFrame), column_name (str).

Parâmetros úteis:

include_na: inclui/exclui ausentes (NaN/None).

sort_by: "index" (rótulo) ou "count" (frequência).

percent: True → 0–100; False → 0–1.

decimals: casas decimais para a relativa.

Saída: DataFrame com:

value, frequency, relative_frequency,
cumulative_frequency, cumulative_relative_frequency.

blinebar(df, x, y_bar, y_line, *, title=None, xlabel=None, ylabel_left="Frequência Absoluta", ylabel_right="Frequência Acumulada (%)", y2_is_percent=True, figsize=(10,6), bar_width=0.65, color_bar=None, color_line=None, rotate_xticks=0, grid=True, savepath=None, show=True) -> (fig, ax, ax2)

Gráfico combinado (barras + linha) com 2 eixos Y.

Usa matplotlib (sem seaborn), com estilo clean e cores automáticas.

y2_is_percent=True formata o eixo direito como % (assumindo 0–100).

Retorna a fig e os axes para customizações extras.

🧪 Testes

Rodar toda a suíte:

python -m pytest -q

🛠 Roadmap (curto)

bsummary(df) — resumo rápido (shape, tipos, nulos, head).

bgroup(df, by, agg) — agrupamentos mais fáceis.

bexport(df, path) — salvar CSV/Excel/Parquet sem dor.

Sugestões são bem-vindas! Abra uma issue 👇
https://github.com/davidcloss/bpandas/issues

📄 Licença

MIT — veja LICENSE
.


se quiser, eu já **adiciono um bloco “Changelog”** no final e monto um `CHANGELOG.md` separado com as entradas dos releases que você fez (incluindo a adição do `bgraphics`).
::contentReference[oaicite:0]{index=0}
