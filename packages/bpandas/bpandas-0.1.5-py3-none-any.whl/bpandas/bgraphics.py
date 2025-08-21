# bpandas/bgraphics.py
from __future__ import annotations

from typing import Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def blinebar(
    df: pd.DataFrame,
    x: str,
    y_bar: str,
    y_line: str,
    *,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel_left: str,
    ylabel_right: str,
    y2_is_percent: bool = True,  # formata o eixo da direita como %
    figsize: Tuple[float, float] = (10, 6),
    bar_width: float = 0.65,
    color_bar: Optional[str] = None,  # ex.: "#4C78A8"
    color_line: Optional[str] = None,  # ex.: "#F58518"
    rotate_xticks: Optional[int] = 0,
    grid: bool = True,
    savepath: Optional[str] = None,
    show: bool = True,
):
    """
    Plota gráfico combinado (barras + linha) com eixos Y duplos.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame de origem.
    x : str
        Nome da coluna categórica do eixo X (ou ordinal).
    y_bar : str
        Coluna usada nas barras (eixo Y da esquerda).
    y_line : str
        Coluna usada na linha (eixo Y da direita).
    title : str, opcional
        Título do gráfico.
    xlabel : str, opcional
        Rótulo do eixo X (se None, usa `x`).
    ylabel_left : str
        Rótulo do eixo Y esquerdo.
    ylabel_right : str
        Rótulo do eixo Y direito.
    y2_is_percent : bool
        Se True, formata o eixo da direita como porcentagem (0–100%).
    figsize : (w, h)
        Tamanho da figura em polegadas.
    bar_width : float
        Largura das barras.
    color_bar : str, opcional
        Cor das barras (hex/nomes matplotlib). Se None, usa ciclo padrão.
    color_line : str, opcional
        Cor da linha. Se None, usa ciclo padrão (diferente da barra).
    rotate_xticks : int, opcional
        Rotação dos rótulos do eixo X (ex.: 0, 30, 45, 90).
    grid : bool
        Se True, mostra grid leve no eixo esquerdo.
    savepath : str, opcional
        Caminho do arquivo para salvar (ex.: "saida.png" ou "saida.svg").
    show : bool
        Se True, chama plt.show() ao final.

    Retorna
    -------
    (fig, ax, ax2) : tuple
        A figura e os dois eixos criados.
    """
    # estilo clean e moderno (sem depender de seaborn)
    plt.style.use("seaborn-v0_8-whitegrid")  # estilo leve disponível no matplotlib

    # validações simples
    for col in (x, y_bar, y_line):
        if col not in df.columns:
            raise KeyError(f"Coluna '{col}' não encontrada no DataFrame.")

    # posições no eixo x e rótulos
    categories = df[x].astype(str).tolist()
    x_pos = np.arange(len(categories))

    # cria figura e eixos
    fig, ax = plt.subplots(figsize=figsize)
    ax2 = ax.twinx()

    # escolhe cores do ciclo padrão se não foram passadas
    if color_bar is None or color_line is None:
        # pega duas cores distintas do ciclo atual
        # (sem fixar paleta para manter compatibilidade com estilos do usuário)
        prop_cycle = plt.rcParams["axes.prop_cycle"].by_key().get("color", [])
        if not prop_cycle:
            prop_cycle = ["#4C78A8", "#F58518"]
        if color_bar is None:
            color_bar = prop_cycle[0]
        if color_line is None:
            # se só houver uma cor no ciclo, define uma alternativa
            color_line = prop_cycle[1] if len(prop_cycle) > 1 else "#F58518"

    # barras (eixo esquerdo)
    bars = ax.bar(
        x_pos,
        df[y_bar].values,
        width=bar_width,
        color=color_bar,
        alpha=0.9,
        label=y_bar,
    )

    # linha (eixo direito)
    line = ax2.plot(
        x_pos,
        df[y_line].values,
        label=y_line,
        linewidth=2.5,
        marker="o",
        markersize=6,
        alpha=0.95,
        color=color_line,
    )[0]

    # formatação dos eixos
    ax.set_xticks(x_pos, categories)
    if rotate_xticks:
        plt.setp(ax.get_xticklabels(), rotation=rotate_xticks, ha="right")

    ax.set_ylabel(ylabel_left)
    ax2.set_ylabel(ylabel_right)
    ax.set_xlabel(xlabel if xlabel is not None else x)

    if y2_is_percent:
        # assume que y_line está em 0–100
        ax2.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    # grid leve só no eixo esquerdo
    if grid:
        ax.grid(True, axis="y", linewidth=0.8, alpha=0.25)  # grade só no Y esquerdo
        ax2.grid(False)  # garante sem grade no direito
    else:
        ax.grid(False, which="both")  # desliga tudo no esquerdo
        ax2.grid(False, which="both")  # desliga tudo no direito

    # remove spines superiores para um look mais clean
    for spine in ("top",):
        ax.spines[spine].set_visible(False)
        ax2.spines[spine].set_visible(False)

    # título
    if title:
        ax.set_title(title, loc="left", pad=12, fontsize=13, fontweight="bold")

    # legenda combinada (barras + linha)
    handles = [bars, line]
    labels = [y_bar, y_line]
    ax.legend(handles, labels, loc="upper left", frameon=False)

    # margens e layout
    ax.margins(x=0.02)
    fig.tight_layout()

    # salvar (se pedido)
    if savepath:
        fig.savefig(savepath, dpi=160, bbox_inches="tight")

    if show:
        plt.show()

    return fig, ax, ax2
